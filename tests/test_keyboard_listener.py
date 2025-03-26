"""Tests for the keyboard listener module."""

import time
import unittest
from unittest.mock import MagicMock
from unittest.mock import patch

from pynput.keyboard import Key
from pynput.keyboard import KeyCode

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

    # Set a known interval for testing
    self.listener.DOUBLE_PRESS_INTERVAL = 0.1

  def tearDown(self):
    """Clean up after tests."""
    # Stop the listener if it's running
    if self.listener.listener is not None:
      self.listener.stop()

  def test_start(self):
    """Test starting the keyboard listener."""
    with patch('speech_transcriber.keyboard_listener.Listener') as mock_listener_class:
      # Create a mock listener instance
      mock_listener_instance = MagicMock()
      mock_listener_class.return_value = mock_listener_instance

      # Start the listener
      self.listener.start()

      # Verify that the Listener was created with the correct callbacks
      mock_listener_class.assert_called_once()
      kwargs = mock_listener_class.call_args[1]
      self.assertEqual(kwargs['on_press'], self.listener._on_press)
      self.assertEqual(kwargs['on_release'], self.listener._on_release)

      # Verify that the listener was started
      mock_listener_instance.start.assert_called_once()

      # Starting again should not create a new listener
      self.listener.start()
      mock_listener_class.assert_called_once()

  def test_stop(self):
    """Test stopping the keyboard listener."""
    # Create a mock pynput listener
    mock_pynput_listener = MagicMock()
    self.listener.listener = mock_pynput_listener

    # Simulate some state
    self.listener.is_recording = True
    self.listener.last_ctrl_press_time = time.time()
    self.listener.last_ctrl_key = Key.ctrl_l
    self.listener.current_keys.add(Key.ctrl_l)

    # Stop the listener
    self.listener.stop()

    # Verify that the pynput listener was stopped
    mock_pynput_listener.stop.assert_called_once()
    self.assertIsNone(self.listener.listener)
    self.assertFalse(self.listener.is_recording)
    # Verify Ctrl state is reset
    self.assertIsNone(self.listener.last_ctrl_press_time)
    self.assertIsNone(self.listener.last_ctrl_key)
    self.assertEqual(self.listener.current_keys, set())  # Check current_keys is cleared

    # Stopping again should not cause an error
    self.listener.stop()

  def test_is_ctrl_key(self):
    """Test the _is_ctrl_key method."""
    # Test with different Ctrl keys
    self.assertTrue(self.listener._is_ctrl_key(Key.ctrl))
    self.assertTrue(self.listener._is_ctrl_key(Key.ctrl_l))
    self.assertTrue(self.listener._is_ctrl_key(Key.ctrl_r))

    # Test with non-Ctrl keys
    self.assertFalse(self.listener._is_ctrl_key(Key.alt))
    self.assertFalse(self.listener._is_ctrl_key(Key.shift))
    self.assertFalse(self.listener._is_ctrl_key(Key.cmd))
    self.assertFalse(self.listener._is_ctrl_key(KeyCode.from_char('a')))

  @patch('time.time')
  def test_double_ctrl_activate(self, mock_time):
    """Test activating recording with double Ctrl press."""
    mock_time.side_effect = [100.0, 100.05]  # Simulate two presses 0.05s apart

    # Press Ctrl the first time
    self.listener._on_press(Key.ctrl_l)
    self.mock_activate.assert_not_called()
    self.assertFalse(self.listener.is_recording)
    self.assertEqual(self.listener.last_ctrl_press_time, 100.0)
    self.assertEqual(self.listener.last_ctrl_key, Key.ctrl_l)

    # Press Ctrl the second time (within interval)
    self.listener._on_press(Key.ctrl_r)  # Use different Ctrl key
    self.mock_activate.assert_called_once()
    self.assertTrue(self.listener.is_recording)
    # Verify state is reset after successful double press
    self.assertIsNone(self.listener.last_ctrl_press_time)
    self.assertIsNone(self.listener.last_ctrl_key)

  @patch('time.time')
  def test_double_ctrl_deactivate(self, mock_time):
    """Test deactivating recording with double Ctrl press."""
    mock_time.side_effect = [100.0, 100.05, 101.0, 101.05]

    # First double press (activate)
    self.listener._on_press(Key.ctrl_l)
    self.listener._on_press(Key.ctrl_l)
    self.mock_activate.assert_called_once()
    self.assertTrue(self.listener.is_recording)
    self.mock_deactivate.assert_not_called()

    # Second double press (deactivate)
    self.listener._on_press(Key.ctrl_r)
    self.listener._on_press(Key.ctrl_r)
    self.mock_activate.assert_called_once()  # Still called only once
    self.mock_deactivate.assert_called_once()
    self.assertFalse(self.listener.is_recording)
    # Verify state is reset
    self.assertIsNone(self.listener.last_ctrl_press_time)
    self.assertIsNone(self.listener.last_ctrl_key)

  @patch('time.time')
  def test_single_ctrl_press_no_trigger(self, mock_time):
    """Test that a single Ctrl press does not trigger activation."""
    mock_time.return_value = 100.0
    self.listener._on_press(Key.ctrl_l)
    self.mock_activate.assert_not_called()
    self.mock_deactivate.assert_not_called()
    self.assertFalse(self.listener.is_recording)
    self.assertEqual(
      self.listener.last_ctrl_press_time, 100.0
    )  # State is set for next potential press

  @patch('time.time')
  def test_ctrl_press_too_slow_no_trigger(self, mock_time):
    """Test that two Ctrl presses too far apart do not trigger."""
    mock_time.side_effect = [100.0, 100.2]  # 0.2s apart > DOUBLE_PRESS_INTERVAL

    # Press Ctrl the first time
    self.listener._on_press(Key.ctrl_l)
    self.mock_activate.assert_not_called()
    self.assertEqual(self.listener.last_ctrl_press_time, 100.0)

    # Press Ctrl the second time (outside interval)
    self.listener._on_press(Key.ctrl_l)
    self.mock_activate.assert_not_called()
    self.mock_deactivate.assert_not_called()
    self.assertFalse(self.listener.is_recording)
    # State should now track the second press
    self.assertEqual(self.listener.last_ctrl_press_time, 100.2)
    self.assertEqual(self.listener.last_ctrl_key, Key.ctrl_l)

  @patch('time.time')
  def test_ctrl_then_other_key_no_trigger(self, mock_time):
    """Test that Ctrl followed by a non-Ctrl key resets and does not trigger."""
    mock_time.side_effect = [100.0, 100.1]  # Time for first Ctrl, time for second Ctrl

    # Press Ctrl
    self.listener._on_press(Key.ctrl_l)
    self.assertEqual(self.listener.last_ctrl_press_time, 100.0)
    self.mock_activate.assert_not_called()

    # Press 'a' shortly after (time.time() is NOT called here in the code)
    self.listener._on_press(KeyCode.from_char('a'))
    # Double-press state should be reset
    self.assertIsNone(self.listener.last_ctrl_press_time)
    self.assertIsNone(self.listener.last_ctrl_key)
    self.mock_activate.assert_not_called()
    self.mock_deactivate.assert_not_called()

    # Press Ctrl again - should only register as the first press now
    self.listener._on_press(Key.ctrl_l)
    # This call to time.time() gets the second value from side_effect
    self.assertEqual(self.listener.last_ctrl_press_time, 100.1)
    self.mock_activate.assert_not_called()

  def test_release_key(self):
    """Test releasing a key removes it from current_keys."""
    self.listener._on_press(Key.ctrl_l)
    self.listener._on_press(KeyCode.from_char('a'))
    self.assertEqual(self.listener.current_keys, {Key.ctrl_l, KeyCode.from_char('a')})

    self.listener._on_release(Key.ctrl_l)
    self.assertEqual(self.listener.current_keys, {KeyCode.from_char('a')})

    # Releasing a key not pressed should not error
    self.listener._on_release(Key.shift)
    self.assertEqual(self.listener.current_keys, {KeyCode.from_char('a')})

    self.listener._on_release(KeyCode.from_char('a'))
    self.assertEqual(self.listener.current_keys, set())


if __name__ == '__main__':
  unittest.main()
