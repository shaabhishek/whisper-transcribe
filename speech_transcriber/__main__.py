"""
Main entry point for the Speech Transcriber application.
"""

import signal
import sys
import time

from speech_transcriber.audio import AudioRecorder
from speech_transcriber.clipboard import copy_to_clipboard
from speech_transcriber.config import OPENAI_API_KEY
from speech_transcriber.keyboard_listener import KeyboardListener
from speech_transcriber.notification import show_notification
from speech_transcriber.sound import play_start_sound, play_stop_sound
from speech_transcriber.transcription import Transcriber


class SpeechTranscriber:
    """Main application class for the Speech Transcriber."""

    def __init__(self):
        self.audio_recorder = AudioRecorder()
        self.transcriber = Transcriber()
        self.keyboard_listener = KeyboardListener(
            on_activate=self.start_recording,
            on_deactivate=self.stop_recording_and_transcribe,
        )
        self.running = False

    def start(self) -> None:
        """Start the application."""
        if not OPENAI_API_KEY:
            print(
                "Error: OpenAI API key not set. Please set the OPENAI_API_KEY environment variable."
            )
            sys.exit(1)

        self.running = True

        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)

        # Start the keyboard listener
        self.keyboard_listener.start()

        print("Speech Transcriber is running.")
        print("Double-press either the left or right Alt key to start recording.")
        print("Double-press either Alt key again to stop recording and transcribe.")
        print("Press Ctrl+C to exit.")

        # Keep the main thread alive
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        """Stop the application."""
        self.running = False
        self.keyboard_listener.stop()
        self.audio_recorder.cleanup()
        print("\nSpeech Transcriber stopped.")

    def handle_signal(self, signum: int, frame) -> None:
        """Handle termination signals."""
        self.stop()
        sys.exit(0)

    def start_recording(self) -> None:
        """Start recording audio."""
        show_notification("Speech Transcriber", "Recording started...")
        play_start_sound()
        print("Recording... (press hotkey again to stop)")
        self.audio_recorder.start_recording()

    def stop_recording_and_transcribe(self) -> None:
        """Stop recording and transcribe the audio."""
        print("Recording stopped. Transcribing...")
        show_notification("Speech Transcriber", "Transcribing...")
        play_stop_sound()

        # Stop recording and get the audio file path
        audio_file_path, duration = self.audio_recorder.stop_recording()

        if not audio_file_path or duration < 0.5:
            print("Recording too short or failed.")
            show_notification("Speech Transcriber", "Recording too short or failed.")
            return

        # Transcribe the audio
        transcribed_text = self.transcriber.transcribe(audio_file_path)

        if not transcribed_text:
            print("Transcription failed.")
            show_notification("Speech Transcriber", "Transcription failed.")
            return

        # Copy the transcribed text to the clipboard
        if copy_to_clipboard(transcribed_text):
            print(f"Transcribed ({duration:.1f}s): {transcribed_text}")
            show_notification(
                "Transcription Complete",
                f"Text copied to clipboard ({len(transcribed_text)} chars)",
            )
        else:
            print(f"Transcribed but failed to copy: {transcribed_text}")
            show_notification("Transcription Complete", "Failed to copy to clipboard")


def main() -> None:
    """Main entry point for the application."""
    app = SpeechTranscriber()
    app.start()


if __name__ == "__main__":
    main()
