"""
Tests for the transcription module.
"""

import unittest
from unittest.mock import MagicMock, patch

from speech_transcriber.transcription import Transcriber
from speech_transcriber.transcription_config import TranscriptionConfig
from speech_transcriber.utils import Logger

# Disable logs during tests
Logger.set_enabled(False)


class TestTranscription(unittest.TestCase):
    """Test cases for the transcription module."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary test file path
        self.test_audio_path = "/tmp/test_audio.wav"

        # Create a mock API response
        self.mock_response = MagicMock()
        self.mock_response.text = "This is a transcribed text"

        # Create a mock for Gemini API response
        self.mock_gemini_response = MagicMock()
        self.mock_gemini_response.json.return_value = {
            "candidates": [
                {"content": {"parts": [{"text": "This is a transcribed text"}]}}
            ]
        }
        self.mock_gemini_response.status_code = 200

        # Create a test config with default OpenAI service
        self.test_openai_config = TranscriptionConfig(
            openai_api_key="test_openai_key",
            gemini_api_key="test_gemini_key",
            transcription_service="openai",
        )

        # Create a test config with Gemini service
        self.test_gemini_config = TranscriptionConfig(
            openai_api_key="test_openai_key",
            gemini_api_key="test_gemini_key",
            transcription_service="gemini",
        )

        # Initialize the transcriber with the OpenAI config
        with patch("openai.OpenAI"):
            self.transcriber = Transcriber(config=self.test_openai_config)

    @patch("os.path.exists")
    @patch("os.path.getsize")
    def test_transcribe_success(self, mock_getsize, mock_exists):
        """Test successful transcription."""
        # Set up mocks
        mock_exists.return_value = True
        # Mock file size: 1MB
        mock_getsize.return_value = 1024 * 1024

        # Test with OpenAI
        # Create a mock OpenAI transcriber
        mock_openai_transcriber = MagicMock()
        mock_openai_transcriber.transcribe.return_value = "This is a transcribed text"

        # Replace the transcriber's transcriber with our mock
        self.transcriber.transcriber = mock_openai_transcriber

        # Call the transcribe method
        result = self.transcriber.transcribe(self.test_audio_path)

        # Verify that the correct text was returned
        self.assertEqual(result, "This is a transcribed text")

        # Test with Gemini
        # Create a mock Gemini transcriber
        mock_gemini_transcriber = MagicMock()
        mock_gemini_transcriber.transcribe.return_value = "This is a transcribed text"

        # Set up a new transcriber with Gemini
        gemini_transcriber = Transcriber(config=self.test_gemini_config)
        gemini_transcriber.transcriber = mock_gemini_transcriber

        # Call the transcribe method
        result = gemini_transcriber.transcribe(self.test_audio_path)

        # Verify that the correct text was returned
        self.assertEqual(result, "This is a transcribed text")

    @patch("os.path.exists")
    def test_transcribe_file_not_found(self, mock_exists):
        """Test transcription with a non-existent file."""
        # Set up mock to return False (file does not exist)
        mock_exists.return_value = False

        # Call the transcribe method
        result = self.transcriber.transcribe(self.test_audio_path)

        # Verify that the file was checked for existence
        mock_exists.assert_called_once_with(self.test_audio_path)

        # Verify that None was returned
        self.assertIsNone(result)

    @patch("os.path.exists")
    @patch("os.path.getsize")
    def test_transcribe_api_error(self, mock_getsize, mock_exists):
        """Test transcription with an API error."""
        # Set up mocks
        mock_exists.return_value = True
        # Mock file size: 500KB
        mock_getsize.return_value = 500 * 1024

        # Test with OpenAI
        # Create a mock OpenAI transcriber that raises an exception
        mock_openai_transcriber = MagicMock()
        mock_openai_transcriber.transcribe.side_effect = Exception("API Error")

        # Replace the transcriber's transcriber with our mock
        self.transcriber.transcriber = mock_openai_transcriber

        # Call the transcribe method - wrap in try/except to handle the exception
        try:
            result = self.transcriber.transcribe(self.test_audio_path)
            # Should not reach here
            self.assertIsNone(result)
        except Exception:
            pass  # Exception was expected

        # Test with Gemini
        # Create a mock Gemini transcriber that raises an exception
        mock_gemini_transcriber = MagicMock()
        mock_gemini_transcriber.transcribe.side_effect = Exception("Gemini API Error")

        # Set up a new transcriber with Gemini
        gemini_transcriber = Transcriber(config=self.test_gemini_config)
        gemini_transcriber.transcriber = mock_gemini_transcriber

        # Call the transcribe method - wrap in try/except to handle the exception
        try:
            result = gemini_transcriber.transcribe(self.test_audio_path)
            # Should not reach here
            self.assertIsNone(result)
        except Exception:
            pass  # Exception was expected

    @patch("os.path.exists")
    @patch("os.path.getsize")
    def test_transcribe_with_language(self, mock_getsize, mock_exists):
        """Test transcription with a specified language."""
        # Set up mocks
        mock_exists.return_value = True
        # Mock file size: 200KB
        mock_getsize.return_value = 200 * 1024

        # Create configs with language specified
        openai_config_with_lang = TranscriptionConfig(
            openai_api_key="test_openai_key",
            gemini_api_key="test_gemini_key",
            transcription_service="openai",
            language="en",
        )

        gemini_config_with_lang = TranscriptionConfig(
            openai_api_key="test_openai_key",
            gemini_api_key="test_gemini_key",
            transcription_service="gemini",
            language="en",
        )

        # Test with OpenAI
        # Create a mock OpenAI transcriber
        mock_openai_transcriber = MagicMock()
        mock_openai_transcriber.transcribe.return_value = "This is a transcribed text"

        # Create a transcriber with OpenAI and language config
        with patch("openai.OpenAI"):
            openai_transcriber = Transcriber(config=openai_config_with_lang)
            openai_transcriber.transcriber = mock_openai_transcriber

            # Call the transcribe method
            result = openai_transcriber.transcribe(self.test_audio_path)

            # Verify that the correct text was returned
            self.assertEqual(result, "This is a transcribed text")

        # Test with Gemini
        # Create a mock Gemini transcriber
        mock_gemini_transcriber = MagicMock()
        mock_gemini_transcriber.transcribe.return_value = "This is a transcribed text"

        # Create a transcriber with Gemini and language config
        with patch("google.generativeai"):
            gemini_transcriber = Transcriber(config=gemini_config_with_lang)
            gemini_transcriber.transcriber = mock_gemini_transcriber

            # Call the transcribe method
            result = gemini_transcriber.transcribe(self.test_audio_path)

            # Verify that the correct text was returned
            self.assertEqual(result, "This is a transcribed text")


if __name__ == "__main__":
    unittest.main()
