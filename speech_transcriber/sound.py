"""Sound module for playing notification sounds."""

import os
import subprocess
import time

try:
  # Try to import PyObjC for native macOS sound playback
  from AppKit import NSSound

  HAVE_PYOBJC = True
except ImportError:
  HAVE_PYOBJC = False


def play_sound(sound_path: str) -> bool:
  """Play a system sound on macOS.

  Args:
      sound_path: Path to the sound file to play.

  Returns:
      True if the sound was played successfully, False otherwise.
  """
  try:
    # Check if the sound file exists
    if not os.path.exists(sound_path):
      print(f'Sound file not found: {sound_path}')
      return False

    if HAVE_PYOBJC:
      # Use NSSound for native macOS sound playback
      ns_sound = NSSound.alloc().initWithContentsOfFile_byReference_(
        sound_path, True
      )
      if ns_sound:
        ns_sound.play()
        # Wait for the sound to start playing
        time.sleep(0.1)
        return True
      return False
    else:
      # Fallback to afplay command
      subprocess.run(
        ['afplay', sound_path],
        check=True,
        capture_output=True,
      )
      return True
  except Exception as e:
    print(f'Error playing sound: {e}')
    return False


def play_start_sound() -> bool:
  """Play a sound to indicate recording has started.

  Uses a sound similar to Mac dictation start sound.

  Returns:
      True if the sound was played successfully, False otherwise.
  """
  # Use the "Hero" sound which is similar to dictation start
  return play_sound('/System/Library/Sounds/Hero.aiff')


def play_stop_sound() -> bool:
  """Play a sound to indicate recording has stopped.

  Uses a sound similar to Mac dictation stop sound.

  Returns:
      True if the sound was played successfully, False otherwise.
  """
  # Use the "Submarine" sound which is similar to dictation stop
  return play_sound('/System/Library/Sounds/Submarine.aiff')
