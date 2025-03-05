"""Tests for the keyboard listener module."""

import unittest
from unittest.mock import MagicMock, patch

from pynput.keyboard import Key

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
        self.assertIsNone(self.listener.last_alt_press_time)
        self.assertIsNone(self.listener.last_alt_key)

        # Stopping again should not cause an error
        self.listener.stop()

    def test_is_alt_key(self):
        """Test the _is_alt_key method."""
        # Test with different Alt keys
        self.assertTrue(self.listener._is_alt_key(Key.alt))
        self.assertTrue(self.listener._is_alt_key(Key.alt_l))
        self.assertTrue(self.listener._is_alt_key(Key.alt_r))

        # Test with non-Alt keys
        self.assertFalse(self.listener._is_alt_key(Key.ctrl))
        self.assertFalse(self.listener._is_alt_key(Key.shift))

    def test_on_press_double_alt_activate(self):
        """Test double Alt key press for activation."""
        # Mock the time to control the interval between presses
        with patch("time.time") as mock_time:
            # Set up time values for the first and second press
            mock_time.side_effect = [
                1.0,
                1.2,
            ]  # 0.2 seconds between presses (within threshold)

            # First Alt press
            self.listener._on_press(Key.alt)

            # Verify that tracking started but no activation yet
            self.assertEqual(self.listener.last_alt_press_time, 1.0)
            self.assertEqual(self.listener.last_alt_key, Key.alt)
            self.mock_activate.assert_not_called()

            # Second Alt press (within threshold)
            self.listener._on_press(Key.alt)

            # Verify that on_activate was called
            self.mock_activate.assert_called_once()
            self.assertTrue(self.listener.is_recording)

            # Verify that tracking state was reset
            self.assertIsNone(self.listener.last_alt_press_time)
            self.assertIsNone(self.listener.last_alt_key)

    def test_on_press_double_alt_deactivate(self):
        """Test double Alt key press for deactivation."""
        # Set the listener to recording state
        self.listener.is_recording = True

        # Mock the time to control the interval between presses
        with patch("time.time") as mock_time:
            # Set up time values for the first and second press
            mock_time.side_effect = [
                2.0,
                2.3,
            ]  # 0.3 seconds between presses (within threshold)

            # First Alt press
            self.listener._on_press(Key.alt)

            # Verify that tracking started but no deactivation yet
            self.assertEqual(self.listener.last_alt_press_time, 2.0)
            self.assertEqual(self.listener.last_alt_key, Key.alt)
            self.mock_deactivate.assert_not_called()

            # Second Alt press (within threshold)
            self.listener._on_press(Key.alt)

            # Verify that on_deactivate was called
            self.mock_deactivate.assert_called_once()
            self.assertFalse(self.listener.is_recording)

            # Verify that tracking state was reset
            self.assertIsNone(self.listener.last_alt_press_time)
            self.assertIsNone(self.listener.last_alt_key)

    def test_on_press_slow_alt_presses(self):
        """Test Alt key presses that are too slow to be a double-press."""
        # Mock the time to control the interval between presses
        with patch("time.time") as mock_time:
            # Set up time values for the first and second press
            mock_time.side_effect = [
                3.0,
                4.0,
            ]  # 1.0 seconds between presses (exceeds threshold)

            # First Alt press
            self.listener._on_press(Key.alt)

            # Verify that tracking started
            self.assertEqual(self.listener.last_alt_press_time, 3.0)
            self.assertEqual(self.listener.last_alt_key, Key.alt)

            # Second Alt press (too slow)
            self.listener._on_press(Key.alt)

            # Verify that no activation occurred
            self.mock_activate.assert_not_called()
            self.assertFalse(self.listener.is_recording)

            # Verify that tracking was reset with the new press
            self.assertEqual(self.listener.last_alt_press_time, 4.0)
            self.assertEqual(self.listener.last_alt_key, Key.alt)

    def test_on_press_mixed_alt_keys(self):
        """Test pressing different Alt keys (left then right)."""
        # Mock the time to control the interval between presses
        with patch("time.time") as mock_time:
            # Set up time values for the first and second press
            mock_time.side_effect = [
                5.0,
                5.2,
            ]  # 0.2 seconds between presses (within threshold)

            # First Alt press (left Alt)
            self.listener._on_press(Key.alt_l)

            # Verify that tracking started
            self.assertEqual(self.listener.last_alt_press_time, 5.0)
            self.assertEqual(self.listener.last_alt_key, Key.alt_l)

            # Second Alt press (right Alt)
            self.listener._on_press(Key.alt_r)

            # Verify that activation occurred even with different Alt keys
            self.mock_activate.assert_called_once()
            self.assertTrue(self.listener.is_recording)

    def test_on_release_functionality(self):
        """Test that key release functionality works correctly."""
        # Add a key to current_keys
        self.listener.current_keys.add(Key.alt)

        # Release the key
        self.listener._on_release(Key.alt)

        # Verify that the key was removed from current_keys
        self.assertNotIn(Key.alt, self.listener.current_keys)

        # Verify that no callbacks were called
        self.mock_activate.assert_not_called()
        self.mock_deactivate.assert_not_called()

    def test_on_release_nonexistent_key(self):
        """Test releasing a key that wasn't pressed."""
        # Try to release a key that wasn't pressed
        self.listener._on_release(Key.esc)

        # Verify that no callbacks were called
        self.mock_activate.assert_not_called()
        self.mock_deactivate.assert_not_called()


if __name__ == "__main__":
    unittest.main()
