"""
Transcription functionality using various API services.
"""

import base64
from abc import ABC, abstractmethod
from typing import Optional

from openai import OpenAI

from speech_transcriber.transcription_config import TranscriptionConfig
from speech_transcriber.utils import Logger, report_file_size


class BaseTranscriber(ABC):
    """Base class for transcription services."""

    def __init__(self, config: Optional[TranscriptionConfig] = None):
        """
        Initialize the transcriber with configuration.

        Args:
            config: Configuration object. If None, config will be loaded from environment.
        """
        self.config = config or TranscriptionConfig.from_env()

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

    def __init__(self, config: Optional[TranscriptionConfig] = None):
        """
        Initialize the OpenAI transcriber.

        Args:
            config: Configuration object. If None, config will be loaded from environment.
        """
        super().__init__(config)

        # Initialize the OpenAI client
        if not self.config.openai_api_key:
            Logger.error("OpenAI API key is not set")
            raise ValueError("OpenAI API key is not set")

        self.client = OpenAI(api_key=self.config.openai_api_key)

    def transcribe(self, audio_file_path: str) -> Optional[str]:
        """
        Transcribe the audio file using the Whisper API.

        Args:
            audio_file_path: Path to the audio file to transcribe

        Returns:
            The transcribed text, or None if transcription failed
        """
        # Check if the file exists
        file_info = TranscriptionConfig.get_file_info(audio_file_path)
        if file_info is None:
            Logger.error(f"Audio file not found at {audio_file_path}")
            return None

        # Get file size and log it
        file_size_bytes, _, _ = file_info
        report_file_size(file_size_bytes, "Whisper API")

        try:
            with open(audio_file_path, "rb") as audio_file:
                # Prepare the request parameters
                params = {
                    "model": self.config.whisper_model,
                    "file": audio_file,
                }

                # Add language if specified
                if self.config.language:
                    params["language"] = self.config.language

                # Make the API request using the client format
                response = self.client.audio.transcriptions.create(**params)

                # Extract and return the transcribed text
                return response.text

        except Exception as e:
            Logger.error("Error during OpenAI transcription", e)
            return None


class GeminiTranscriber(BaseTranscriber):
    """Transcribes audio files using Google's Gemini API."""

    def __init__(self, config: Optional[TranscriptionConfig] = None):
        """
        Initialize the Gemini transcriber.

        Args:
            config: Configuration object. If None, config will be loaded from environment.
        """
        super().__init__(config)

        try:
            import google.generativeai as genai

            self.genai = genai

            # Configure the Gemini client with the API key
            if not self.config.gemini_api_key:
                raise ValueError("GEMINI_API_KEY is not set")

            self.genai.configure(api_key=self.config.gemini_api_key)
            self.model = self.config.gemini_model
            Logger.info(f"Initialized Gemini transcriber with model: {self.model}")

        except ImportError:
            Logger.error(
                "google-generativeai library not installed. Please install it with: pip install google-generativeai"
            )
            raise
        except ValueError as e:
            Logger.error(f"Error initializing Gemini transcriber: {e}")
            raise

    def transcribe(self, audio_file_path: str) -> Optional[str]:
        """
        Transcribe the audio file using the Gemini API.

        Args:
            audio_file_path: Path to the audio file to transcribe

        Returns:
            The transcribed text, or None if transcription failed
        """
        # Check if the file exists
        file_info = TranscriptionConfig.get_file_info(audio_file_path)
        if file_info is None:
            Logger.error(f"Audio file not found at {audio_file_path}")
            return None

        # Get file size and log it
        file_size_bytes, _, _ = file_info
        report_file_size(file_size_bytes, "Gemini API")

        try:
            # Read the audio file
            with open(audio_file_path, "rb") as audio_file:
                audio_data = audio_file.read()

            # Determine the MIME type based on the file extension
            mime_type = TranscriptionConfig.get_mime_type(audio_file_path)

            # Get a generative model
            model = self.genai.GenerativeModel(self.model)

            # Create a clear transcription prompt
            language_part = (
                f" in {self.config.language}" if self.config.language else ""
            )
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

            Logger.warn("Unexpected response format from Gemini API")
            return None

        except Exception as e:
            Logger.error("Error during Gemini transcription", e)
            return None


class Transcriber:
    """Factory class that provides the appropriate transcription service."""

    def __init__(
        self,
        config: Optional[TranscriptionConfig] = None,
        service: Optional[str] = None,
    ):
        """
        Initialize the transcriber with the appropriate service.

        Args:
            config: Configuration object. If None, config will be loaded from environment.
            service: Transcription service to use. Overrides config.transcription_service if provided.
        """
        self.config = config or TranscriptionConfig.from_env()

        # Override the service if provided
        if service:
            self.config.transcription_service = service.lower()

        # Select the appropriate transcriber based on configuration
        if self.config.transcription_service == "gemini" and self.config.gemini_api_key:
            self.transcriber = GeminiTranscriber(self.config)
            Logger.info("Using Gemini API for transcription")
        elif (
            self.config.transcription_service == "openai" and self.config.openai_api_key
        ):
            self.transcriber = OpenAITranscriber(self.config)
            Logger.info("Using OpenAI Whisper API for transcription")
        else:
            # Default to OpenAI if no valid configuration is found
            Logger.warn(
                f"Invalid transcription service '{self.config.transcription_service}' or missing API key. Defaulting to OpenAI."
            )
            self.transcriber = OpenAITranscriber(self.config)

    def transcribe(self, audio_file_path: str) -> Optional[str]:
        """
        Transcribe the audio file using the configured service.

        Args:
            audio_file_path: Path to the audio file to transcribe

        Returns:
            The transcribed text, or None if transcription failed
        """
        return self.transcriber.transcribe(audio_file_path)
