"""Transcription functionality using various API services."""

from abc import ABC
from abc import abstractmethod
import base64
import os
from typing import Optional
from typing import Tuple

from openai import OpenAI

from speech_transcriber.audio_compression import AudioCompressor
from speech_transcriber.transcription_config import TranscriptionConfig
from speech_transcriber.utils import Logger
from speech_transcriber.utils import report_file_size


class BaseTranscriber(ABC):
  """Base class for transcription services."""

  def __init__(self, config: Optional[TranscriptionConfig] = None):
    """Initialize the transcriber with configuration.

    Args:
        config: Configuration object. If None, config will be loaded from environment.
    """
    self.config = config or TranscriptionConfig.from_env()

  @abstractmethod
  def transcribe(self, audio_file_path: str) -> Optional[str]:
    """Transcribe the audio file.

    Args:
        audio_file_path: Path to the audio file to transcribe

    Returns:
        The transcribed text, or None if transcription failed
    """
    pass

  def cleanup(self) -> None:
    """Clean up resources used by the transcriber.

    Should be called when the application is shutting down.
    """
    pass


class OpenAITranscriber(BaseTranscriber):
  """Transcribes audio files using OpenAI's GPT-4o API."""

  def __init__(self, config: Optional[TranscriptionConfig] = None):
    """Initialize the OpenAI transcriber.

    Args:
        config: Configuration object. If None, config will be loaded from environment.
    """
    super().__init__(config)

    # Initialize the OpenAI client
    if not self.config.openai_api_key:
      Logger.error('OpenAI API key is not set')
      raise ValueError('OpenAI API key is not set')

    self.client = OpenAI(api_key=self.config.openai_api_key)

  def transcribe(self, audio_file_path: str) -> Optional[str]:
    """Transcribe the audio file using the GPT-4o API.

    Args:
        audio_file_path: Path to the audio file to transcribe

    Returns:
        The transcribed text, or None if transcription failed
    """
    # Check if the file exists
    file_info = TranscriptionConfig.get_file_info(audio_file_path)
    if file_info is None:
      Logger.error(f'Audio file not found at {audio_file_path}')
      return None

    # Get file size and log it
    file_size_bytes, _, _ = file_info
    report_file_size(file_size_bytes, 'GPT-4o API')

    try:
      with open(audio_file_path, 'rb') as audio_file:
        # Prepare the request parameters
        params = {
          'model': self.config.openai_model,
          'file': audio_file,
        }

        # Add language if specified
        if self.config.language:
          params['language'] = self.config.language

        # Make the API request using the client format
        response = self.client.audio.transcriptions.create(**params)

        # Extract and return the transcribed text
        return response.text

    except Exception as e:
      Logger.error('Error during OpenAI transcription', e)
      return None

  def cleanup(self) -> None:
    """Clean up resources used by the OpenAI transcriber."""
    # Nothing special to clean up for OpenAI client
    pass


class GeminiTranscriber(BaseTranscriber):
  """Transcribes audio files using Google's Gemini API."""

  def __init__(self, config: Optional[TranscriptionConfig] = None):
    """Initialize the Gemini transcriber.

    Args:
        config: Configuration object. If None, config will be loaded from environment.
    """
    super().__init__(config)

    try:
      # Set environment variable to prevent or reduce absl logging issues
      os.environ['ABSL_LOGGING_VERBOSITY'] = '0'

      # Try to initialize absl logging early
      try:
        import absl.logging

        absl.logging.set_verbosity(absl.logging.ERROR)
        absl.logging.use_python_logging()
      except ImportError:
        pass

      import google.generativeai as genai

      self.genai = genai

      # Configure the Gemini client with the API key
      if not self.config.gemini_api_key:
        raise ValueError('GEMINI_API_KEY is not set')

      self.genai.configure(api_key=self.config.gemini_api_key)
      self.model = self.config.gemini_model
      Logger.info(f'Initialized Gemini transcriber with model: {self.model}')

    except ImportError:
      Logger.error(
        'google-generativeai library not installed. '
        'Please install it with: pip install google-generativeai'
      )
      raise
    except ValueError as e:
      Logger.error(f'Error initializing Gemini transcriber: {e}')
      raise

  def transcribe(self, audio_file_path: str) -> Optional[str]:
    """Transcribe the audio file using the Gemini API.

    Args:
        audio_file_path: Path to the audio file to transcribe

    Returns:
        The transcribed text, or None if transcription failed
    """
    # Check if the file exists
    file_info = TranscriptionConfig.get_file_info(audio_file_path)
    if file_info is None:
      Logger.error(f'Audio file not found at {audio_file_path}')
      return None

    # Get file size and log it
    file_size_bytes, _, _ = file_info
    report_file_size(file_size_bytes, 'Gemini API')

    try:
      # Read the audio file
      with open(audio_file_path, 'rb') as audio_file:
        audio_data = audio_file.read()

      # Determine the MIME type based on the file extension
      mime_type = TranscriptionConfig.get_mime_type(audio_file_path)

      # Get a generative model
      model = self.genai.GenerativeModel(self.model)

      # Create a clear transcription prompt
      language_part = f' in {self.config.language}' if self.config.language else ''
      prompt = (
        f'Please transcribe the following audio file accurately{language_part}. '
        f'Provide only the transcribed text without any explanations or '
        f'additional commentary.'
      )

      # Create multimodal content
      content = [
        {
          'parts': [
            {'text': prompt},
            {
              'inline_data': {
                'mime_type': mime_type,
                'data': base64.b64encode(audio_data).decode('utf-8'),
              }
            },
          ]
        }
      ]

      # Set generation config for better transcription results
      generation_config = {
        'temperature': 0.0,  # Use lowest temperature for accurate transcription
        'top_p': 1.0,
        'top_k': 32,
      }

      # Generate content with the audio file
      response = model.generate_content(content, generation_config=generation_config)

      # Extract the transcription from the response
      if hasattr(response, 'text'):
        return response.text.strip()

      Logger.warn('Unexpected response format from Gemini API')
      return None

    except Exception as e:
      Logger.error('Error during Gemini transcription', e)
      return None

  def cleanup(self) -> None:
    """Clean up resources used by the Gemini transcriber.

    This is important to prevent gRPC shutdown timeout errors.
    """
    try:
      # Clean up any active gRPC channels in the genai library
      if hasattr(self, 'genai'):
        Logger.info('Cleaning up Gemini gRPC resources')

        # Minimal cleanup approach that should avoid dependency issues
        # Reset the configuration only - this should help release resources
        if hasattr(self.genai, 'configure'):
          try:
            # Set API key to None to help release resources
            self.genai.configure(api_key=None)
          except Exception as e:
            Logger.error(f'Error resetting Gemini configuration: {e}')
    except Exception as e:
      Logger.error(f'Error during Gemini cleanup: {e}')


