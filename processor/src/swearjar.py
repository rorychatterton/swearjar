import feedparser
import os
import boto3
import tempfile
import urllib.request
import logging as LOGGER
import json

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

# AWS Clients
PRE_PROCESSED_KEY = "raw/"
POST_PROCESSED_KEY = "processed/"
SCRATCH_LOCATION_KEY = "scratch/"
TRANSCRIBE_CLIENT = boto3.client('transcribe')
S3_CLIENT = boto3.client('s3')
ENVIRONMENT_VARIABLES = ["S3_BUCKET", "REGION", "TRANSCRIPTION_JOB_PREFIX", "PODCAST_NAME", "PODCAST_FEED"]


def process_podcasts():
    LOGGER.info("Processing Podcasts from RSS Feed")
    [trigger_transcription(podcast) for podcast in get_unprocessed_podcasts()]


def move_transcription_output(transcription_job_name):
    s3_key = PRE_PROCESSED_KEY + transcription_job_name[len(os.environ["TRANSCRIPTION_JOB_PREFIX"]):] + ".json"
    LOGGER.info("Uploading transcription output to: '" + s3_key + "'")

    job = TRANSCRIBE_CLIENT.get_transcription_job(TranscriptionJobName=transcription_job_name)
    if job["TranscriptionJob"]["TranscriptionJobStatus"] == "COMPLETED":
        upload_file_to_s3(
            url=job["TranscriptionJob"]["Transcript"]["TranscriptFileUri"],
            key=s3_key
        )

def process_all_podcasts():

    for file_key in get_filelist_from_s3():
        obj = boto3.resource('s3').Object(os.environ["S3_BUCKET"], file_key)

        boto3.resource('s3').Object(
            os.environ["S3_BUCKET"],
            POST_PROCESSED_KEY + file_key[len(PRE_PROCESSED_KEY):] # Change Key to correct target
        ).put(
            Body=json.dumps(profanity_processor(json.load(obj.get()['Body'].read())))
        )


def profanity_processor(transcript):

    LOGGER.info("Processing Profanities")

    with open(os.path.join(__location__, 'swearwords.json')) as file:
        profanity_dictionary = {word: 0 for word in json.load(file)}

        for word in transcript["results"]["transcripts"][0]["transcript"].split(" "):
            if word in profanity_dictionary.keys():
                profanity_dictionary[word] = profanity_dictionary[word] + 1

    # Strip any swearwords that aren't instantiated
    return {word: profanity_dictionary[word] for word in profanity_dictionary if profanity_dictionary[word] > 0}




def trigger_transcription(podcast):
    upload_file_to_s3(url=podcast["url"], key=podcast["s3_key"])

    s3_url = "https://s3-" + os.environ["REGION"] + ".amazonaws.com/" + os.environ["S3_BUCKET"] + "/" + podcast["s3_key"]
    transcription_job_name = os.environ["TRANSCRIPTION_JOB_PREFIX"] + podcast["name"]

    LOGGER.info("Triggering transcription Job: " + transcription_job_name)
    return TRANSCRIBE_CLIENT.start_transcription_job(
        TranscriptionJobName=transcription_job_name,
        LanguageCode="en-AU",
        MediaFormat=get_and_validate_filetype(s3_url),
        Media={'MediaFileUri': s3_url}
    )


def get_podcast_name(podcast):
    return podcast.media_content[0]['url'].split("/")[-1].split(".")[0]


def get_podcast_s3_key(podcast):
    return SCRATCH_LOCATION_KEY + podcast.media_content[0]['url'].split("/")[-1]


def get_unprocessed_podcasts():
    # Searches the RSS feed for latest podcasts, and uploads them to S3 for Processing
    return [
        {
            "name": get_podcast_name(podcast),
            "s3_key": get_podcast_s3_key(podcast),
            "url": podcast.media_content[0]['url']
        }
        for podcast in feedparser.parse(os.environ["PODCAST_FEED"]).entries
        if PRE_PROCESSED_KEY + get_podcast_name(podcast) + ".json"
           not in get_filelist_from_s3(PRE_PROCESSED_KEY)
    ]


def check_environment_variables(environment_variables):
    missing_variables = []
    for variable in environment_variables:
        if variable not in os.environ:
            missing_variables.append(variable)

    if len(missing_variables) > 0:
        raise LookupError("The following environment variables have not been set: '" +
                          ', '.join(missing_variables) + "'")


def get_and_validate_filetype(s3_file_location):
    for file_type in ['mp3', 'mp4', 'wav', 'flac']:
        if s3_file_location.endswith(file_type):
            return file_type

    raise Exception("InvalidFileType")


def get_filelist_from_s3(prefix):

    response = S3_CLIENT.list_objects_v2(
        Bucket=os.environ["S3_BUCKET"],
        Prefix=prefix
    )

    if response["KeyCount"] == 0:
        return []

    return [file["Key"] for file in response["Contents"]]


def upload_file_to_s3(url, key):

    LOGGER.info("Uploading file to S3: " + url)
    with tempfile.NamedTemporaryFile() as temporary_file:
        urllib.request.urlretrieve(url, temporary_file.name)
        return S3_CLIENT.upload_file(temporary_file.name, os.environ["S3_BUCKET"], key)


check_environment_variables(ENVIRONMENT_VARIABLES)

