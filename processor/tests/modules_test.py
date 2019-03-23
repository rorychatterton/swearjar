import src.modules as mdls
import pytest


def test_valid_filetype():
    assert (mdls.get_and_validate_filetype("https://s3-us-east-1.amazonaws.com/examplebucket/example.mp4") is "mp4")
    assert (mdls.get_and_validate_filetype("https://s3-us-east-1.amazonaws.com/examplebucket/example.mp3") is "mp3")
    assert (mdls.get_and_validate_filetype("https://s3-us-east-1.amazonaws.com/examplebucket/example.flac") is "flac")
    assert (mdls.get_and_validate_filetype("https://s3-us-east-1.amazonaws.com/examplebucket/example.wav") is "wav")

def test_invalid_filetype():
    with pytest.raises(Exception):
        mdls.get_and_validate_filetype("https://s3-us-east-1.amazonaws.com/examplebucket/example.mp8")