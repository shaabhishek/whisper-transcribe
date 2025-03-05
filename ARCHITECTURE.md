# Speech Transcriber Architecture

This document outlines the architecture of the Speech Transcriber application after refactoring for better decoupling and testability.

## Core Architecture

The application follows a modular design with clear separation of responsibilities:

```
                  ┌───────────────────┐
                  │ TranscriptionConfig│
                  └────────┬──────────┘
                           │
                           ▼
┌──────────────┐    ┌──────────────┐
│   Logger     │◄───│  Transcriber │
└──────────────┘    └───────┬──────┘
                            │
              ┌─────────────┴─────────────┐
              │                           │
              ▼                           ▼
    ┌─────────────────┐         ┌─────────────────┐
    │ OpenAITranscriber│         │GeminiTranscriber│
    └─────────────────┘         └─────────────────┘
```

## Key Components

### TranscriptionConfig

The `TranscriptionConfig` class centralizes all configuration parameters in a single data structure:

- API keys
- Service selection
- Audio parameters
- Model configurations

It also provides utility methods for file information and MIME type determination, which were previously duplicated.

### Logger

A simple logging utility that replaces scattered print statements throughout the code:

- Configurable (can be disabled during tests)
- Standard log levels (info, warn, error)
- Consistent formatting

### Transcriber

The factory class that selects and initializes the appropriate transcription service:

- Accepts a `TranscriptionConfig` instance or creates one from the environment
- Can override the service selection at instantiation time
- Forwards transcription requests to the selected service

### BaseTranscriber

An abstract base class defining the interface for all transcription services:

- Standardized initialization with configuration
- Common transcribe method signature

### Concrete Transcribers

Implementations for specific transcription services:

- **OpenAITranscriber**: Handles transcription with OpenAI's Whisper API
- **GeminiTranscriber**: Handles transcription with Google's Gemini API

## Design Benefits

1. **Reduced Coupling**: Components no longer depend directly on global variables.
2. **Improved Testability**: Configuration can be injected, making testing easier without patching globals.
3. **DRY Code**: Common functionality like file validation and MIME type detection is centralized.
4. **Consistent Error Handling**: Centralized logging improves error reporting consistency.
5. **Flexible Configuration**: Configuration can be created programmatically or loaded from the environment.

## Usage Examples

```python
# Using default configuration from environment
transcriber = Transcriber()
result = transcriber.transcribe("audio.wav")

# Using a custom configuration
config = TranscriptionConfig(
    openai_api_key="my_key",
    transcription_service="openai",
    language="es"
)
transcriber = Transcriber(config=config)
result = transcriber.transcribe("audio.wav")

# Forcing a specific service
transcriber = Transcriber(service="gemini")
result = transcriber.transcribe("audio.wav")
``` 