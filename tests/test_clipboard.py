"""
Tests for the clipboard module.
"""

import unittest
from unittest.mock import patch

from speech_transcriber.clipboard import copy_to_clipboard, paste_from_clipboard


class TestClipboard(unittest.TestCase):
    """Test cases for the clipboard module."""

    def test_copy_to_clipboard_success(self):
        """Test that text is successfully copied to the clipboard."""
        test_text = "This is a test text for clipboard"

        # Mock pyperclip.copy to avoid actual clipboard operations
        with patch("pyperclip.copy") as mock_copy:
            result = copy_to_clipboard(test_text)

            # Verify that pyperclip.copy was called with the correct text
            mock_copy.assert_called_once_with(test_text)

            # Verify that the function returned True (success)
            self.assertTrue(result)

    def test_copy_to_clipboard_failure(self):
        """Test handling of clipboard copy failures."""
        test_text = "This is a test text for clipboard"

        # Mock pyperclip.copy to raise an exception
        with patch("pyperclip.copy", side_effect=Exception("Clipboard error")):
            # Capture print output to avoid cluttering test output
            with patch("builtins.print"):
                result = copy_to_clipboard(test_text)

                # Verify that the function returned False (failure)
                self.assertFalse(result)

    def test_paste_from_clipboard_success(self):
        """Test that text is successfully pasted from the clipboard."""
        expected_text = "This is a test text from clipboard"

        # Mock pyperclip.paste to return a predefined text
        with patch("pyperclip.paste", return_value=expected_text):
            result = paste_from_clipboard()

            # Verify that the function returned the expected text
            self.assertEqual(result, expected_text)

    def test_paste_from_clipboard_failure(self):
        """Test handling of clipboard paste failures."""

        # Mock pyperclip.paste to raise an exception
        with patch("pyperclip.paste", side_effect=Exception("Clipboard error")):
            # Capture print output to avoid cluttering test output
            with patch("builtins.print"):
                result = paste_from_clipboard()

                # Verify that the function returned an empty string
                self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
