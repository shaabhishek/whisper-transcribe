"""Tests for the notification module."""

import unittest
from unittest.mock import patch

from speech_transcriber.notification import _show_macos_notification, show_notification


class TestNotification(unittest.TestCase):
    """Test cases for the notification module."""

    @patch("speech_transcriber.notification.NOTIFICATION_ENABLED", True)
    def test_show_notification_macos(self):
        """Test showing a notification on macOS."""
        with patch(
            "speech_transcriber.notification._show_macos_notification"
        ) as mock_macos:
            show_notification("Test Title", "Test Message")

            # Verify that the macOS notification function was called with the correct arguments
            mock_macos.assert_called_once_with("Test Title", "Test Message")

    @patch("speech_transcriber.notification.NOTIFICATION_ENABLED", False)
    def test_show_notification_disabled(self):
        """Test that notifications are not shown when disabled."""
        with patch(
            "speech_transcriber.notification._show_macos_notification"
        ) as mock_macos:
            show_notification("Test Title", "Test Message")

            # Verify that the notification function was not called
            mock_macos.assert_not_called()

    @patch(
        "speech_transcriber.notification._show_macos_notification",
        side_effect=Exception("Test error"),
    )
    def test_show_notification_error(self, mock_macos):
        """Test handling notification errors."""
        with patch("builtins.print") as mock_print:
            show_notification("Test Title", "Test Message")

            # Verify that the error was printed
            mock_print.assert_any_call("Error showing notification: Test error")
            mock_print.assert_any_call("Test Title: Test Message")

    @patch("subprocess.run")
    def test_show_macos_notification(self, mock_run):
        """Test the macOS notification function."""
        _show_macos_notification("Test Title", "Test Message")

        # Verify that subprocess.run was called with the correct command
        mock_run.assert_called_once()
        args = mock_run.call_args[0][0]
        self.assertIn("osascript", args)
        self.assertIn("Test Title", args)
        self.assertIn("Test Message", args)


if __name__ == "__main__":
    unittest.main()
