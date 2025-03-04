"""
Audio recording functionality for the Speech Transcriber.
"""

import os
import tempfile
import threading
import time
import wave
from typing import Tuple

import pyaudio

from speech_transcriber.config import (
    CHANNELS,
    CHUNK_SIZE,
    MAX_RECORDING_TIME,
    SAMPLE_RATE,
)


class AudioRecorder:
    """Records audio from the microphone and saves it to a file."""

    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.is_recording = False
        self.recording_thread = None
        self.temp_file = None
        self._max_time_reached = (
            False  # Flag to track if max recording time was reached
        )

    def start_recording(self) -> None:
        """Start recording audio from the microphone."""
        if self.is_recording:
            return

        self.frames = []
        self.is_recording = True
        self._max_time_reached = False  # Reset the flag

        # Create a temporary file for the recording
        self.temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)

        # Open the audio stream
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE,
        )

        # Start recording in a separate thread
        self.recording_thread = threading.Thread(target=self._record)
        self.recording_thread.start()

    def _record(self) -> None:
        """Record audio data in a loop until stopped."""
        start_time = time.time()

        while self.is_recording:
            if time.time() - start_time > MAX_RECORDING_TIME:
                # Just set the flag and break the loop instead of calling stop_recording
                # This avoids the thread trying to join itself
                self.is_recording = False
                # Signal that max time was reached (will be handled in stop_recording)
                self._max_time_reached = True
                break

            data = self.stream.read(CHUNK_SIZE, exception_on_overflow=False)
            self.frames.append(data)

    def stop_recording(self) -> Tuple[str, float]:
        """Stop recording and save the audio to a file."""
        if not self.is_recording:
            return "", 0.0

        self.is_recording = False

        # Check if this was called from the recording thread (auto-stop case)
        called_from_recording_thread = (
            threading.current_thread() is self.recording_thread
        )

        # Wait for the recording thread to finish, but only if not called from the recording thread
        if (
            self.recording_thread
            and self.recording_thread.is_alive()
            and not called_from_recording_thread
        ):
            self.recording_thread.join()

        # Stop and close the audio stream
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        # Calculate the duration of the recording
        duration = len(self.frames) * CHUNK_SIZE / SAMPLE_RATE

        # Save the recording to the temporary file
        with wave.open(self.temp_file.name, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(b"".join(self.frames))

        return self.temp_file.name, duration

    def cleanup(self) -> None:
        """Clean up resources."""
        if self.stream:
            self.stream.close()

        self.audio.terminate()

        # Remove the temporary file if it exists
        if self.temp_file and os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
