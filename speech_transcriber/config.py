"""
Configuration settings for the Speech Transcriber application.
"""

import os

from pynput.keyboard import Key, KeyCode

# API Configuration
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Audio Recording Configuration
SAMPLE_RATE = 44100  # Hz
CHANNELS = 1  # Mono
CHUNK_SIZE = 1024  # Frames per buffer
FORMAT = "wav"  # Audio format
MAX_RECORDING_TIME = 120  # Maximum recording time in seconds

# Keyboard Shortcut Configuration
# Default: Command + Shift + ' (apostrophe)
ACTIVATION_KEYS = {
    "modifier1": Key.cmd,
    "modifier2": Key.shift,
    "main_key": KeyCode.from_char("'"),
}

# Whisper API Configuration
WHISPER_MODEL = "whisper-1"
LANGUAGE = "en"  # Language code (optional)

# UI Configuration
NOTIFICATION_ENABLED = True  # Show notifications during recording/transcription
