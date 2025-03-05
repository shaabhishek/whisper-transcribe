#!/bin/bash

# Check if correct parameters were provided
if [ $# -ne 2 ]; then
  echo "Usage: $0 <service> <api-key>"
  echo "Where <service> is either 'openai' or 'gemini'"
  echo "Example for OpenAI: $0 openai sk-abcdefghijklmnopqrstuvwxyz123456"
  echo "Example for Gemini: $0 gemini AIzaSyAbCdEfGhIjKlMnOpQrStUvWxYz123456"
  exit 1
fi

# Get the service and API key
SERVICE=$(echo "$1" | tr '[:upper:]' '[:lower:]')
API_KEY="$2"

# Validate the service
if [[ "$SERVICE" != "openai" && "$SERVICE" != "gemini" ]]; then
  echo "Error: Service must be either 'openai' or 'gemini'."
  echo "Usage: $0 <service> <api-key>"
  exit 1
fi

# Set the API key and service as environment variables
if [ "$SERVICE" == "openai" ]; then
  export OPENAI_API_KEY="$API_KEY"
  export TRANSCRIPTION_SERVICE="openai"
  ENV_VAR="OPENAI_API_KEY"
else
  export GEMINI_API_KEY="$API_KEY"
  export TRANSCRIPTION_SERVICE="gemini"
  ENV_VAR="GEMINI_API_KEY"
fi

# Print confirmation
echo "$SERVICE API key set successfully!"
echo "Environment variable $ENV_VAR is now configured."
echo "Transcription service set to: $TRANSCRIPTION_SERVICE"
echo "You can now run the application with: python -m speech_transcriber"

# Run the application if requested
read -p "Do you want to run the application now? (y/n): " run_app
if [[ $run_app == "y" || $run_app == "Y" ]]; then
  python -m speech_transcriber
fi 

