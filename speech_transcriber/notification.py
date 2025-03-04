"""
Notification functionality for the Speech Transcriber.
"""

import subprocess

from speech_transcriber.config import NOTIFICATION_ENABLED


def show_notification(title: str, message: str) -> None:
    """
    Show a notification to the user on macOS.

    Args:
        title: The notification title
        message: The notification message
    """
    if not NOTIFICATION_ENABLED:
        return

    try:
        _show_macos_notification(title, message)
    except Exception as e:
        print(f"Error showing notification: {e}")
        print(f"{title}: {message}")


def _show_macos_notification(title: str, message: str) -> None:
    """Show a notification on macOS."""
    script = f'''
  osascript -e 'display notification "{message}" with title "{title}"'
  '''
    subprocess.run(script, shell=True)
