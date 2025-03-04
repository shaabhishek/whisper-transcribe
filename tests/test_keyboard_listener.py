"""
Tests for the keyboard listener module.
"""

import unittest
from unittest.mock import MagicMock, patch

from pynput.keyboard import Key

from speech_transcriber.config import ACTIVATION_KEYS
from speech_transcriber.keyboard_listener import KeyboardListener


class TestKeyboardListener(unittest.TestCase):
    """Test cases for the keyboard listener module."""

    def setUp(self):
        """Set up test fixtures."""
        # Create mock callback functions
        self.mock_activate = MagicMock()
        self.mock_deactivate = MagicMock()

        # Create a keyboard listener
        self.listener = KeyboardListener(
            on_activate=self.mock_activate,
            on_deactivate=self.mock_deactivate,
        )

        # Reset mock call counts
        self.mock_activate.reset_mock()
        self.mock_deactivate.reset_mock()

    def tearDown(self):
        """Clean up after tests."""
        # Stop the listener if it's running
        if self.listener.listener is not None:
            self.listener.stop()

    def test_start(self):
        """Test starting the keyboard listener."""
        with patch(
            "speech_transcriber.keyboard_listener.Listener"
        ) as mock_listener_class:
            # Create a mock listener instance
            mock_listener_instance = MagicMock()
            mock_listener_class.return_value = mock_listener_instance

            # Start the listener
            self.listener.start()

            # Verify that the Listener was created with the correct callbacks
            mock_listener_class.assert_called_once()
            kwargs = mock_listener_class.call_args[1]
            self.assertEqual(kwargs["on_press"], self.listener._on_press)
            self.assertEqual(kwargs["on_release"], self.listener._on_release)

            # Verify that the listener was started
            mock_listener_instance.start.assert_called_once()

            # Starting again should not create a new listener
            self.listener.start()
            mock_listener_class.assert_called_once()

    def test_stop(self):
        """Test stopping the keyboard listener."""
        # Create a mock listener
        mock_listener = MagicMock()
        self.listener.listener = mock_listener

        # Stop the listener
        self.listener.stop()

        # Verify that the listener was stopped
        mock_listener.stop.assert_called_once()
        self.assertIsNone(self.listener.listener)
        self.assertFalse(self.listener.is_recording)
        self.assertFalse(self.listener.all_keys_pressed)

        # Stopping again should not cause an error
        self.listener.stop()

    def test_on_press_activation(self):
        """Test key press handling for activation."""
        # Press the activation keys one by one
        self.listener._on_press(ACTIVATION_KEYS["modifier1"])
        self.listener._on_press(ACTIVATION_KEYS["modifier2"])

        # Verify that no activation occurred yet
        self.mock_activate.assert_not_called()

        # Press the main key to complete the activation
        self.listener._on_press(ACTIVATION_KEYS["main_key"])

        # Verify that all_keys_pressed is set to True
        self.assertTrue(self.listener.all_keys_pressed)

        # Verify that on_activate was not called yet (should be called on release)
        self.mock_activate.assert_not_called()

    def test_on_release_toggle_recording(self):
        """Test key release handling for toggling recording."""
        # Set up the state as if all keys were pressed
        self.listener._on_press(ACTIVATION_KEYS["modifier1"])
        self.listener._on_press(ACTIVATION_KEYS["modifier2"])
        self.listener._on_press(ACTIVATION_KEYS["main_key"])
        self.listener.all_keys_pressed = True

        # Release one of the keys
        self.listener._on_release(ACTIVATION_KEYS["main_key"])

        # Verify that all_keys_pressed is reset
        self.assertFalse(self.listener.all_keys_pressed)

        # Verify that on_activate was called (start recording)
        self.mock_activate.assert_called_once()
        self.assertTrue(self.listener.is_recording)

        # Press and release the keys again
        self.listener._on_press(ACTIVATION_KEYS["modifier1"])
        self.listener._on_press(ACTIVATION_KEYS["modifier2"])
        self.listener._on_press(ACTIVATION_KEYS["main_key"])
        self.listener.all_keys_pressed = True
        self.listener._on_release(ACTIVATION_KEYS["main_key"])

        # Verify that on_deactivate was called (stop recording)
        self.mock_deactivate.assert_called_once()
        self.assertFalse(self.listener.is_recording)

    def test_on_release_nonexistent_key(self):
        """Test releasing a key that wasn't pressed."""
        # Try to release a key that wasn't pressed
        self.listener._on_release(Key.esc)

        # Verify that no callbacks were called
        self.mock_activate.assert_not_called()
        self.mock_deactivate.assert_not_called()


if __name__ == "__main__":
    unittest.main()
