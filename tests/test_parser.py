import pytest
from unittest.mock import patch
from app.cmd_parser import CommandParser

# We use @patch to mock os.path.isfile so we don't need real video files to test logic
@patch('app.cmd_parser.os.path.isfile')
def test_extract_audio_logic(mock_isfile):
    mock_isfile.return_value = True # Pretend file exists
    
    # 1. Test basic extraction
    parser = CommandParser("Extract audio as mp3", "test_video.mp4")
    args, output = parser.parse()
    
    assert output == "extracted_audio.mp3"
    assert "-vn" in args
    assert "libmp3lame" in args

@patch('app.cmd_parser.os.path.isfile')
def test_convert_video_logic(mock_isfile):
    mock_isfile.return_value = True
    
    # 2. Test conversion
    parser = CommandParser("Convert to mkv", "my_movie.mp4")
    args, output = parser.parse()
    
    assert output == "my_movie_converted.mkv"
    assert "-c" in args
    assert "copy" in args

@patch('app.cmd_parser.os.path.isfile')
def test_trim_logic(mock_isfile):
    mock_isfile.return_value = True
    
    # 3. Test trimming
    parser = CommandParser("Trim from 00:00:10 to 00:00:20", "video.mp4")
    args, output = parser.parse()
    
    assert "-ss" in args
    assert "00:00:10" in args
    assert "-to" in args
    assert "00:00:20" in args

@patch('app.cmd_parser.os.path.isfile')
def test_trim_first_n_seconds(mock_isfile):
    mock_isfile.return_value = True

    # 4. Test "First 10 seconds" logic
    parser = CommandParser("Trim first 10 sec", "video.mp4")
    args, output = parser.parse()

    assert "-ss" in args
    assert "00:00:00" in args
    assert "-t" in args
    assert "10" in args # Assuming logic extracts '10'

def test_missing_input():
    # 5. Test Error Handling (No mock needed here as it fails before file check)
    with pytest.raises(ValueError, match="Command text is required"):
        CommandParser("", "video.mp4")