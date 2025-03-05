"""Configuration settings for the Speech Transcriber application."""

import os
from pathlib import Path

# Try to load environment variables from .env file
try:
  from dotenv import load_dotenv

  # Get the project root directory
  ROOT_DIR = Path(__file__).resolve().parent.parent
  ENV_FILE = ROOT_DIR / '.env'

  # Load environment variables from .env file if it exists
  if ENV_FILE.exists():
    load_dotenv(dotenv_path=ENV_FILE)
    print(f'Loaded environment variables from {ENV_FILE}')
except ImportError:
  # python-dotenv is not installed, fallback to os.environ
  pass

# API Configuration
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')

# Transcription Service Configuration
# Options: "openai" or "gemini"
TRANSCRIPTION_SERVICE = os.environ.get('TRANSCRIPTION_SERVICE', 'openai').lower()

# Audio Recording Configuration
SAMPLE_RATE = 16000  # Hz (default rate for Whisper models)
CHANNELS = 1  # Mono
CHUNK_SIZE = 1024  # Frames per buffer
FORMAT = 'wav'  # Audio format
MAX_RECORDING_TIME = 3600  # Maximum recording time in seconds

# OpenAI Whisper API Configuration
WHISPER_MODEL = 'whisper-1'
LANGUAGE = os.environ.get('LANGUAGE', 'en')  # Language code (optional)

# Gemini API Configuration
GEMINI_MODEL = 'gemini-2.0-flash'  # Model for audio transcription

# UI Configuration
NOTIFICATION_ENABLED = True  # Show notifications during recording/transcription

# Output settings
OUTPUT_DIR = Path(__file__).parent.parent / 'transcripts'

# Ensure output directory exists
OUTPUT_DIR.mkdir(exist_ok=True)
