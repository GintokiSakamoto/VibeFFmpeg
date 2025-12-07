import pytest
from unittest.mock import patch
from vibeffmpeg.app.cmd_parser import CommandParser

@patch('vibeffmpeg.app.cmd_parser.os.path.isfile')
def test_fuzzy_matching_typos(mock_isfile):
    """Can it handle 'xtract' instead of 'extract'?"""
    mock_isfile.return_value = True
    
    # User makes a typo: "plz xtract audio"
    # This tests if the fuzzy logic correctly identifies "extract audio"
    parser = CommandParser("plz xtract audio", "vid.mp4")
    args, output = parser.parse()
    
    assert "extracted_audio.mp3" in output
    assert "-vn" in args

@patch('vibeffmpeg.app.cmd_parser.os.path.isfile')
def test_fuzzy_matching_synonyms(mock_isfile):
    """Can it handle 'turn into' instead of 'convert'?"""
    mock_isfile.return_value = True
    
    # User uses synonym: "turn into mkv"
    parser = CommandParser("turn into mkv", "vid.mp4")
    args, output = parser.parse()
    
    assert "mkv" in output
    assert "-c" in args

@patch('vibeffmpeg.app.cmd_parser.os.path.isfile')
def test_trim_logic_fix(mock_isfile):
    """Verifies the fix for -t vs -to"""
    mock_isfile.return_value = True
    
    # Test "first 10 seconds" specifically
    parser = CommandParser("trim first 10 sec", "vid.mp4")
    args, output = parser.parse()
    
    assert "-ss" in args
    assert "-t" in args
    assert "10" in args
    assert "-to" not in args # Ensure we didn't use the wrong flag

@patch('vibeffmpeg.app.cmd_parser.os.path.isfile')
def test_range_trimming(mock_isfile):
    """Verifies standard range trimming works with fuzzy parser"""
    mock_isfile.return_value = True
    
    # "cut video from X to Y"
    parser = CommandParser("cut video from 00:00:10 to 00:00:20", "vid.mp4")
    args, output = parser.parse()
    
    assert "-ss" in args
    assert "00:00:10" in args
    assert "-to" in args
    assert "00:00:20" in args

@patch('vibeffmpeg.app.cmd_parser.os.path.isfile')
def test_low_confidence_failure(mock_isfile):
    """If I say gibberish, it should fail safely"""
    mock_isfile.return_value = True
    
    # "make me a sandwich" looks nothing like "extract" or "trim"
    parser = CommandParser("make me a sandwich", "vid.mp4")
    
    # Expect a ValueError because confidence will be low
    with pytest.raises(ValueError, match="Could not understand command"):
        parser.parse()

@patch('vibeffmpeg.app.cmd_parser.os.path.isfile')
def test_gif_creation_defaults(mock_isfile):
    """Test 'make gif' defaults to first 5 seconds"""
    mock_isfile.return_value = True
    
    parser = CommandParser("make gif", "funny.mp4")
    args, output = parser.parse()
    
    assert output == "funny.gif"
    assert "-t" in args
    assert "5" in args      # The default duration
    assert "-ss" in args
    assert "00:00:00" in args

@patch('vibeffmpeg.app.cmd_parser.os.path.isfile')
def test_gif_creation_range(mock_isfile):
    """Test 'make gif from X to Y'"""
    mock_isfile.return_value = True
    
    parser = CommandParser("make gif from 00:00:10 to 00:00:15", "funny.mp4")
    args, output = parser.parse()
    
    assert "-ss" in args
    assert "00:00:10" in args
    assert "-to" in args
    assert "00:00:15" in args
    assert "palettegen" in args[args.index("-vf") + 1] # Check if complex filters are present

@patch('vibeffmpeg.app.cmd_parser.os.path.isfile')
def test_gif_creation_first_n(mock_isfile):
    """Test 'make gif first 3 seconds'"""
    mock_isfile.return_value = True
    
    parser = CommandParser("create gif first 3 sec", "funny.mp4")
    args, output = parser.parse()
    
    assert "-t" in args
    assert "3" in args

@patch('vibeffmpeg.app.cmd_parser.os.path.isfile')
def test_resize_video(mock_isfile):
    """Test resizing to 720p"""
    mock_isfile.return_value = True
    
    parser = CommandParser("resize video to 720p", "movie.mkv")
    args, output = parser.parse()
    
    assert "movie_resized.mp4" in output
    assert "-vf" in args
    assert "scale=-2:720" in args
    assert "-crf" in args
    assert "23" in args # Default quality if 'compress' not mentioned

@patch('vibeffmpeg.app.cmd_parser.os.path.isfile')
def test_compress_video(mock_isfile):
    """Test 'compress' keyword triggers lower quality (CRF 28)"""
    mock_isfile.return_value = True
    
    parser = CommandParser("compress this video", "big_file.mp4")
    args, output = parser.parse()
    
    assert "big_file_compressed.mp4" in output
    assert "-crf" in args
    assert "28" in args # The 'compressed' quality value

@patch('vibeffmpeg.app.cmd_parser.os.path.isfile')
def test_compress_and_resize(mock_isfile):
    """Test doing both: 'Compress to 480p'"""
    mock_isfile.return_value = True
    
    parser = CommandParser("compress to 480p", "movie.mp4")
    args, output = parser.parse()
    
    assert "-vf" in args
    assert "scale=-2:480" in args # Resizing
    assert "28" in args           # AND Compressing

@patch('vibeffmpeg.app.cmd_parser.os.path.isfile')
def test_mute_video(mock_isfile):
    mock_isfile.return_value = True
    parser = CommandParser("mute this video", "noisy.mp4")
    args, output = parser.parse()
    
    assert "noisy_muted.mp4" in output
    assert "-an" in args
    assert "-c:v" in args # Ensure video is copied, not re-encoded (speed!)

@patch('vibeffmpeg.app.cmd_parser.os.path.isfile')
def test_boost_volume(mock_isfile):
    mock_isfile.return_value = True
    parser = CommandParser("make audio louder", "quiet.mp4")
    args, output = parser.parse()
    
    assert "quiet_boosted.mp4" in output
    assert "-filter:a" in args
    assert "volume=1.5" in args

@patch('vibeffmpeg.app.cmd_parser.os.path.isfile')
def test_custom_resolution_no_stretch(mock_isfile):
    """Test 'resize to 350x500' (Default: Preserve Aspect Ratio)"""
    mock_isfile.return_value = True
    
    parser = CommandParser("resize to 350x500", "vid.mp4")
    args, output = parser.parse()
    
    assert "-vf" in args
    # Expect the safe flag
    assert "force_original_aspect_ratio=decrease" in args[args.index("-vf") + 1]

@patch('vibeffmpeg.app.cmd_parser.os.path.isfile')
def test_custom_resolution_with_stretch(mock_isfile):
    """Test 'resize to 350x500 stretch' (Explicit: Force Distortion)"""
    mock_isfile.return_value = True
    
    parser = CommandParser("resize to 350x500 stretch", "vid.mp4")
    args, output = parser.parse()
    
    assert "-vf" in args
    # Expect pure scaling
    assert "scale=350:500" in args[args.index("-vf") + 1]
    # Ensure safe flag is NOT there
    assert "force_original_aspect_ratio" not in args[args.index("-vf") + 1]