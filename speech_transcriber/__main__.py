"""Main entry point for the Speech Transcriber application."""

import argparse
import os
import signal
import sys
import time

from speech_transcriber.audio import AudioRecorder
from speech_transcriber.clipboard import copy_to_clipboard
from speech_transcriber.config import GEMINI_API_KEY
from speech_transcriber.config import OPENAI_API_KEY
from speech_transcriber.keyboard_listener import KeyboardListener
from speech_transcriber.notification import show_notification
from speech_transcriber.sound import play_start_sound
from speech_transcriber.sound import play_stop_sound
from speech_transcriber.transcription import Transcriber


class SpeechTranscriber:
  """Main application class for the Speech Transcriber."""

  def __init__(self, service=None):
    """Initialize the Speech Transcriber application with required components."""
    self.audio_recorder = AudioRecorder()
    self.transcriber = Transcriber(service=service)
    self.keyboard_listener = KeyboardListener(
      on_activate=self.start_recording,
      on_deactivate=self.stop_recording_and_transcribe,
    )
    self.running = False
    self._cleanup_in_progress = False

  def start(self) -> None:
    """Start the application."""
    # Check API keys based on selected service
    service = self.transcriber.config.transcription_service

    if service == 'openai' and not OPENAI_API_KEY:
      print(
        'Error: OpenAI API key not set. Please set the '
        'OPENAI_API_KEY environment variable.'
      )
      sys.exit(1)

    if service == 'gemini' and not GEMINI_API_KEY:
      print(
        'Error: Gemini API key not set. Please set the '
        'GEMINI_API_KEY environment variable.'
      )
      sys.exit(1)

    self.running = True

    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, self.handle_signal)
    signal.signal(signal.SIGTERM, self.handle_signal)

    # Start the keyboard listener
    self.keyboard_listener.start()

    print('Speech Transcriber is running.')
    print(f'Using {service.upper()} as the transcription service.')
    print('Double-press either the left or right Alt key to start recording.')
    print('Double-press either Alt key again to stop recording and transcribe.')
    print('Press Ctrl+C to exit.')

    # Keep the main thread alive
    try:
      while self.running:
        time.sleep(0.1)
    except KeyboardInterrupt:
      self.stop()

  def stop(self) -> None:
    """Stop the application."""
    # Prevent multiple cleanup attempts
    if self._cleanup_in_progress:
      return

    self._cleanup_in_progress = True
    self.running = False

    # First stop the listeners
    try:
      self.keyboard_listener.stop()
    except Exception as e:
      print(f'Error stopping keyboard listener: {e}')

    # Suppress all logging during shutdown to avoid errors
    os.environ['ABSL_LOGGING_VERBOSITY'] = '0'
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

    # Redirect stderr temporarily to suppress unwanted messages
    original_stderr = sys.stderr
    try:
      # Create a no-op stream that discards writes
      class NullWriter:
        def write(self, s):
          pass

        def flush(self):
          pass

      sys.stderr = NullWriter()

      # Clean up transcriber first
      if hasattr(self, 'transcriber'):
        try:
          self.transcriber.cleanup()
        except Exception:
          # Just continue if there's an error
          pass

      # Restore stderr
      sys.stderr = original_stderr
    except Exception as e:
      # Ensure stderr is restored even if an error occurs
      sys.stderr = original_stderr
      # Log that we caught an error during cleanup but don't disrupt shutdown
      print(f'Error during stderr redirection cleanup: {e}')

    # Then clean up audio recorder
    try:
      self.audio_recorder.cleanup()
    except Exception:
      pass

    print('\nSpeech Transcriber stopped.')

  def handle_signal(self, signum: int, frame) -> None:
    """Handle termination signals."""
    print('\nShutting down Speech Transcriber...')
    # Important: call stop() to clean up resources before exiting
    self.stop()

    # Force a quick exit - don't let any lingering tasks delay shutdown
    os._exit(0)

  def start_recording(self) -> None:
    """Start recording audio."""
    show_notification('Speech Transcriber', 'Recording started...')
    play_start_sound()
    print('Recording... (press hotkey again to stop)')
    self.audio_recorder.start_recording()

  def stop_recording_and_transcribe(self) -> None:
    """Stop recording and transcribe the audio."""
    print('Recording stopped. Transcribing...')
    show_notification('Speech Transcriber', 'Transcribing...')
    play_stop_sound()

    # Stop recording and get the audio file path
    audio_file_path, duration = self.audio_recorder.stop_recording()

    if not audio_file_path or duration < 0.5:
      print('Recording too short or failed.')
      show_notification('Speech Transcriber', 'Recording too short or failed.')
      return

    # Transcribe the audio
    transcribed_text = self.transcriber.transcribe(audio_file_path)

    if not transcribed_text:
      print('Transcription failed.')
      show_notification('Speech Transcriber', 'Transcription failed.')
      return

    # Copy the transcribed text to the clipboard
    if copy_to_clipboard(transcribed_text):
      print(f'Transcribed ({duration:.1f}s): {transcribed_text}')
      show_notification(
        'Transcription Complete',
        f'Text copied to clipboard ({len(transcribed_text)} chars)',
      )
    else:
      print(f'Transcribed but failed to copy: {transcribed_text}')
      show_notification('Transcription Complete', 'Failed to copy to clipboard')


def main() -> None:
  """Main entry point for the application."""
  # Parse command line arguments
  parser = argparse.ArgumentParser(
    description='Speech Transcriber - Convert audio to text using AI services',
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
  )

  parser.add_argument(
    '--service',
    '-s',
    choices=['openai', 'gemini'],
    default=None,
    help='Transcription service to use (overrides environment variable setting)',
  )

  parser.add_argument(
    '--list-services',
    action='store_true',
    help='List available transcription services and exit',
  )

  args = parser.parse_args()

  if args.list_services:
    print('Available transcription services:')
    print(
      '  - openai: OpenAI Whisper API (requires OPENAI_API_KEY environment variable)'
    )
    print(
      '  - gemini: Google Gemini API (requires GEMINI_API_KEY environment variable)'
    )
    sys.exit(0)

  app = SpeechTranscriber(service=args.service)
  app.start()


if __name__ == '__main__':
  main()
