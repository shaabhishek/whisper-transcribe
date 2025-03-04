# Speech Transcriber

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A Python application that transcribes speech to text using OpenAI's Whisper API, activated by a custom keypress. This macOS-focused tool streamlines the transcription workflow by automatically copying the result to your clipboard.

## ✨ Features

- 🎹 Activate recording with a customizable key combination
- 🎤 Record audio directly from your microphone
- 🔄 Transcribe speech using OpenAI's powerful Whisper API
- 📋 Automatically paste transcribed text into the active text field
- 🔔 macOS native notifications for operation status
- 🧪 Comprehensive test suite

## 🔧 Requirements

- macOS (currently not supported on other platforms)
- Python 3.8+
- OpenAI API key
- Microphone
- PortAudio library (required for PyAudio)

## 📦 Installation

### Using pip

```bash
# Install from PyPI
pip install speech-transcriber

# Or install from source
git clone https://github.com/yourusername/speech-transcriber.git
cd speech-transcriber
pip install -e .
```

### Using uv (recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/speech-transcriber.git
cd speech-transcriber

# Install PortAudio (required for PyAudio)
brew install portaudio

# Install dependencies using uv
uv sync
source .venv/bin/activate
```

### Setting up your API Key

Set up your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY="your-api-key"
```

Or use the provided script:

```bash
./set_api_key.sh your-api-key
```

## 🚀 Usage

1. Run the application:
   ```bash
   speech-transcriber
   # Or if installed with -e:
   python -m speech_transcriber
   ```
2. Press the configured key combination (default: Command + Shift + ') to start recording
3. Speak clearly into your microphone
4. Press the same key combination again to stop recording and start transcription
5. The transcribed text will be automatically pasted into the active text field

## 🔒 macOS Permissions

This application requires accessibility permissions to monitor keyboard input. When you first run the application, you may need to:

1. Open System Preferences/Settings
2. Go to Security & Privacy (or Privacy & Security in newer versions)
3. Select the Privacy tab
4. Click on Accessibility in the left sidebar
5. Click the lock icon at the bottom and enter your password to make changes
6. Add Terminal (or your Python IDE) to the list of allowed applications

## ⚙️ Configuration

You can modify the following settings in the `config.py` file:

| Setting | Description | Default |
|---------|-------------|---------|
| `ACTIVATION_KEYS` | Key combination to activate recording | Command + Shift + ' |
| `WHISPER_MODEL` | OpenAI Whisper model to use | whisper-1 |
| `LANGUAGE` | Language code for transcription | en |
| `MAX_RECORDING_TIME` | Maximum recording time in seconds | 60 |

## 🧪 Testing

The application includes a comprehensive test suite that covers all core components:

```bash
# Run all tests
./run_tests.py

# Run a specific test module
python -m unittest tests.test_clipboard

# Run a specific test case
python -m unittest tests.test_clipboard.TestClipboard.test_copy_to_clipboard_success
```

The tests use mocking to avoid actual hardware access (microphone) and API calls, making them suitable for CI/CD environments.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone your fork
git clone https://github.com/yourusername/speech-transcriber.git
cd speech-transcriber

# Install development dependencies
pip install -e ".[dev]"

# Run tests
./run_tests.py
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/) for the Whisper API
- [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/) for audio recording capabilities
- [pynput](https://pynput.readthedocs.io/) for keyboard monitoring

## 🗺️ Roadmap

- [ ] Cross-platform support for Windows and Linux
- [ ] GUI interface
- [ ] Configurable settings via command-line arguments
- [ ] Support for additional transcription services
- [ ] Custom language model fine-tuning 