import src.swearjar as swearjar
import pytest
import os
import json
import pprint

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

def test_valid_file_type():
    assert (swearjar.get_and_validate_filetype("https://s3-us-east-1.amazonaws.com/examplebucket/example.mp4") is "mp4")
    assert (swearjar.get_and_validate_filetype("https://s3-us-east-1.amazonaws.com/examplebucket/example.mp3") is "mp3")
    assert (swearjar.get_and_validate_filetype("https://s3-us-east-1.amazonaws.com/examplebucket/example.flac") is "flac")
    assert (swearjar.get_and_validate_filetype("https://s3-us-east-1.amazonaws.com/examplebucket/example.wav") is "wav")


def test_invalid_file_type():
    with pytest.raises(Exception):
        swearjar.get_and_validate_filetype("https://s3-us-east-1.amazonaws.com/examplebucket/example.mp8")


def test_upload_file_to_s3():
    file_url = "https://upload.wikimedia.org/wikipedia/commons/8/8e/Nubian_Goat_Image_002.jpg"
    swearjar.upload_file_to_s3(url=file_url, key="test/goat_test.jpg")


def test_get_processed_files_from_s3():
    assert("test/goat_test.jpg" in swearjar.get_filelist_from_s3("test/"))


def test_fail_processed_files_from_s3():
    assert("NonExistantFile" not in swearjar.get_filelist_from_s3("fail/"))


#def test_process_podcasts():
#    swearjar.process_podcasts()


def test_move_transcription_output():
    swearjar.move_transcription_output("podcast-swearjar-dev-podcast-e04")

def test_profanity_processor():
    with open(os.path.join(__location__, 'files/example_transcript.json')) as file:
        transcript = swearjar.profanity_processor(json.load(file))

    swearjar.upload_profanity_to_aws(processed_transcript=transcript, podcast_name="podcast-e12")
