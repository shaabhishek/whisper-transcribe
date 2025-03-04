"""
Keyboard listener for detecting activation key combinations.
"""

from typing import Any, Callable, Set

from pynput.keyboard import Listener

from speech_transcriber.config import ACTIVATION_KEYS


class KeyboardListener:
    """Listens for keyboard events to detect activation key combinations."""

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
        self.all_keys_pressed = False

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
        self.all_keys_pressed = False

    def _on_press(self, key: Any) -> None:
        """Handle key press events."""
        self.current_keys.add(key)

        # Check if all activation keys are pressed
        if (
            ACTIVATION_KEYS["modifier1"] in self.current_keys
            and ACTIVATION_KEYS["modifier2"] in self.current_keys
            and ACTIVATION_KEYS["main_key"] in self.current_keys
            and not self.all_keys_pressed
        ):
            self.all_keys_pressed = True

    def _on_release(self, key: Any) -> None:
        """Handle key release events."""
        try:
            self.current_keys.remove(key)
        except KeyError:
            pass

        # Check if any of the activation keys were released while all keys were pressed
        if self.all_keys_pressed and (
            key == ACTIVATION_KEYS["modifier1"]
            or key == ACTIVATION_KEYS["modifier2"]
            or key == ACTIVATION_KEYS["main_key"]
        ):
            self.all_keys_pressed = False

            # Toggle recording state
            if not self.is_recording:
                self.is_recording = True
                self.on_activate()
            else:
                self.is_recording = False
                self.on_deactivate()
