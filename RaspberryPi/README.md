# PiChat: Smart Speaker for Raspberry Pi

PiChat is a voice-controlled AI assistant for Raspberry Pi that connects to Azure services for speech recognition, text-to-speech, and intelligent responses through Azure IoT Hub and OpenAI.

## Features

- Voice activation with configurable wake word ("Hey Iris" by default)
- Natural speech recognition using Azure Cognitive Services
- High-quality text-to-speech with Azure's neural voices
- Intelligent responses powered by OpenAI's GPT models via Azure IoT Hub
- Conversation memory with context preservation
- Configuration via simple JSON file

## Prerequisites

- Raspberry Pi with microphone and speaker
- Azure account with the following services:
  - Azure Cognitive Services (Speech Services)
  - Azure IoT Hub
  - Azure OpenAI or other backend service
- Python 3.7+ installed on your Raspberry Pi

## Installation

1. Clone this repository to your Raspberry Pi:
   ```bash
   git clone https://github.com/yourusername/pichat.git
   cd pichat
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the configuration template and edit with your keys:
   ```bash
   cp config.json.template config.json
   nano config.json
   ```

4. Update the configuration with your Azure service credentials.

## Configuration

The `config.json` file contains all the necessary settings:

```json
{
    "AzureCognitiveServices": {
        "Key": "your-speech-services-key",
        "Region": "uksouth",
        "SpeechRecognitionLanguage": "en-US",
        "SpeechSynthesisVoiceName": "en-US-JennyNeural",
        "WakePhraseModel": "keyword_model.table",
        "WakeWord": "Hey Iris",
        "StopWord": "Stop conversation"
    },
    "AzureIoTHub": {
        "ConnectionString": "your-iot-hub-connection-string"
    },
    "AzureOpenAI": {
        "Key": "your-openai-key",
        "Endpoint": "your-openai-endpoint",
        "api_version": "2023-05-15",
        "Model": "gpt-35-turbo",
        "MaxTokens": 4000
    }
}
```

Alternatively, you can set the IoT Hub connection string using an environment variable:
```bash
export IOTHUB_DEVICE_CONNECTION_STRING="your-connection-string"
```

## Usage

Start the application:

```bash
python main.py
```

Once running:

1. Say the wake word ("Hey GPT" by default) to activate the assistant.
2. Ask your question or give a command.
3. The assistant will process your request and respond with synthesized speech.

## Azure IoT Hub Setup

PiChat uses Azure IoT Hub to securely communicate with the backend service. Follow these steps to set up Azure IoT Hub:

### Register your Raspberry Pi as a Device

1. Login to Azure:
   ```bash
   az login
   ```

2. Register your device:
   ```bash
   az iot hub device-identity create --hub-name iot-pichat-dev --device-id raspberry-pi-1
   ```

3. Get the connection string:
   ```bash
   az iot hub device-identity connection-string show --hub-name iot-pichat-dev --device-id raspberry-pi-1
   ```

4. Use the connection string in your config.json or set it as an environment variable.


## Architecture

PiChat follows this process flow:

1. Wake word detection activates the assistant
2. Speech-to-text converts your voice to text
3. Text is sent to a backend service via Azure IoT Hub
4. The backend processes your request (typically using OpenAI GPT)
5. Response is sent back to the device via IoT Hub
6. Text-to-speech converts the response to spoken words
