"""
Tests for the transcription module.
"""

import unittest
from unittest.mock import MagicMock, patch

from speech_transcriber.transcription import Transcriber


class TestTranscription(unittest.TestCase):
    """Test cases for the transcription module."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary test file path
        self.test_audio_path = "/tmp/test_audio.wav"

        # Create a mock API response
        self.mock_response = MagicMock()
        self.mock_response.text = "This is a transcribed text"

        # Initialize the transcriber
        with patch("openai.OpenAI"):
            self.transcriber = Transcriber()

    @patch("os.path.exists")
    @patch("os.path.getsize")
    def test_transcribe_success(self, mock_getsize, mock_exists):
        """Test successful transcription."""
        # Set up mocks
        mock_exists.return_value = True
        # Mock file size: 1MB
        mock_getsize.return_value = 1024 * 1024

        # Mock the OpenAI client and its methods
        mock_client = MagicMock()
        mock_transcriptions = MagicMock()
        mock_client.audio.transcriptions = mock_transcriptions
        mock_transcriptions.create.return_value = self.mock_response

        # Replace the transcriber's client with our mock
        self.transcriber.client = mock_client

        # Mock the file open operation and capture print output
        mock_file = MagicMock()
        with (
            patch("builtins.open", return_value=mock_file),
            patch("builtins.print") as mock_print,
        ):
            # Call the transcribe method
            result = self.transcriber.transcribe(self.test_audio_path)

            # Verify that the file was checked for existence
            mock_exists.assert_called_once_with(self.test_audio_path)

            # Verify that the file size was checked
            mock_getsize.assert_called_once_with(self.test_audio_path)

            # Verify that the file size was printed
            mock_print.assert_any_call(
                "Uploading audio file (1.00 MB) to Whisper API..."
            )

            # Verify that the API was called
            mock_transcriptions.create.assert_called_once()

            # Verify that the correct text was returned
            self.assertEqual(result, "This is a transcribed text")

    @patch("os.path.exists")
    def test_transcribe_file_not_found(self, mock_exists):
        """Test transcription with a non-existent file."""
        # Set up mock to return False (file does not exist)
        mock_exists.return_value = False

        # Capture print output to avoid cluttering test output
        with patch("builtins.print"):
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

        # Mock the OpenAI client and its methods
        mock_client = MagicMock()
        mock_transcriptions = MagicMock()
        mock_client.audio.transcriptions = mock_transcriptions
        mock_transcriptions.create.side_effect = Exception("API Error")

        # Replace the transcriber's client with our mock
        self.transcriber.client = mock_client

        # Mock the file open operation
        mock_file = MagicMock()
        with patch("builtins.open", return_value=mock_file):
            # Capture print output to avoid cluttering test output
            with patch("builtins.print"):
                # Call the transcribe method
                result = self.transcriber.transcribe(self.test_audio_path)

                # Verify that the file was checked for existence
                mock_exists.assert_called_once_with(self.test_audio_path)

                # Verify that the file size was checked
                mock_getsize.assert_called_once_with(self.test_audio_path)

                # Verify that the API was called
                mock_transcriptions.create.assert_called_once()

                # Verify that None was returned
                self.assertIsNone(result)

    @patch("os.path.exists")
    @patch("os.path.getsize")
    def test_transcribe_with_language(self, mock_getsize, mock_exists):
        """Test transcription with a specified language."""
        # Set up mocks
        mock_exists.return_value = True
        # Mock file size: 200KB
        mock_getsize.return_value = 200 * 1024

        # Mock the OpenAI client and its methods
        mock_client = MagicMock()
        mock_transcriptions = MagicMock()
        mock_client.audio.transcriptions = mock_transcriptions
        mock_transcriptions.create.return_value = self.mock_response

        # Replace the transcriber's client with our mock
        self.transcriber.client = mock_client

        # Mock the language setting
        with patch("speech_transcriber.transcription.LANGUAGE", "en"):
            # Mock the file open operation and capture print output
            mock_file = MagicMock()
            with (
                patch("builtins.open", return_value=mock_file),
                patch("builtins.print") as mock_print,
            ):
                # Call the transcribe method
                result = self.transcriber.transcribe(self.test_audio_path)

                # Verify that the file size was checked
                mock_getsize.assert_called_once_with(self.test_audio_path)

                # Verify that the file size was printed
                mock_print.assert_any_call(
                    "Uploading audio file (200.00 KB) to Whisper API..."
                )

                # Verify that the API was called with the language parameter
                args, kwargs = mock_transcriptions.create.call_args
                self.assertEqual(kwargs.get("language"), "en")

                # Verify that the correct text was returned
                self.assertEqual(result, "This is a transcribed text")


if __name__ == "__main__":
    unittest.main()
