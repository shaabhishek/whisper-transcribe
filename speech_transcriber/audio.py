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

    self._initialize_recording()
    self._setup_temp_file()

    try:
      self._setup_audio_stream()
      self._start_recording_thread()
      logging.info('Recording started')
    except OSError as e:
      self._handle_recording_error(e)
      raise

  def _initialize_recording(self) -> None:
    """Initialize recording state."""
    self.is_recording = True
    self.frames = []
    self._max_time_reached = False

  def _setup_temp_file(self) -> None:
    """Create a temporary file for the recording."""
    self.temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)

  def _get_available_input_devices(self) -> list:
    """Get a list of available input devices."""
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

    return devices

  def _get_input_device_index(self, devices) -> int:
    """Get the index of the input device to use."""
    try:
      return self.audio.get_default_input_device_info()['index']
    except OSError:
      # If default device retrieval fails, use the first available input device
      return devices[0][0] if devices else 0

  def _setup_audio_stream(self) -> None:
    """Set up the audio stream for recording."""
    devices = self._get_available_input_devices()
    default_input_device_index = self._get_input_device_index(devices)

    self.stream = self.audio.open(
      format=pyaudio.paInt16,
      channels=CHANNELS,
      rate=SAMPLE_RATE,
      input=True,
      frames_per_buffer=CHUNK_SIZE,
      input_device_index=default_input_device_index,
    )

  def _start_recording_thread(self) -> None:
    """Start the recording thread."""
    self.recording_thread = threading.Thread(target=self._record)
    self.recording_thread.start()

  def _handle_recording_error(self, error) -> None:
    """Handle errors during recording setup."""
    self.is_recording = False
    logging.error(f'Failed to start recording: {error}')

  def _record(self) -> None:
    """Record audio data in a loop until stopped."""
    start_time = time.time()

    try:
      while self.is_recording:
        if time.time() - start_time > MAX_RECORDING_TIME:
          self._handle_max_time_reached()
          break

        data = self.stream.read(CHUNK_SIZE, exception_on_overflow=False)
        self.frames.append(data)
    except Exception as e:
      logging.error(f'Error during recording: {e}')
      self.is_recording = False

  def _handle_max_time_reached(self) -> None:
    """Handle when maximum recording time is reached."""
    self.is_recording = False
    self._max_time_reached = True

  def stop_recording(self) -> Tuple[str, float]:
    """Stop recording and save the audio to a file."""
    if not self.is_recording:
      return '', 0.0

    self.is_recording = False
    self._wait_for_recording_thread()
    self._close_audio_stream()

    # Calculate the duration of the recording
    duration = len(self.frames) * CHUNK_SIZE / SAMPLE_RATE

    # Ensure we have a temp file to write to
    self._ensure_temp_file_exists()
    self._save_audio_to_file()

    return self.temp_file.name, duration

  def _wait_for_recording_thread(self) -> None:
    """Wait for the recording thread to finish."""
    # Check if this was called from the recording thread (auto-stop case)
    called_from_recording_thread = threading.current_thread() is self.recording_thread

    # Wait for the recording thread to finish, but only if not called from the recording thread
    if (
      self.recording_thread
      and self.recording_thread.is_alive()
      and not called_from_recording_thread
    ):
      self.recording_thread.join()

  def _close_audio_stream(self) -> None:
    """Close the audio stream if it exists."""
    if self.stream:
      self.stream.stop_stream()
      self.stream.close()
      self.stream = None

  def _ensure_temp_file_exists(self) -> None:
    """Ensure that a temporary file exists for saving the recording."""
    if self.temp_file is None:
      logging.warning('temp_file was None during stop_recording, creating a new one')
      self.temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)

  def _save_audio_to_file(self) -> None:
    """Save the recorded audio frames to a WAV file."""
    with wave.open(self.temp_file.name, 'wb') as wf:
      wf.setnchannels(CHANNELS)
      wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
      wf.setframerate(SAMPLE_RATE)
      wf.writeframes(b''.join(self.frames))

  def cleanup(self) -> None:
    """Clean up resources."""
    if self.stream:
      self.stream.close()

    self.audio.terminate()

    # Remove the temporary file if it exists
    if self.temp_file and os.path.exists(self.temp_file.name):
      os.unlink(self.temp_file.name)
