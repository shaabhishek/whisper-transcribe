"""
Keyboard listener for detecting activation key combinations.
"""

import time
from typing import Any, Callable, Optional, Set

from pynput.keyboard import Key, Listener


class KeyboardListener:
    """Listens for keyboard events to detect activation key combinations."""

    # Maximum time in seconds between two key presses to be considered a double-press
    DOUBLE_PRESS_INTERVAL = 0.5

    def __init__(
        self, on_activate: Callable[[], None], on_deactivate: Callable[[], None]
    ):
        """
        Initialize the keyboard listener.

        Args:
            on_activate: Callback function to call when activation keys are pressed to start recording
            on_deactivate: Callback function to call when activation keys are pressed to stop recording
        """
        self.on_activate = on_activate
        self.on_deactivate = on_deactivate
        self.listener = None
        self.current_keys: Set[Any] = set()
        self.is_recording = False

        # State for tracking double-press
        self.last_alt_press_time: Optional[float] = None
        self.last_alt_key: Optional[Any] = None

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
        self.last_alt_press_time = None
        self.last_alt_key = None

    def _is_alt_key(self, key: Any) -> bool:
        """Check if a key is either left or right Alt."""
        return key == Key.alt or key == Key.alt_l or key == Key.alt_r

    def _on_press(self, key: Any) -> None:
        """Handle key press events."""
        self.current_keys.add(key)

        # Check if an Alt key was pressed
        if self._is_alt_key(key):
            current_time = time.time()

            # Check if it's a double-press
            if (
                self.last_alt_press_time is not None
                and current_time - self.last_alt_press_time < self.DOUBLE_PRESS_INTERVAL
                and self._is_alt_key(self.last_alt_key)
            ):
                # Toggle recording state
                if not self.is_recording:
                    self.is_recording = True
                    self.on_activate()
                else:
                    self.is_recording = False
                    self.on_deactivate()

                # Reset double-press tracking
                self.last_alt_press_time = None
                self.last_alt_key = None
            else:
                # Start tracking this press
                self.last_alt_press_time = current_time
                self.last_alt_key = key

    def _on_release(self, key: Any) -> None:
        """Handle key release events."""
        try:
            self.current_keys.remove(key)
        except KeyError:
            pass
