# Upload file to S3


def get_and_validate_filetype(s3_file_location):
    valid_filetypes = ['mp3', 'mp4', 'wav', 'flac']

    for file_type in valid_filetypes:
        if s3_file_location.endswith(file_type):
            return file_type

    raise Exception("InvalidFileType")


# Process File
def process_file(s3_file_location, client):


    object_key = 'mp3' | 'mp4' | 'wav' | 'flac'

    client.start_transcription_job(
        TranscriptionJobName="swearjar-" + podcast_id,
        LanguageCode="en-AU",
        MediaFormat="",
        Media={
            'MediaFileUri': 'string'
        },
        OutputBucketName='string',
    )


# Upload File to DynamoDB

# Merge File Contents Together