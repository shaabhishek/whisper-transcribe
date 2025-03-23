"""Configuration data structures for transcription services."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TranscriptionConfig:
  """Configuration for transcription services."""

  # API Keys
  openai_api_key: str
  gemini_api_key: str

  # Service selection
  transcription_service: str

  # Audio configuration
  sample_rate: int
  channels: int
  chunk_size: int
  format: str
  max_recording_time: int

  # Model configuration
  openai_model: str
  gemini_model: str
  language: str

  # Utility for getting file info
  @staticmethod
  def get_file_info(file_path: str) -> Optional[tuple[int, float, float]]:
    """Get file information including existence check and size.

    Args:
        file_path: Path to the file

    Returns:
        Tuple of (file_size_bytes, file_size_kb, file_size_mb) or None if
            file doesn't exist
    """
    import os

    if not os.path.exists(file_path):
      return None

    file_size_bytes = os.path.getsize(file_path)
    file_size_kb = file_size_bytes / 1024
    file_size_mb = file_size_kb / 1024

    return (file_size_bytes, file_size_kb, file_size_mb)

  @staticmethod
  def get_mime_type(audio_file_path: str) -> str:
    """Determine the MIME type based on the file extension.

    Args:
        audio_file_path: Path to the audio file

    Returns:
        MIME type string
    """
    # Default to WAV
    mime_type = 'audio/wav'

    # Check file extension
    path_lower = audio_file_path.lower()
    if path_lower.endswith('.mp3'):
      mime_type = 'audio/mp3'
    elif path_lower.endswith('.aac'):
      mime_type = 'audio/aac'
    elif path_lower.endswith('.ogg'):
      mime_type = 'audio/ogg'
    elif path_lower.endswith('.flac'):
      mime_type = 'audio/flac'
    elif path_lower.endswith('.aiff'):
      mime_type = 'audio/aiff'

    return mime_type

  @classmethod
  def from_env(cls):
    """Create a TranscriptionConfig from environment variables.

    Returns:
        TranscriptionConfig instance
    """
    from speech_transcriber.config import CHANNELS
    from speech_transcriber.config import CHUNK_SIZE
    from speech_transcriber.config import FORMAT
    from speech_transcriber.config import GEMINI_API_KEY
    from speech_transcriber.config import GEMINI_MODEL
    from speech_transcriber.config import LANGUAGE
    from speech_transcriber.config import MAX_RECORDING_TIME
    from speech_transcriber.config import OPENAI_API_KEY
    from speech_transcriber.config import OPENAI_MODEL
    from speech_transcriber.config import SAMPLE_RATE
    from speech_transcriber.config import TRANSCRIPTION_SERVICE

    return cls(
      openai_api_key=OPENAI_API_KEY,
      gemini_api_key=GEMINI_API_KEY,
      transcription_service=TRANSCRIPTION_SERVICE,
      sample_rate=SAMPLE_RATE,
      channels=CHANNELS,
      chunk_size=CHUNK_SIZE,
      format=FORMAT,
      max_recording_time=MAX_RECORDING_TIME,
      openai_model=OPENAI_MODEL,
      gemini_model=GEMINI_MODEL,
      language=LANGUAGE,
    )
