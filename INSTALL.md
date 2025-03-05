# Installation and Usage Guide

## Prerequisites

- macOS
- Python 3.8 or higher
- OpenAI API key
- Working microphone
- PortAudio library (required for PyAudio)

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd speech-transcriber
```

### 2. Install PortAudio

PyAudio requires the PortAudio library to be installed on your system.

```bash
brew install portaudio
```

### 3. Install dependencies

#### Using `uv` (recommended)

```bash
uv sync
source .venv/bin/activate
```

#### Using pip

```bash
pip install -e .
```

### 4. Set up your OpenAI API key

You have several options to set up your OpenAI API key:

#### Option 1: Using a .env file (recommended)

The application includes a .env file for convenient API key storage:

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your favorite editor
nano .env  # or vim, or any text editor
```

Then add your OpenAI API key to the .env file:
```
OPENAI_API_KEY=your_openai_api_key_here
```

The application will automatically detect and use this key when it starts.

#### Option 2: Using environment variables

You can set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY="your-api-key"
```

For permanent setup, add the export command to your shell profile file (e.g., `.bashrc`, `.zshrc`).

#### Option 3: Using the provided script

```bash
chmod +x set_api_key.sh  # Make the script executable (first time only)
./set_api_key.sh your-api-key
```

## macOS Permissions

This application requires accessibility permissions to monitor keyboard input. When you first run the application, you may need to:

1. Open System Preferences/Settings
2. Go to Security & Privacy (or Privacy & Security in newer versions)
3. Select the Privacy tab
4. Click on Accessibility in the left sidebar
5. Click the lock icon at the bottom and enter your password to make changes
6. Add Terminal (or your Python IDE) to the list of allowed applications

## Usage

### Running the application

```bash
speech-transcriber
```

Or:

```bash
python -m speech_transcriber
```

### Using the application

1. The application will run in the background, waiting for the activation keypress.
2. **Double-press** either the left or right **Alt key** to start recording.
3. Speak clearly into your microphone.
4. **Double-press** either **Alt key** again to stop recording and start transcription.
5. The transcribed text will be automatically copied to your clipboard.
6. Paste the text into any text field using Cmd+V.
7. Audio notifications will play when recording starts and stops.

### Customization

You can customize the application by modifying the `config.py` file:

- Adjust the double-press interval (default: 0.5 seconds)
- Adjust audio recording parameters
- Change the Whisper API model
- Enable/disable notifications

## Troubleshooting

### Common issues:

1. **API key not recognized**: Make sure your OpenAI API key is correctly set as an environment variable.

2. **Audio recording issues**: Ensure your microphone is properly connected and working. Try adjusting the audio parameters in `config.py`.

3. **Keypress not detected**: This is likely due to missing accessibility permissions. See the "macOS Permissions" section above.

4. **PyAudio installation issues**: If you're still having issues with PyAudio after installing PortAudio, you might need to specify the path to PortAudio:
   ```bash
   CFLAGS="-I/opt/homebrew/include" LDFLAGS="-L/opt/homebrew/lib" pip install pyaudio
   ```

5. **Clipboard issues**: If text isn't being pasted correctly, try manually copying and pasting the transcribed text shown in the console output.

## Testing

### Running the Tests

The application includes a comprehensive test suite that covers all core components:

```bash
# Run all tests
./run_tests.py

# Run a specific test module
python -m unittest tests.test_clipboard

# Run a specific test case
python -m unittest tests.test_clipboard.TestClipboard.test_copy_to_clipboard_success
```

### Test Coverage

The tests cover the following components:

1. **Audio Recording**: Tests for recording, stopping, and saving audio
2. **Transcription**: Tests for sending audio to the Whisper API and processing the response
3. **Keyboard Listener**: Tests for detecting key combinations
4. **Clipboard Operations**: Tests for copying and pasting text
5. **Notifications**: Tests for displaying notifications on different platforms
6. **Main Application**: Tests for the overall application flow

The tests use mocking to avoid actual hardware access (microphone) and API calls, making them suitable for CI/CD environments. 