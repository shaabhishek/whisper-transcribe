"""
Tests for the main application module.
"""

import signal
import unittest
from unittest.mock import MagicMock, call, patch

from speech_transcriber.__main__ import SpeechTranscriber, main


class TestSpeechTranscriber(unittest.TestCase):
    """Test cases for the SpeechTranscriber class."""

    @patch("speech_transcriber.__main__.AudioRecorder")
    @patch("speech_transcriber.__main__.Transcriber")
    @patch("speech_transcriber.__main__.KeyboardListener")
    def setUp(self, mock_keyboard_listener, mock_transcriber, mock_audio_recorder):
        """Set up test fixtures."""
        # Create mock instances
        self.mock_audio_recorder = MagicMock()
        self.mock_transcriber = MagicMock()
        self.mock_keyboard_listener = MagicMock()

        # Set up the mocks to return our mock instances
        mock_audio_recorder.return_value = self.mock_audio_recorder
        mock_transcriber.return_value = self.mock_transcriber
        mock_keyboard_listener.return_value = self.mock_keyboard_listener

        # Initialize the application
        self.app = SpeechTranscriber()

        # Verify that the components were initialized correctly
        mock_audio_recorder.assert_called_once()
        mock_transcriber.assert_called_once()
        mock_keyboard_listener.assert_called_once()

        # Verify that the keyboard listener was initialized with the correct callbacks
        args, kwargs = mock_keyboard_listener.call_args
        self.assertEqual(kwargs["on_activate"], self.app.start_recording)
        self.assertEqual(
            kwargs["on_deactivate"], self.app.stop_recording_and_transcribe
        )

    @patch("speech_transcriber.__main__.OPENAI_API_KEY", "test_api_key")
    @patch("signal.signal")
    def test_start(self, mock_signal):
        """Test starting the application."""
        # Mock time.sleep to avoid blocking
        with patch("time.sleep", side_effect=KeyboardInterrupt):
            # Start the application
            self.app.start()

            # Verify that the signal handlers were set up
            mock_signal.assert_has_calls(
                [
                    call(signal.SIGINT, self.app.handle_signal),
                    call(signal.SIGTERM, self.app.handle_signal),
                ]
            )

            # Verify that the keyboard listener was started
            self.mock_keyboard_listener.start.assert_called_once()

    @patch("speech_transcriber.__main__.OPENAI_API_KEY", "")
    @patch("sys.exit")
    @patch("time.sleep", side_effect=KeyboardInterrupt)
    def test_start_no_api_key(self, mock_sleep, mock_exit):
        """Test starting the application without an API key."""
        # Start the application
        self.app.start()

        # Verify that the application exited with the correct error code
        mock_exit.assert_any_call(1)

    def test_stop(self):
        """Test stopping the application."""
        # Set up the application state
        self.app.running = True

        # Stop the application
        self.app.stop()

        # Verify that the application state was updated
        self.assertFalse(self.app.running)

        # Verify that the keyboard listener was stopped
        self.mock_keyboard_listener.stop.assert_called_once()

        # Verify that the audio recorder was cleaned up
        self.mock_audio_recorder.cleanup.assert_called_once()

    @patch("sys.exit")
    def test_handle_signal(self, mock_exit):
        """Test handling termination signals."""
        # Create mock signal and frame
        mock_signum = signal.SIGINT
        mock_frame = None

        # Handle the signal
        self.app.handle_signal(mock_signum, mock_frame)

        # Verify that the application was stopped
        self.assertFalse(self.app.running)
        self.mock_keyboard_listener.stop.assert_called_once()
        self.mock_audio_recorder.cleanup.assert_called_once()

        # Verify that the application exited
        mock_exit.assert_called_once_with(0)

    @patch("speech_transcriber.__main__.show_notification")
    def test_start_recording(self, mock_show_notification):
        """Test starting recording."""
        # Start recording
        self.app.start_recording()

        # Verify that a notification was shown
        mock_show_notification.assert_called_once_with(
            "Speech Transcriber", "Recording started..."
        )

        # Verify that recording was started
        self.mock_audio_recorder.start_recording.assert_called_once()

    @patch("speech_transcriber.__main__.show_notification")
    @patch("speech_transcriber.__main__.copy_to_clipboard")
    def test_stop_recording_and_transcribe_success(
        self, mock_copy, mock_show_notification
    ):
        """Test stopping recording and transcribing successfully."""
        # Set up mocks
        self.mock_audio_recorder.stop_recording.return_value = (
            "/tmp/test_audio.wav",
            5.0,
        )
        self.mock_transcriber.transcribe.return_value = "This is a test transcription"
        mock_copy.return_value = True

        # Stop recording and transcribe
        self.app.stop_recording_and_transcribe()

        # Verify that recording was stopped
        self.mock_audio_recorder.stop_recording.assert_called_once()

        # Verify that a notification was shown
        mock_show_notification.assert_has_calls(
            [
                call("Speech Transcriber", "Transcribing..."),
                call("Transcription Complete", "Text copied to clipboard (28 chars)"),
            ]
        )

        # Verify that the audio was transcribed
        self.mock_transcriber.transcribe.assert_called_once_with("/tmp/test_audio.wav")

        # Verify that the transcribed text was copied to the clipboard
        mock_copy.assert_called_once_with("This is a test transcription")

    @patch("speech_transcriber.__main__.show_notification")
    def test_stop_recording_and_transcribe_short_recording(
        self, mock_show_notification
    ):
        """Test stopping recording with a recording that's too short."""
        # Set up mocks
        self.mock_audio_recorder.stop_recording.return_value = (
            "/tmp/test_audio.wav",
            0.3,
        )

        # Stop recording and transcribe
        self.app.stop_recording_and_transcribe()

        # Verify that recording was stopped
        self.mock_audio_recorder.stop_recording.assert_called_once()

        # Verify that a notification was shown
        mock_show_notification.assert_has_calls(
            [
                call("Speech Transcriber", "Transcribing..."),
                call("Speech Transcriber", "Recording too short or failed."),
            ]
        )

        # Verify that transcription was not attempted
        self.mock_transcriber.transcribe.assert_not_called()

    @patch("speech_transcriber.__main__.show_notification")
    def test_stop_recording_and_transcribe_transcription_failed(
        self, mock_show_notification
    ):
        """Test stopping recording with a failed transcription."""
        # Set up mocks
        self.mock_audio_recorder.stop_recording.return_value = (
            "/tmp/test_audio.wav",
            5.0,
        )
        self.mock_transcriber.transcribe.return_value = None

        # Stop recording and transcribe
        self.app.stop_recording_and_transcribe()

        # Verify that recording was stopped
        self.mock_audio_recorder.stop_recording.assert_called_once()

        # Verify that a notification was shown
        mock_show_notification.assert_has_calls(
            [
                call("Speech Transcriber", "Transcribing..."),
                call("Speech Transcriber", "Transcription failed."),
            ]
        )

        # Verify that the audio was transcribed
        self.mock_transcriber.transcribe.assert_called_once_with("/tmp/test_audio.wav")

    @patch("speech_transcriber.__main__.show_notification")
    @patch("speech_transcriber.__main__.copy_to_clipboard")
    def test_stop_recording_and_transcribe_copy_failed(
        self, mock_copy, mock_show_notification
    ):
        """Test stopping recording with a failed clipboard copy."""
        # Set up mocks
        self.mock_audio_recorder.stop_recording.return_value = (
            "/tmp/test_audio.wav",
            5.0,
        )
        self.mock_transcriber.transcribe.return_value = "This is a test transcription"
        mock_copy.return_value = False

        # Stop recording and transcribe
        self.app.stop_recording_and_transcribe()

        # Verify that recording was stopped
        self.mock_audio_recorder.stop_recording.assert_called_once()

        # Verify that a notification was shown
        mock_show_notification.assert_has_calls(
            [
                call("Speech Transcriber", "Transcribing..."),
                call("Transcription Complete", "Failed to copy to clipboard"),
            ]
        )

        # Verify that the audio was transcribed
        self.mock_transcriber.transcribe.assert_called_once_with("/tmp/test_audio.wav")

        # Verify that the transcribed text was copied to the clipboard
        mock_copy.assert_called_once_with("This is a test transcription")

    @patch("speech_transcriber.__main__.SpeechTranscriber")
    def test_main(self, mock_speech_transcriber):
        """Test the main entry point."""
        # Create a mock application instance
        mock_app = MagicMock()
        mock_speech_transcriber.return_value = mock_app

        # Call the main function
        main()

        # Verify that the application was created and started
        mock_speech_transcriber.assert_called_once()
        mock_app.start.assert_called_once()


if __name__ == "__main__":
    unittest.main()
