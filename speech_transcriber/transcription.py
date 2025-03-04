"""
Transcription functionality using OpenAI's Whisper API.
"""

import os
from typing import Optional

from openai import OpenAI

from speech_transcriber.config import LANGUAGE, OPENAI_API_KEY, WHISPER_MODEL


class Transcriber:
    """Transcribes audio files using OpenAI's Whisper API."""

    def __init__(self):
        # Initialize the OpenAI client
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def transcribe(self, audio_file_path: str) -> Optional[str]:
        """
        Transcribe the audio file using the Whisper API.

        Args:
            audio_file_path: Path to the audio file to transcribe

        Returns:
            The transcribed text, or None if transcription failed
        """
        if not os.path.exists(audio_file_path):
            print(f"Error: Audio file not found at {audio_file_path}")
            return None

        # Get and print the file size
        file_size_bytes = os.path.getsize(audio_file_path)
        file_size_kb = file_size_bytes / 1024
        file_size_mb = file_size_kb / 1024

        if file_size_mb >= 1:
            print(f"Uploading audio file ({file_size_mb:.2f} MB) to Whisper API...")
        else:
            print(f"Uploading audio file ({file_size_kb:.2f} KB) to Whisper API...")

        try:
            with open(audio_file_path, "rb") as audio_file:
                # Prepare the request parameters
                params = {
                    "model": WHISPER_MODEL,
                    "file": audio_file,
                }

                # Add language if specified
                if LANGUAGE:
                    params["language"] = LANGUAGE

                # Make the API request using the new client format
                response = self.client.audio.transcriptions.create(**params)

                # Extract and return the transcribed text
                return response.text

        except Exception as e:
            print(f"Error during transcription: {e}")
            return None
