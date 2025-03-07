"""Clipboard operations for the Speech Transcriber."""

import pyperclip


def copy_to_clipboard(text: str) -> bool:
  """Copy text to the clipboard.

  Args:
      text: The text to copy to the clipboard

  Returns:
      True if successful, False otherwise
  """
  try:
    pyperclip.copy(text)
    return True
  except Exception as e:
    print(f'Error copying to clipboard: {e}')
    return False


def paste_from_clipboard() -> str:
  """Get text from the clipboard.

  Returns:
      The text from the clipboard, or an empty string if failed
  """
  try:
    return pyperclip.paste()
  except Exception as e:
    print(f'Error pasting from clipboard: {e}')
    return ''
