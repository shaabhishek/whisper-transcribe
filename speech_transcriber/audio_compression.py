"""Audio compression functionality for the Speech Transcriber."""

import logging
import os
import shutil
import subprocess
import tempfile
from typing import Optional


class AudioCompressor:
  """Compresses audio files to reduce size."""

  def __init__(self):
    """Initialize the audio compressor."""
    self._check_ffmpeg_available()

  def _check_ffmpeg_available(self) -> None:
    """Check if ffmpeg is installed and available."""
    if shutil.which('ffmpeg') is None:
      logging.warning('ffmpeg not found in PATH. Audio compression will not work.')
      self.ffmpeg_available = False
    else:
      self.ffmpeg_available = True

  def compress_audio(self, input_file: str, max_size_mb: int = 19) -> Optional[str]:
    """Compress the audio file to reduce its size below the limit.

    Args:
        input_file: Path to the input audio file
        max_size_mb: Maximum target size in MB

    Returns:
        Path to the compressed audio file or None if compression failed
    """
    if not self.ffmpeg_available:
      logging.error('Cannot compress audio: ffmpeg not available')
      return None

    if not os.path.exists(input_file):
      logging.error(f'Input file does not exist: {input_file}')
      return None

    # Create a temporary file for the compressed audio
    compressed_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
    compressed_file.close()

    try:
      # Calculate appropriate bitrate based on file size
      bitrate = self._calculate_bitrate(input_file, max_size_mb)

      # Log compression details
      input_size_mb = os.path.getsize(input_file) / (1024 * 1024)
      logging.info(
        f'Compressing audio file from {input_size_mb:.2f}MB to target {max_size_mb}MB using {bitrate}k bitrate'
      )

      # Run ffmpeg to compress the audio
      result = self._run_ffmpeg(input_file, compressed_file.name, bitrate)

      # Verify compression succeeded
      if (
        not os.path.exists(compressed_file.name)
        or os.path.getsize(compressed_file.name) == 0
      ):
        logging.error('Compression failed: output file is empty or does not exist')
        return None

      compressed_size_mb = os.path.getsize(compressed_file.name) / (1024 * 1024)
      logging.info(f'Compressed audio file to {compressed_size_mb:.2f}MB')

      return compressed_file.name
    except Exception as e:
      self._handle_compression_error(e, compressed_file.name)
      return None

  def _calculate_bitrate(self, input_file: str, max_size_mb: int) -> int:
    """Calculate an appropriate bitrate for the compressed file."""
    input_size_mb = os.path.getsize(input_file) / (1024 * 1024)

    # Calculate a bitrate that will result in a file under the max size
    # Assuming compression ratio of ~10x for WAV to MP3 conversion
    estimated_bitrate = int((max_size_mb * 8 * 1024) / (input_size_mb / 10))

    # Clamp the bitrate to reasonable values
    return max(16, min(128, estimated_bitrate))

  def _run_ffmpeg(
    self, input_file: str, output_file: str, bitrate: int
  ) -> subprocess.CompletedProcess:
    """Run ffmpeg to compress the audio file."""
    return subprocess.run(
      [
        'ffmpeg',
        '-i',
        input_file,
        '-b:a',
        f'{bitrate}k',
        '-ac',
        '1',  # Convert to mono
        '-y',  # Overwrite existing file
        output_file,
      ],
      capture_output=True,
      text=True,
      check=True,
    )

  def _handle_compression_error(self, error: Exception, temp_file: str) -> None:
    """Handle errors during compression and clean up."""
    if isinstance(error, subprocess.CalledProcessError):
      logging.error(f'Error compressing audio file: {error.stderr}')
    else:
      logging.error(f'Error compressing audio file: {error}')

    # Clean up temporary file if it exists
    if os.path.exists(temp_file):
      try:
        os.unlink(temp_file)
      except Exception as e:
        logging.error(f'Failed to clean up temporary file: {e}')
