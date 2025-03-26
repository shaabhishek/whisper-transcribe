# Speech Transcriber

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A Python application that transcribes speech to text using OpenAI's GPT-4o-transcribe API or Google's Gemini API, activated by a custom keypress. This macOS-focused tool streamlines the transcription workflow by automatically copying the result to your clipboard.

## ✨ Features

- 🎹 Activate recording with a customizable key combination
- 🎤 Record audio directly from your microphone
- 🔄 Transcribe speech using OpenAI's GPT-4o-transcribe API or Google's Gemini API
- 📋 Automatically paste transcribed text into the active text field
- 🔔 macOS native notifications for operation status
- 🧪 Comprehensive test suite
- 🔄 Audio compression for handling large recordings (requires ffmpeg)

## 🔧 Requirements

- macOS (currently not supported on other platforms)
- Python 3.8+
- OpenAI API key
- Google Gemini API key
- Microphone
- PortAudio library (required for PyAudio)
- ffmpeg (for audio compression)

## 📦 Installation

### Using pip

```bash
# Install from source
git clone https://github.com/shaabhishek/whisper-transcribe.git
cd whisper-transcribe
pip install -e .
```

### Using uv (recommended)

```bash
# Clone the repository
git clone https://github.com/shaabhishek/whisper-transcribe.git
cd whisper-transcribe

# Install PortAudio (required for PyAudio)
brew install portaudio

# Install ffmpeg (required for audio compression)
brew install ffmpeg

# Install dependencies using uv
uv sync
source .venv/bin/activate
```

### Setting up your API Key

You can set up API keys in several ways. The application supports both OpenAI and Google Gemini APIs for transcription.

1. **Using a .env file (recommended):**
   
   Copy the example environment file and add your API key:
   ```bash
   cp .env.example .env
   ```
   
   Then edit the `.env` file and add your preferred API key:
   ```
   # Choose either OpenAI or Gemini
   OPENAI_API_KEY=your_openai_api_key
   GEMINI_API_KEY=your_gemini_api_key
   
   # Select which service to use (options: "openai" or "gemini")
   TRANSCRIPTION_SERVICE=openai
   ```

2. **Using environment variables:**
   
   Set up your API keys as environment variables:
   ```bash
   # For OpenAI
   export OPENAI_API_KEY="your-openai-api-key"
   export TRANSCRIPTION_SERVICE="openai"
   
   # OR for Gemini
   export GEMINI_API_KEY="your-gemini-api-key"
   export TRANSCRIPTION_SERVICE="gemini"
   ```

3. **Using the provided script:**

```bash
# For OpenAI
./set_api_key.sh openai your-openai-api-key

# OR for Gemini
./set_api_key.sh gemini your-gemini-api-key
```

## 🚀 Usage

1. Run the application:
   ```bash
   speech-transcriber
   ```

2. Or specify a transcription service:
   ```bash
   # Use OpenAI GPT-4o-transcribe API
   speech-transcriber --service openai
   
   # Use Google Gemini API
   speech-transcriber --service gemini
   
   # View all available options
   speech-transcriber --help
   ```

3. Double-press the Ctrl key to start recording.
4. Speak clearly into your microphone
5. Double-press the Ctrl key again to stop recording and start transcription
6. The transcribed text will be automatically pasted into the active text field

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
| `DOUBLE_PRESS_INTERVAL` | Maximum time between Alt key presses to detect as double-press (seconds) | 0.5 |
| `TRANSCRIPTION_SERVICE` | Which API to use for transcription | openai |
| `OPENAI_MODEL` | OpenAI model to use | gpt-4o-transcribe |
| `GEMINI_MODEL` | Google Gemini model to use | gemini-pro-vision |
| `LANGUAGE` | Language code for transcription | en |
| `MAX_RECORDING_TIME` | Maximum recording time in seconds | 120 |

### 🔊 Audio Quality Settings

The following audio configuration options can be modified in `config.py` to adjust recording quality:

