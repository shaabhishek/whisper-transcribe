"""Tests for the sound module."""

import unittest
from unittest.mock import MagicMock, patch

from speech_transcriber.sound import play_sound, play_start_sound, play_stop_sound


class TestSound(unittest.TestCase):
    """Test cases for the sound module."""

    @patch("os.path.exists")
    @patch("speech_transcriber.sound.HAVE_PYOBJC", True)
    @patch("speech_transcriber.sound.NSSound")
    def test_play_sound_with_nssound(self, mock_nssound, mock_exists):
        """Test playing a sound using NSSound."""
        # Set up mocks
        mock_exists.return_value = True
        mock_sound = MagicMock()
        mock_nssound.alloc.return_value.initWithContentsOfFile_byReference_.return_value = mock_sound

        # Call the function with a test sound path
        test_sound_path = "/System/Library/Sounds/Hero.aiff"
        result = play_sound(test_sound_path)

        # Verify NSSound was used correctly
        mock_nssound.alloc.assert_called_once()
        mock_nssound.alloc.return_value.initWithContentsOfFile_byReference_.assert_called_once_with(
            test_sound_path, True
        )
        mock_sound.play.assert_called_once()
        self.assertTrue(result)

    @patch("os.path.exists")
    @patch("speech_transcriber.sound.HAVE_PYOBJC", False)
    @patch("subprocess.run")
    def test_play_sound_with_afplay(self, mock_run, mock_exists):
        """Test playing a sound using afplay."""
        # Set up mocks
        mock_exists.return_value = True
        mock_run.return_value.returncode = 0

        # Call the function with a test sound path
        test_sound_path = "/System/Library/Sounds/Hero.aiff"
        result = play_sound(test_sound_path)

        # Verify subprocess.run was called with the correct arguments
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(args[0][0], "afplay")
        self.assertEqual(args[0][1], test_sound_path)
        self.assertTrue(result)

    @patch("os.path.exists")
    def test_play_sound_file_not_found(self, mock_exists):
        """Test playing a sound with a non-existent file."""
        # Set up mock
        mock_exists.return_value = False

        # Capture print output to avoid cluttering test output
        with patch("builtins.print"):
            # Call the function with a non-existent sound path
            test_sound_path = "/System/Library/Sounds/NonExistentSound.aiff"
            result = play_sound(test_sound_path)

            # Verify the result
            self.assertFalse(result)

    @patch("os.path.exists")
    @patch("speech_transcriber.sound.HAVE_PYOBJC", True)
    @patch("speech_transcriber.sound.NSSound")
    def test_play_sound_nssound_failure(self, mock_nssound, mock_exists):
        """Test playing a sound with NSSound failure."""
        # Set up mocks
        mock_exists.return_value = True
        mock_nssound.alloc.return_value.initWithContentsOfFile_byReference_.return_value = None

        # Call the function with a test sound path
        test_sound_path = "/System/Library/Sounds/Hero.aiff"
        result = play_sound(test_sound_path)

        # Verify the result
        self.assertFalse(result)

    @patch("speech_transcriber.sound.play_sound")
    def test_play_start_sound(self, mock_play_sound):
        """Test playing the start sound."""
        # Set up mock
        mock_play_sound.return_value = True

        # Call the function
        result = play_start_sound()

        # Verify play_sound was called with the correct sound path
        mock_play_sound.assert_called_once_with("/System/Library/Sounds/Hero.aiff")
        self.assertTrue(result)

    @patch("speech_transcriber.sound.play_sound")
    def test_play_stop_sound(self, mock_play_sound):
        """Test playing the stop sound."""
        # Set up mock
        mock_play_sound.return_value = True

        # Call the function
        result = play_stop_sound()

        # Verify play_sound was called with the correct sound path
        mock_play_sound.assert_called_once_with("/System/Library/Sounds/Submarine.aiff")
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
