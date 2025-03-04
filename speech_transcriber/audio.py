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

    def start_recording(self) -> None:
        """Start recording audio from the microphone."""
        if self.is_recording:
            return

        self.frames = []
        self.is_recording = True

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
                self.stop_recording()
                break

            data = self.stream.read(CHUNK_SIZE, exception_on_overflow=False)
            self.frames.append(data)

    def stop_recording(self) -> Tuple[str, float]:
        """Stop recording and save the audio to a file."""
        if not self.is_recording:
            return "", 0.0

        self.is_recording = False

        # Wait for the recording thread to finish
        if self.recording_thread and self.recording_thread.is_alive():
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
