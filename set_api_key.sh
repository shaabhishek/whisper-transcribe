#!/bin/bash

# Check if an API key was provided
if [ $# -ne 1 ]; then
  echo "Usage: $0 <your-openai-api-key>"
  echo "Example: $0 sk-abcdefghijklmnopqrstuvwxyz123456"
  exit 1
fi

# Set the API key as an environment variable
export OPENAI_API_KEY="$1"

# Print confirmation
echo "OpenAI API key set successfully!"
echo "You can now run the application with: python -m speech_transcriber"

# Run the application if requested
read -p "Do you want to run the application now? (y/n): " run_app
if [[ $run_app == "y" || $run_app == "Y" ]]; then
  python -m speech_transcriber
fi 

