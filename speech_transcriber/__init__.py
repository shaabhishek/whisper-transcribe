"""
Speech Transcriber - A speech-to-text transcription tool activated by keypress.
"""

__version__ = "0.1.0"

from speech_transcriber.transcription import (
    BaseTranscriber,
    GeminiTranscriber,
    OpenAITranscriber,
    Transcriber,
)
from speech_transcriber.transcription_config import TranscriptionConfig
from speech_transcriber.utils import Logger

__all__ = [
    "BaseTranscriber",
    "OpenAITranscriber",
    "GeminiTranscriber",
    "Transcriber",
    "TranscriptionConfig",
    "Logger",
]
