"""Audio recording functionality for the Speech Transcriber."""

import logging
import os
import tempfile
import threading
import time
from typing import Tuple
import wave

import pyaudio

from speech_transcriber.config import CHANNELS
from speech_transcriber.config import CHUNK_SIZE
from speech_transcriber.config import MAX_RECORDING_TIME
from speech_transcriber.config import SAMPLE_RATE


class AudioRecorder:
  """Records audio from the microphone and saves it to a file."""

  def __init__(self):
    """Initialize the audio recorder with default settings."""
    self.audio = pyaudio.PyAudio()
    self.stream = None
    self.frames = []
    self.is_recording = False
    self.recording_thread = None
    self.temp_file = None
    self._max_time_reached = False  # Flag to track if max recording time was reached

  def start_recording(self) -> None:
    """Start recording audio."""
    if self.is_recording:
      return

    self.is_recording = True
    self.frames = []
    self._max_time_reached = False  # Reset the flag

    # Create a temporary file for the recording
    self.temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)

    # List available input devices to help with debugging
    info = self.audio.get_host_api_info_by_index(0)
    num_devices = info.get('deviceCount')
    devices = []

    for i in range(num_devices):
      device_info = self.audio.get_device_info_by_host_api_device_index(0, i)
      if device_info.get('maxInputChannels') > 0:
        devices.append((i, device_info.get('name')))

    # Log available devices for debugging
    for device_id, name in devices:
      logging.info(f'Input device {device_id}: {name}')

    # Try to find default input device index
    try:
      default_input_device_index = self.audio.get_default_input_device_info()['index']
    except OSError:
      # If default device retrieval fails, use the first available input device
      default_input_device_index = devices[0][0] if devices else 0

    try:
      self.stream = self.audio.open(
        format=pyaudio.paInt16,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE,
        input_device_index=default_input_device_index,
      )

      # Start recording in a separate thread
      self.recording_thread = threading.Thread(target=self._record)
      self.recording_thread.start()

      logging.info('Recording started')
    except OSError as e:
      self.is_recording = False
      logging.error(f'Failed to start recording: {e}')
      raise

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
      return '', 0.0

    self.is_recording = False

    # Check if this was called from the recording thread (auto-stop case)
    called_from_recording_thread = threading.current_thread() is self.recording_thread

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

    # Safety check - if temp_file is None, create it now
    if self.temp_file is None:
      logging.warning('temp_file was None during stop_recording, creating a new one')
      self.temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)

    # Save the recording to the temporary file
    with wave.open(self.temp_file.name, 'wb') as wf:
      wf.setnchannels(CHANNELS)
      wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
      wf.setframerate(SAMPLE_RATE)
      wf.writeframes(b''.join(self.frames))

    return self.temp_file.name, duration

  def cleanup(self) -> None:
    """Clean up resources."""
    if self.stream:
      self.stream.close()

    self.audio.terminate()

    # Remove the temporary file if it exists
    if self.temp_file and os.path.exists(self.temp_file.name):
      os.unlink(self.temp_file.name)