class Transcriber:
  """Factory class that provides transcription services with appropriate handling."""

  def __init__(
    self,
    config: Optional[TranscriptionConfig] = None,
    service: Optional[str] = None,
  ):
    """Initialize the transcriber with the appropriate service.

    Args:
        config: Configuration object. If None, config will be loaded from environment.
        service: Transcription service to use. Overrides
            config.transcription_service if provided.
    """
    self.config = config or TranscriptionConfig.from_env()
    self._override_service(service)
    self.transcriber = self._create_transcriber()

  def _override_service(self, service: Optional[str]) -> None:
    """Override the service in the config if provided."""
    if service:
      self.config.transcription_service = service.lower()

  def _create_transcriber(self) -> BaseTranscriber:
    """Create the appropriate transcriber based on configuration."""
    if self.config.transcription_service == 'gemini' and self.config.gemini_api_key:
      Logger.info('Using Gemini API for transcription')
      return GeminiTranscriber(self.config)
    elif self.config.transcription_service == 'openai' and self.config.openai_api_key:
      Logger.info('Using OpenAI GPT-4o API for transcription')
      return OpenAITranscriber(self.config)
    else:
      # Default to OpenAI if no valid configuration is found
      Logger.warn(
        f"Invalid transcription service '{self.config.transcription_service}' "
        'or missing API key. Defaulting to OpenAI.'
      )
      return OpenAITranscriber(self.config)

  def transcribe(self, audio_file_path: str) -> Optional[str]:
    """Transcribe the audio file using the selected transcription service.

    Args:
        audio_file_path: Path to the audio file to transcribe

    Returns:
        The transcribed text, or None if transcription failed
    """
    # Validate file exists
    file_info = self._validate_file(audio_file_path)
    if not file_info:
      return None

    # Check if compression is needed
    audio_path = self._handle_file_size(audio_file_path, file_info)
    if not audio_path:
      return None

    # Perform transcription
    try:
      return self.transcriber.transcribe(audio_path)
    except Exception as e:
      Logger.error(
        f'Error transcribing audio with {self.config.transcription_service}: {e}'
      )
      return None
    finally:
      # Clean up temporary file if it's not the original
      if audio_path != audio_file_path:
        self._cleanup_temp_file(audio_path)

  def _validate_file(self, file_path: str) -> Optional[Tuple]:
    """Validate that the file exists and return its info."""
    file_info = TranscriptionConfig.get_file_info(file_path)
    if not file_info:
      Logger.error(f'Audio file not found at {file_path}')
      return None
    return file_info

  def _handle_file_size(self, audio_file_path: str, file_info: Tuple) -> Optional[str]:
    """Compress the file if it exceeds size limits."""
    file_size_bytes, _, _ = file_info
    file_size_mb = file_size_bytes / (1024 * 1024)

    # Check size limits based on service
    if self._exceeds_size_limit(file_size_mb):
      return self._compress_audio_file(audio_file_path, file_size_mb)

    return audio_file_path

  def _exceeds_size_limit(self, file_size_mb: float) -> bool:
    """Check if the file size exceeds the service limit."""
    if self.config.transcription_service == 'gemini' and file_size_mb > 19:
      return True
    if self.config.transcription_service == 'openai' and file_size_mb > 24:
      return True
    return False

  def _compress_audio_file(
    self, audio_file_path: str, file_size_mb: float
  ) -> Optional[str]:
    """Compress the audio file to meet size requirements."""
    max_size = 19 if self.config.transcription_service == 'gemini' else 24
    Logger.info(
      f'Audio file size ({file_size_mb:.2f} MB) exceeds API limit. Compressing...'
    )

    try:
      compressor = AudioCompressor()
      compressed_file = compressor.compress_audio(audio_file_path, max_size_mb=max_size)

      if compressed_file and os.path.exists(compressed_file):
        compressed_size = os.path.getsize(compressed_file) / (1024 * 1024)
        Logger.info(f'Using compressed audio file: {compressed_size:.2f} MB')
        return compressed_file
      else:
        Logger.error('Compression failed, using original file')
        return audio_file_path
    except Exception as e:
      Logger.error(f'Error compressing audio file: {e}')
      return audio_file_path

  def _cleanup_temp_file(self, file_path: str) -> None:
    """Clean up a temporary file."""
    if os.path.exists(file_path):
      try:
        os.unlink(file_path)
      except Exception as e:
        Logger.error(f'Error removing temporary compressed file: {e}')

  def cleanup(self) -> None:
    """Clean up resources used by the transcriber."""
    if hasattr(self, 'transcriber'):
      self.transcriber.cleanup()
