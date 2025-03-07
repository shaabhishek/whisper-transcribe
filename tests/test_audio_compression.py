"""Tests for the audio compression module."""

import os
import tempfile
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

from speech_transcriber.audio_compression import AudioCompressor


class TestAudioCompressor(unittest.TestCase):
  """Test cases for the audio compression module."""

  def setUp(self):
    """Set up test fixtures."""
    # Create a mock audio file for testing
    self.test_audio_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    self.test_audio_file.write(b'mock audio data' * 1000)  # Fake audio data
    self.test_audio_file.close()

    # File size in MB for testing
    self.file_size_mb = 0.01  # Small file for testing

    # Create the audio compressor
    self.compressor = AudioCompressor()

  def tearDown(self):
    """Clean up after tests."""
    # Remove test files
    if hasattr(self, 'test_audio_file') and self.test_audio_file:
      if os.path.exists(self.test_audio_file.name):
        os.unlink(self.test_audio_file.name)

  @patch('shutil.which')
  def test_check_ffmpeg_available_success(self, mock_which):
    """Test ffmpeg availability check when ffmpeg is installed."""
    mock_which.return_value = '/usr/bin/ffmpeg'  # Mock ffmpeg being installed

    compressor = AudioCompressor()

    self.assertTrue(compressor.ffmpeg_available)
    mock_which.assert_called_once_with('ffmpeg')

  @patch('shutil.which')
  def test_check_ffmpeg_available_failure(self, mock_which):
    """Test ffmpeg availability check when ffmpeg is not installed."""
    mock_which.return_value = None  # Mock ffmpeg not being installed

    compressor = AudioCompressor()

    self.assertFalse(compressor.ffmpeg_available)
    mock_which.assert_called_once_with('ffmpeg')

  def test_calculate_bitrate(self):
    """Test the bitrate calculation algorithm."""
    # Test with a small file
    small_file_bitrate = self.compressor._calculate_bitrate(
      self.test_audio_file.name, 19
    )
    self.assertGreaterEqual(
      small_file_bitrate, 16
    )  # Should be at least the minimum bitrate

    # Test with different target sizes
    larger_bitrate = self.compressor._calculate_bitrate(self.test_audio_file.name, 50)
    smaller_bitrate = self.compressor._calculate_bitrate(self.test_audio_file.name, 5)

    self.assertGreaterEqual(larger_bitrate, smaller_bitrate)

    # Test maximum bitrate clamping
    max_bitrate = self.compressor._calculate_bitrate(self.test_audio_file.name, 1000)
    self.assertLessEqual(max_bitrate, 128)  # Should be capped at maximum bitrate

  @patch('subprocess.run')
  def test_run_ffmpeg(self, mock_run):
    """Test the ffmpeg command execution."""
    mock_result = MagicMock()
    mock_run.return_value = mock_result

    output_file = '/tmp/test_output.mp3'
    result = self.compressor._run_ffmpeg(self.test_audio_file.name, output_file, 64)

    # Verify ffmpeg was called with correct parameters
    mock_run.assert_called_once()
    call_args = mock_run.call_args[0][0]

    self.assertEqual(call_args[0], 'ffmpeg')
    self.assertEqual(call_args[1], '-i')
    self.assertEqual(call_args[2], self.test_audio_file.name)
    self.assertEqual(call_args[3], '-b:a')
    self.assertEqual(call_args[4], '64k')
    self.assertEqual(call_args[5], '-ac')
    self.assertEqual(call_args[6], '1')  # Mono
    self.assertEqual(call_args[7], '-y')  # Overwrite
    self.assertEqual(call_args[8], output_file)

    # Verify the result is returned properly
    self.assertEqual(result, mock_result)

  @patch('subprocess.run')
  @patch('os.path.getsize')
  @patch('os.path.exists')
  def test_compress_audio_success(self, mock_exists, mock_getsize, mock_run):
    """Test successful audio compression."""
    # Set up the mocks
    self.compressor.ffmpeg_available = True
    mock_run.return_value = MagicMock()

    # Create a mock temporary file path
    temp_file_path = '/tmp/test_compressed.mp3'

    # Mock file existence checks
    mock_exists.return_value = True

    # Mock file sizes - setup both calls with concrete values
    mock_getsize.side_effect = [
      1024 * 1024,  # 1MB for input file (first call)
      512 * 1024,  # 0.5MB for output file (second call)
    ]

    # Mock the subprocess call
    def run_side_effect(*args, **kwargs):
      # When ffmpeg is called, create a mock file
      # This simulates ffmpeg creating the output file
      return MagicMock()

    mock_run.side_effect = run_side_effect

    # Mock NamedTemporaryFile to return a controlled path
    with patch('tempfile.NamedTemporaryFile') as mock_temp_file:
      # Create mock file object
      mock_file = MagicMock()
      mock_file.name = temp_file_path
      mock_temp_file.return_value = mock_file

      # Direct mocking of the internal verification to ensure success
      with (
        patch.object(os.path, 'exists', return_value=True),
        patch.object(os.path, 'getsize', return_value=512 * 1024),
      ):
        # Call the method to test
        result = self.compressor.compress_audio(self.test_audio_file.name, 19)

        # Verify the result
        self.assertEqual(result, temp_file_path)

    # Verify ffmpeg was called with the right arguments
    mock_run.assert_called_once()

  @patch('subprocess.run')
  def test_compress_audio_ffmpeg_not_available(self, mock_run):
    """Test compression when ffmpeg is not available."""
    # Set ffmpeg as not available
    self.compressor.ffmpeg_available = False

    # Call the compression method
    result = self.compressor.compress_audio(self.test_audio_file.name, 19)

    # Verify that None is returned and ffmpeg is not called
    self.assertIsNone(result)
    mock_run.assert_not_called()

  @patch('subprocess.run')
  def test_compress_audio_file_not_exists(self, mock_run):
    """Test compression when input file doesn't exist."""
    # Set ffmpeg as available
    self.compressor.ffmpeg_available = True

    # Call with a non-existent file
    result = self.compressor.compress_audio('/non/existent/file.wav', 19)

    # Verify that None is returned and ffmpeg is not called
    self.assertIsNone(result)
    mock_run.assert_not_called()

  @patch('subprocess.run')
  @patch('os.path.exists')
  def test_compress_audio_empty_output(self, mock_exists, mock_run):
    """Test compression when output file is empty or doesn't exist."""
    # Set up the mocks
    self.compressor.ffmpeg_available = True
    mock_run.return_value = MagicMock()

    # Mock the output file doesn't exist after compression
    mock_exists.side_effect = [True, False]  # Input exists, output doesn't

    # Call the compression method
    with patch('tempfile.NamedTemporaryFile') as mock_temp_file:
      mock_file = MagicMock()
      mock_file.name = '/tmp/test_compressed.mp3'
      mock_temp_file.return_value = mock_file

      result = self.compressor.compress_audio(self.test_audio_file.name, 19)

      # Verify that None is returned for failed compression
      self.assertIsNone(result)

  @patch('subprocess.run')
  @patch('os.path.exists')
  def test_compress_audio_exception_handling(self, mock_exists, mock_run):
    """Test exception handling during compression."""
    # Set up the mocks
    self.compressor.ffmpeg_available = True
    mock_run.side_effect = Exception('Test exception')

    # Mock file existence checks - input file exists, output doesn't
    mock_exists.side_effect = lambda path: path == self.test_audio_file.name

    # Call the compression method
    with patch('tempfile.NamedTemporaryFile') as mock_temp_file:
      mock_file = MagicMock()
      mock_file.name = '/tmp/test_compressed.mp3'
      mock_temp_file.return_value = mock_file

      # Create a patch for the error handler to verify it's called
      with patch.object(self.compressor, '_handle_compression_error') as mock_handler:
        result = self.compressor.compress_audio(self.test_audio_file.name, 19)

        # Verify error handler was called
        mock_handler.assert_called_once()

        # Verify that None is returned for failed compression
        self.assertIsNone(result)


if __name__ == '__main__':
  unittest.main()