| Setting | Description | Default | Notes |
|---------|-------------|---------|-------|
| `SAMPLE_RATE` | Audio sampling rate in Hz | 16000 | Matched to GPT-4o's optimal rate[¹](#references). Higher values (e.g., 44100, 48000) can provide more audio detail but increase file size. |
| `CHANNELS` | Number of audio channels | 1 (Mono) | Mono is recommended for speech recognition[²](#references). |
| `CHUNK_SIZE` | Frames per buffer | 1024 | Lower values reduce latency but may cause performance issues. Typical values: 512, 1024, 2048[³](#references). |
| `FORMAT` | Audio format | wav | WAV format provides lossless quality for transcription. |

#### Optimizing Audio for Transcription

For the best transcription results, consider these audio optimization tips:

1. **Sample Rate Considerations**: 
   - The default is 16000 Hz (GPT-4o's optimal rate)[¹](#references)
   - Higher sample rates (e.g., 44100 Hz - CD quality) provide more detail but increase file size and processing time
   - GPT-4o models were trained on 16000 Hz audio, so this rate is optimal for accuracy

2. **Background Noise Reduction**[⁸](#references):
   - Record in a quiet environment when possible
   - Position the microphone closer to the speaker
   - Consider using a directional microphone for noisy environments

3. **Speech Clarity**[⁹](#references):
   - Speak at a moderate pace with clear articulation
   - Avoid overlapping speech when possible
   - Maintain consistent volume throughout recording

4. **Hardware Recommendations**[¹⁰](#references):
   - External microphones typically provide better quality than built-in laptop/device microphones
   - USB condenser microphones are good affordable options for clear speech capture
   - Headset microphones can help maintain consistent distance from the sound source

### 🔍 Transcription API Features

This application supports two transcription services:

#### OpenAI GPT-4o-transcribe API

OpenAI's GPT-4o-transcribe API offers several configuration options that affect transcription quality and behavior:

| Setting | Description | Default | Available Options |
|---------|-------------|---------|-------------------|
| `OPENAI_MODEL` | OpenAI model to use | gpt-4o-transcribe | • `gpt-4o-transcribe`: Standard API model<br>• OpenAI also offers more advanced models which may be accessible through their API[⁴](#references) |
| `LANGUAGE` | Language code for transcription | en | Any [ISO 639-1 language code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) (e.g., 'en', 'fr', 'de', 'es', 'ja'). Leave empty for auto-detection[⁵](#references). |

#### Google Gemini API

Google's Gemini API provides an alternative for transcription:

| Setting | Description | Default | Notes |
|---------|-------------|---------|-------|
| `GEMINI_MODEL` | Gemini model to use | gemini-pro-vision | Used for processing audio content |
| `LANGUAGE` | Language code for transcription | en | Any [ISO 639-1 language code](https://en.wikipedia.org/wiki/List_of_ISO_639-1_codes) to specify the language in the transcription prompt |

#### Choosing an API

Both APIs provide excellent transcription capabilities, but there are some considerations:

- **OpenAI GPT-4o-transcribe**: Specifically designed for speech-to-text with high accuracy
- **Google Gemini**: More general-purpose AI with multimodal capabilities, which can handle audio transcription

To select which API to use, set the `TRANSCRIPTION_SERVICE` value in your `.env` file or environment variables to either `"openai"` or `"gemini"`.

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
git clone https://github.com/shaabhishek/whisper-transcribe.git
cd whisper-transcribe

# Install development dependencies
pip install -e ".[dev]"

# Run tests
./run_tests.py
```

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAI](https://openai.com/) for the GPT-4o-transcribe API
- [Google](https://cloud.google.com/) for the Gemini API
- [PyAudio](https://people.csail.mit.edu/hubert/pyaudio/) for audio recording capabilities
- [pynput](https://pynput.readthedocs.io/) for keyboard monitoring

## 🗺️ Roadmap

- [ ] Cross-platform support for Windows and Linux
- [ ] GUI interface
- [ ] Configurable settings via command-line arguments
- [ ] Support for additional transcription services
- [ ] Custom language model fine-tuning 

## References

1. <a name="references"></a> OpenAI Documentation: [Audio Preprocessing](https://platform.openai.com/docs/guides/speech-to-text) - The 16000 Hz sample rate for audio processing.
2. PyAudio Documentation: [Channel Configuration](https://people.csail.mit.edu/hubert/pyaudio/docs/#pyaudio.Stream) - PyAudio stream configuration for audio channels.
3. PyAudio Documentation: [Chunk Size Parameters](https://people.csail.mit.edu/hubert/pyaudio/docs/#pyaudio.Stream) - PyAudio documentation for frame buffer sizes.
4. OpenAI API Documentation: [Speech to Text](https://platform.openai.com/docs/guides/speech-to-text) - Official OpenAI API documentation for GPT-4o-transcribe.
5. OpenAI API Documentation: [Speech to Text](https://platform.openai.com/docs/guides/speech-to-text) - Official OpenAI API documentation for transcription.
6. OpenAI Research: [GPT-4o models](https://openai.com/research/) - Research on OpenAI's latest models and audio processing.
7. OpenAI Documentation: [Model Performance and Limitations](https://platform.openai.com/docs/models/) - Official notes on language-specific performance.
8. Microsoft Research: [Automatic Speech Recognition - Best Practices](https://www.microsoft.com/en-us/research/publication/automatic-speech-recognition-on-mobile-devices-and-over-communication-networks/) - Research on ASR performance in varying noise conditions.
9. Google Cloud Documentation: [Speech-to-Text Best Practices](https://cloud.google.com/speech-to-text/docs/best-practices) - Recommendations for speech recognition clarity.
10. Audio Engineering Society: [Microphone Selection Guide](https://www.aes.org/e-lib/browse.cfm?elib=15814) - Professional recommendations for speech recording equipment. 