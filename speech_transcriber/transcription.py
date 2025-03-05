"""
Transcription functionality using various API services.
"""

import base64
import os
from abc import ABC, abstractmethod
from typing import Optional

from openai import OpenAI

from speech_transcriber.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    LANGUAGE,
    OPENAI_API_KEY,
    TRANSCRIPTION_SERVICE,
    WHISPER_MODEL,
)


class BaseTranscriber(ABC):
    """Base class for transcription services."""

    @abstractmethod
    def transcribe(self, audio_file_path: str) -> Optional[str]:
        """
        Transcribe the audio file.

        Args:
            audio_file_path: Path to the audio file to transcribe

        Returns:
            The transcribed text, or None if transcription failed
        """
        pass


class OpenAITranscriber(BaseTranscriber):
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
            print(f"Error during OpenAI transcription: {e}")
            return None


class GeminiTranscriber(BaseTranscriber):
    """Transcribes audio files using Google's Gemini API."""

    def __init__(self):
        try:
            import google.generativeai as genai

            self.genai = genai

            # Configure the Gemini client with the API key
            if not GEMINI_API_KEY:
                raise ValueError("GEMINI_API_KEY is not set")

            self.genai.configure(api_key=GEMINI_API_KEY)
            self.model = GEMINI_MODEL
            print(f"Initialized Gemini transcriber with model: {self.model}")
        except ImportError:
            print(
                "Error: google-generativeai library not installed. Please install it with: pip install google-generativeai"
            )
            raise
        except ValueError as e:
            print(f"Error initializing Gemini transcriber: {e}")
            raise

    def transcribe(self, audio_file_path: str) -> Optional[str]:
        """
        Transcribe the audio file using the Gemini API.

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
            print(f"Uploading audio file ({file_size_mb:.2f} MB) to Gemini API...")
        else:
            print(f"Uploading audio file ({file_size_kb:.2f} KB) to Gemini API...")

        try:
            # Read the audio file
            with open(audio_file_path, "rb") as audio_file:
                audio_data = audio_file.read()

            # Determine the MIME type based on the file extension
            mime_type = "audio/wav"  # Default to WAV
            if audio_file_path.lower().endswith(".mp3"):
                mime_type = "audio/mp3"
            elif audio_file_path.lower().endswith(".aac"):
                mime_type = "audio/aac"
            elif audio_file_path.lower().endswith(".ogg"):
                mime_type = "audio/ogg"
            elif audio_file_path.lower().endswith(".flac"):
                mime_type = "audio/flac"
            elif audio_file_path.lower().endswith(".aiff"):
                mime_type = "audio/aiff"

            # Get a generative model
            model = self.genai.GenerativeModel(self.model)

            # Create a clear transcription prompt
            language_part = f" in {LANGUAGE}" if LANGUAGE else ""
            prompt = (
                f"Please transcribe the following audio file accurately{language_part}. "
                f"Provide only the transcribed text without any explanations or additional commentary."
            )

            # Create multimodal content
            content = [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": mime_type,
                                "data": base64.b64encode(audio_data).decode("utf-8"),
                            }
                        },
                    ]
                }
            ]

            # Set generation config for better transcription results
            generation_config = {
                "temperature": 0.0,  # Use lowest temperature for accurate transcription
                "top_p": 1.0,
                "top_k": 32,
            }

            # Generate content with the audio file
            response = model.generate_content(
                content, generation_config=generation_config
            )

            # Extract the transcription from the response
            if hasattr(response, "text"):
                return response.text.strip()

            print("Warning: Unexpected response format from Gemini API")
            return None

        except Exception as e:
            print(f"Error during Gemini transcription: {e}")
            return None


class Transcriber:
    """Factory class that provides the appropriate transcription service."""

    def __init__(self):
        # Select the appropriate transcriber based on configuration
        if TRANSCRIPTION_SERVICE == "gemini" and GEMINI_API_KEY:
            self.transcriber = GeminiTranscriber()
            print("Using Gemini API for transcription")
        elif TRANSCRIPTION_SERVICE == "openai" and OPENAI_API_KEY:
            self.transcriber = OpenAITranscriber()
            print("Using OpenAI Whisper API for transcription")
        else:
            # Default to OpenAI if no valid configuration is found
            print(
                f"Warning: Invalid transcription service '{TRANSCRIPTION_SERVICE}' or missing API key. Defaulting to OpenAI."
            )
            self.transcriber = OpenAITranscriber()

    def transcribe(self, audio_file_path: str) -> Optional[str]:
        """
        Transcribe the audio file using the configured service.

        Args:
            audio_file_path: Path to the audio file to transcribe

        Returns:
            The transcribed text, or None if transcription failed
        """
        return self.transcriber.transcribe(audio_file_path)
