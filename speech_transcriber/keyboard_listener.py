"""Keyboard listener for detecting activation key combinations."""

import time
from typing import Any
from typing import Callable
from typing import Optional
from typing import Set

from pynput.keyboard import Key
from pynput.keyboard import Listener


class KeyboardListener:
  """Listens for keyboard events to detect double-press of Ctrl key."""

  # Maximum time in seconds between two key presses to be considered a double-press
  DOUBLE_PRESS_INTERVAL = 0.5

  def __init__(
    self, on_activate: Callable[[], None], on_deactivate: Callable[[], None]
  ):
    """Initialize the keyboard listener.

    Args:
        on_activate: Callback function to call when activation keys are
            pressed to start recording
        on_deactivate: Callback function to call when activation keys are
            pressed to stop recording
    """
    self.on_activate = on_activate
    self.on_deactivate = on_deactivate
    self.listener = None
    self.current_keys: Set[Any] = set()
    self.is_recording = False

    # State for tracking double-press (now for Ctrl)
    self.last_ctrl_press_time: Optional[float] = None
    self.last_ctrl_key: Optional[Any] = None

  def start(self) -> None:
    """Start listening for keyboard events."""
    if self.listener is not None:
      return

    self.listener = Listener(on_press=self._on_press, on_release=self._on_release)
    self.listener.start()

  def stop(self) -> None:
    """Stop listening for keyboard events."""
    if self.listener is None:
      return

    self.listener.stop()
    self.listener = None
    self.current_keys.clear()
    self.is_recording = False
    # Reset Ctrl tracking state
    self.last_ctrl_press_time = None
    self.last_ctrl_key = None

  def _is_ctrl_key(self, key: Any) -> bool:
    """Check if a key is either left or right Ctrl."""
    # Use Key.ctrl for generic Ctrl, Key.ctrl_l and Key.ctrl_r for specific ones
    return key == Key.ctrl or key == Key.ctrl_l or key == Key.ctrl_r

  def _on_press(self, key: Any) -> None:
    """Handle key press events."""
    # Add key regardless, needed for release tracking
    self.current_keys.add(key)

    # Check if a Ctrl key was pressed
    if self._is_ctrl_key(key):
      current_time = time.time()

      # Check if it's a double-press of Ctrl
      if (
        self.last_ctrl_press_time is not None
        and current_time - self.last_ctrl_press_time < self.DOUBLE_PRESS_INTERVAL
        # Ensure the previous press was also a Ctrl key
        and self._is_ctrl_key(self.last_ctrl_key)
        # Optional: Prevent trigger if another modifier is held (e.g., Shift+Ctrl double press)
        # and not any(k in {Key.shift, Key.alt, Key.cmd} for k in self.current_keys if k != key)
      ):
        # Toggle recording state
        if not self.is_recording:
          self.is_recording = True
          self.on_activate()
        else:
          self.is_recording = False
          self.on_deactivate()

        # Reset double-press tracking
        self.last_ctrl_press_time = None
        self.last_ctrl_key = None
      else:
        # Start tracking this Ctrl press
        self.last_ctrl_press_time = current_time
        self.last_ctrl_key = key

    # If a non-Ctrl key is pressed, reset the double-press sequence
    elif not self._is_ctrl_key(key):
      self.last_ctrl_press_time = None
      self.last_ctrl_key = None

  def _on_release(self, key: Any) -> None:
    """Handle key release events."""
    try:
      self.current_keys.remove(key)
    except KeyError:
      pass
