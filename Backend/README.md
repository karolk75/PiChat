# Backend PiChat

## Overview

This document describes the architecture of the backend for the PiChat AI Assistant project. The backend is written in Python using FastAPI and provides WebSocket functionality for real-time communication between the web interface and the Raspberry Pi voice interface.

## Table of Contents

1. [Technology Stack](#technology-stack)
2. [Project Structure](#project-structure)
3. [WebSocket Protocol](#websocket-protocol)
4. [WebSocket Implementation](#websocket-implementation)
5. [Database Schema](#database-schema)
6. [Authentication and Authorization](#authentication-and-authorization)
7. [Environment Variables](#environment-variables)
8. [Development Setup](#development-setup)
9. [Docker Configuration](#docker-configuration)
10. [Azure Deployment](#azure-deployment)
11. [Testing](#testing)

## Technology Stack

The backend uses the following technologies:

- **Python 3.11+** - Main programming language
  - Why Python? Python is widely used for AI/ML applications, has excellent integration with Azure services, and FastAPI provides high performance with async support.
  
- **FastAPI** - Web framework
  - Offers high performance, automatic API documentation, and native async support.
  
- **WebSockets** - For real-time communication
  - Provides bidirectional communication between clients and server.
  
- **SQLAlchemy** - ORM for database operations
  - Simplifies database interactions with automatic migrations and query building.
  
- **Azure SQL** - Main database
  - Provides managed SQL capabilities with good integration with other Azure services.
  
- **Azure OpenAI** - AI processing
  - Integrates with GPT models for natural language understanding and generation.

- **Azure Speech Services** - Text-to-speech and speech-to-text capabilities
  - Essential for the voice interface functionality.

- **Docker** - Containerization
  - Ensures consistent deployment across different environments.

## Project Structure

The project uses a clean architecture with clear separation of concerns:

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                # Application entry point
│   ├── config.py              # Configuration management
│   ├── models.py              # Database models and schema
│   ├── schemas.py             # Pydantic models for validation
│   ├── auth.py                # Authentication utilities
│   ├── websocket.py           # WebSocket connection manager
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── conversations.py   # Conversation endpoints
│   │   ├── messages.py        # Message endpoints
│   │   ├── users.py           # User endpoints
│   │   └── settings_router.py # Settings endpoints
│   └── services/
│       ├── __init__.py
│       ├── azure_openai.py    # Azure OpenAI integration
│       └── azure_speech.py    # Azure Speech integration
├── requirements.txt           # Python dependencies
├── Dockerfile                 # Docker build instructions
├── .dockerignore              # Files to exclude from Docker context
└── README.md                  # This file
```

### Structure Explanation

#### `app/`
Contains the main application code and modules.

- **`main.py`** - Application entry point with FastAPI initialization.
- **`config.py`** - Manages configuration loaded from environment variables.
- **`models.py`** - SQLAlchemy models representing database tables.
- **`schemas.py`** - Pydantic models for request/response validation.
- **`auth.py`** - Authentication utilities for API key validation.
- **`websocket.py`** - Manages WebSocket connections and message handling.

#### `app/routers/`
Contains API route definitions organized by functionality.

- **`conversations.py`** - Endpoints for managing conversations.
- **`messages.py`** - Endpoints for message handling.
- **`users.py`** - Endpoints for user management.
- **`settings_router.py`** - Endpoints for user settings.

#### `app/services/`
Contains integration with external services.

- **`azure_openai.py`** - Integration with Azure OpenAI for AI responses.
- **`azure_speech.py`** - Integration with Azure Speech Services for voice.

## WebSocket Protocol

In the PiChat application, all real-time communication between clients (web interface and Raspberry Pi) and the server happens via WebSocket protocol, enabling bidirectional real-time communication that's ideal for chat and synchronization.

### Message Structure

WebSocket messages are structured as JSON in the following format:

```json
{
  "action": "string",
  "payload": {}
}
```

The `action` field specifies the type of operation, and the `payload` contains data related to that operation.

### Main WebSocket Operations

#### Conversation Management

- **`get_conversations`** - Get list of conversations
  ```json
  { "action": "get_conversations" }
  ```
  Response:
  ```json
  {
    "action": "conversations_list",
    "payload": {
      "conversations": [
        { "id": "uuid", "title": "Title", "last_message_at": "timestamp" }
      ]
    }
  }
  ```

- **`create_conversation`** - Create a new conversation
  ```json
  { "action": "create_conversation", "payload": { "title": "New Conversation" } }
  ```

- **`get_conversation`** - Get conversation details
  ```json
  { "action": "get_conversation", "payload": { "id": "uuid" } }
  ```

- **`update_conversation`** - Update conversation title
  ```json
  { "action": "update_conversation", "payload": { "id": "uuid", "title": "New Title" } }
  ```

- **`delete_conversation`** - Delete a conversation
  ```json
  { "action": "delete_conversation", "payload": { "id": "uuid" } }
  ```

#### Message Management

- **`send_message`** - Send a new message
  ```json
  {
    "action": "send_message",
    "payload": {
      "conversation_id": "uuid",
      "content": "Message content",
      "is_audio": false
    }
  }
  ```

- **`get_messages`** - Get message history
  ```json
  { "action": "get_messages", "payload": { "conversation_id": "uuid" } }
  ```

#### User Settings

- **`get_settings`** - Get user settings
  ```json
  { "action": "get_settings" }
  ```

- **`update_settings`** - Update user settings
  ```json
  {
    "action": "update_settings",
    "payload": {
      "selected_model": "gpt-4",
      "voice_settings": { "gender": "female", "accent": "polish" }
    }
  }
  ```

#### Speech Services

- **`text_to_speech`** - Convert text to speech
  ```json
  {
    "action": "text_to_speech",
    "payload": {
      "text": "Text to convert to speech",
      "voice_gender": "female",
      "voice_accent": "polish"
    }
  }
  ```

- **`speech_to_text`** - Convert speech to text
  ```json
  {
    "action": "speech_to_text",
    "payload": {
      "audio_data": "base64_encoded_audio"
    }
  }
  ```

## Environment Variables

The application configuration is managed through environment variables:

```
# Server configuration
SERVER_PORT=8080
API_TOKEN=your_secure_token_here
ENVIRONMENT=development

# Azure OpenAI configuration
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint
AZURE_OPENAI_KEY=your_azure_openai_key
AZURE_OPENAI_DEPLOYMENT_GPT4=your_gpt4_deployment_name
AZURE_OPENAI_DEPLOYMENT_GPT35=your_gpt35_deployment_name

# Azure Speech configuration
AZURE_SPEECH_KEY=your_azure_speech_key
AZURE_SPEECH_REGION=your_azure_speech_region

# Database configuration
DB_HOST=localhost
DB_NAME=pichat
DB_USER=pichat_admin
DB_PASSWORD=secure_password
DB_PORT=5432
```

## Development Setup

To set up the development environment:

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with required environment variables
5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```
6. Access the API documentation at http://localhost:8080/docs

## Docker Configuration

The application can be run in a Docker container:

```bash
# Build the Docker image
docker build -t pichat-backend .

# Run the container
docker run -p 8080:8080 --env-file .env pichat-backend
```

## Testing

To run tests:

```bash
pytest
```

The test suite includes unit tests for API endpoints, WebSocket handlers, and service integrations. 