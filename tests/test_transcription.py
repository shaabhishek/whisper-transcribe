"""Tests for the transcription module."""

import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

from speech_transcriber.transcription import Transcriber
from speech_transcriber.transcription_config import TranscriptionConfig
from speech_transcriber.utils import Logger

# Disable logs during tests
Logger.set_enabled(False)


class TestTranscription(unittest.TestCase):
  """Test cases for the transcription module."""

  def setUp(self):
    """Set up test fixtures."""
    # Create a mock configuration
    self.config = MagicMock(spec=TranscriptionConfig)
    self.config.transcription_service = 'openai'
    self.config.openai_api_key = 'test_openai_key'
    self.config.gemini_api_key = 'test_gemini_key'
    self.config.whisper_model = 'whisper-1'
    self.config.gemini_model = 'gemini-pro-vision'
    self.config.language = 'en'

    # Create a mock transcriber
    self.mock_transcriber = MagicMock()
    self.mock_transcriber.transcribe.return_value = 'Test transcription'

    # Create a transcription service with the mock transcriber
    with patch('speech_transcriber.transcription.OpenAITranscriber') as mock_openai:
      mock_openai.return_value = self.mock_transcriber
      self.transcription_service = Transcriber(config=self.config)

  @patch('os.path.exists')
  @patch('os.path.getsize')
  def test_transcribe_success(self, mock_getsize, mock_exists):
    """Test successful transcription."""
    # Set up mocks
    mock_exists.return_value = True
    mock_getsize.return_value = 1024 * 1024  # 1MB file

    # Mock the file info
    with patch.object(
      TranscriptionConfig,
      'get_file_info',
      return_value=(1024 * 1024, 'audio/wav', '.wav'),
    ):
      # Call the transcribe method
      result = self.transcription_service.transcribe('test.wav')

      # Verify the result
      self.assertEqual(result, 'Test transcription')
      self.mock_transcriber.transcribe.assert_called_once_with('test.wav')

  @patch('os.path.exists')
  def test_transcribe_file_not_found(self, mock_exists):
    """Test transcription with a non-existent file."""
    # Set up mocks
    mock_exists.return_value = False

    # Mock the file info
    with patch.object(TranscriptionConfig, 'get_file_info', return_value=None):
      # Call the transcribe method
      result = self.transcription_service.transcribe('nonexistent.wav')

      # Verify the result
      self.assertIsNone(result)
      self.mock_transcriber.transcribe.assert_not_called()

  @patch('os.path.exists')
  @patch('os.path.getsize')
  def test_transcribe_api_error(self, mock_getsize, mock_exists):
    """Test transcription with an API error."""
    # Set up mocks
    mock_exists.return_value = True
    mock_getsize.return_value = 1024 * 1024  # 1MB file
    self.mock_transcriber.transcribe.side_effect = Exception('API Error')

    # Mock the file info
    with patch.object(
      TranscriptionConfig,
      'get_file_info',
      return_value=(1024 * 1024, 'audio/wav', '.wav'),
    ):
      # Call the transcribe method
      result = self.transcription_service.transcribe('test.wav')

      # Verify the result
      self.assertIsNone(result)
      self.mock_transcriber.transcribe.assert_called_once_with('test.wav')

  @patch('os.path.exists')
  @patch('os.path.getsize')
  def test_exceeds_size_limit_gemini(self, mock_getsize, mock_exists):
    """Test file size limit detection for Gemini."""
    # Set up Gemini service
    self.transcription_service.config.transcription_service = 'gemini'

    # Test with a file that exceeds the limit
    self.assertTrue(self.transcription_service._exceeds_size_limit(20))

    # Test with a file under the limit
    self.assertFalse(self.transcription_service._exceeds_size_limit(18))

  @patch('os.path.exists')
  @patch('os.path.getsize')
  def test_exceeds_size_limit_openai(self, mock_getsize, mock_exists):
    """Test file size limit detection for OpenAI."""
    # Set up OpenAI service
    self.transcription_service.config.transcription_service = 'openai'

    # Test with a file that exceeds the limit
    self.assertTrue(self.transcription_service._exceeds_size_limit(25))

    # Test with a file under the limit
    self.assertFalse(self.transcription_service._exceeds_size_limit(23))

  @patch('os.path.exists')
  @patch('os.path.getsize')
  @patch('speech_transcriber.audio_compression.AudioCompressor')
  def test_compress_audio_file_success(
    self, mock_compressor_class, mock_getsize, mock_exists
  ):
    """Test successful audio compression."""
    # Set up mocks
    mock_exists.return_value = True
    mock_getsize.side_effect = [25 * 1024 * 1024, 15 * 1024 * 1024]  # 25MB -> 15MB

    # Mock the compressor instance
    mock_compressor = MagicMock()
    mock_compressor.compress_audio.return_value = '/tmp/compressed.mp3'
    mock_compressor_class.return_value = mock_compressor

    # Override calls to the actual ffmpeg command
    with patch('subprocess.run'):
      # Call the compression method
      result = self.transcription_service._compress_audio_file('test.wav', 25)

      # Verify the result
      self.assertEqual(result, '/tmp/compressed.mp3')
      mock_compressor.compress_audio.assert_called_once_with('test.wav', max_size_mb=24)

  @patch('os.path.exists')
  @patch('os.path.getsize')
  @patch('speech_transcriber.audio_compression.AudioCompressor')
  def test_compress_audio_file_failure(
    self, mock_compressor_class, mock_getsize, mock_exists
  ):
    """Test failed audio compression."""
    # Set up mocks
    mock_exists.return_value = True
    mock_getsize.return_value = 25 * 1024 * 1024  # 25MB

    # Mock the compressor instance
    mock_compressor = MagicMock()
    mock_compressor.compress_audio.return_value = None  # Compression failed
    mock_compressor_class.return_value = mock_compressor

    # Override calls to the actual ffmpeg command
    with patch('subprocess.run'):
      # Call the compression method
      result = self.transcription_service._compress_audio_file('test.wav', 25)

      # Verify the result - should return original file on failure
      self.assertEqual(result, 'test.wav')
      mock_compressor.compress_audio.assert_called_once_with('test.wav', max_size_mb=24)

  @patch('os.path.exists')
  @patch('os.path.getsize')
  @patch('speech_transcriber.audio_compression.AudioCompressor')
  def test_handle_file_size_compression_needed(
    self, mock_compressor_class, mock_getsize, mock_exists
  ):
    """Test file size handling when compression is needed."""
    # Set up mocks
    mock_exists.return_value = True
    mock_getsize.side_effect = [25 * 1024 * 1024, 15 * 1024 * 1024]  # 25MB -> 15MB

    # Mock the compressor
    mock_compressor = MagicMock()
    mock_compressor.compress_audio.return_value = '/tmp/compressed.mp3'
    mock_compressor_class.return_value = mock_compressor

    # Override calls to the actual ffmpeg command
    with patch('subprocess.run'):
      # Mock the file info
      file_info = (25 * 1024 * 1024, 'audio/wav', '.wav')

      # Call the method
      result = self.transcription_service._handle_file_size('test.wav', file_info)

      # Verify the result - should return compressed file
      self.assertEqual(result, '/tmp/compressed.mp3')
      mock_compressor.compress_audio.assert_called_once()

  @patch('os.path.exists')
  @patch('os.path.getsize')
  @patch('speech_transcriber.audio_compression.AudioCompressor')
  def test_handle_file_size_no_compression_needed(
    self, mock_compressor_class, mock_getsize, mock_exists
  ):
    """Test file size handling when no compression is needed."""
    # Set up mocks
    mock_exists.return_value = True
    mock_getsize.return_value = 10 * 1024 * 1024  # 10MB

    # Mock the file info
    file_info = (10 * 1024 * 1024, 'audio/wav', '.wav')

    # Call the method
    result = self.transcription_service._handle_file_size('test.wav', file_info)

    # Verify the result - should return original file
    self.assertEqual(result, 'test.wav')
    mock_compressor_class.assert_not_called()

  @patch('os.path.exists')
  @patch('os.unlink')
  def test_cleanup_temp_file(self, mock_unlink, mock_exists):
    """Test temporary file cleanup."""
    # Set up mocks
    mock_exists.return_value = True

    # Call the cleanup method
    self.transcription_service._cleanup_temp_file('/tmp/temp.mp3')

    # Verify the file was deleted
    mock_unlink.assert_called_once_with('/tmp/temp.mp3')

  @patch('os.path.exists')
  @patch('os.unlink')
  def test_cleanup_temp_file_error(self, mock_unlink, mock_exists):
    """Test temporary file cleanup with an error."""
    # Set up mocks
    mock_exists.return_value = True
    mock_unlink.side_effect = Exception('Deletion error')

    # Call the cleanup method - should not raise an exception
    self.transcription_service._cleanup_temp_file('/tmp/temp.mp3')

    # Verify the file deletion was attempted
    mock_unlink.assert_called_once_with('/tmp/temp.mp3')


if __name__ == '__main__':
  unittest.main()
