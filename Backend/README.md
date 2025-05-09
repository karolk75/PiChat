# PiChat Backend

A streamlined WebSocket-based backend for PiChat with Azure Cosmos DB and IoT Hub integration.

## Features

- WebSocket API for real-time chat messaging
- Azure Cosmos DB integration for cloud-native NoSQL storage
- Azure IoT Hub integration for device telemetry and commands
- Azure OpenAI integration for AI capabilities
- Structured project layout following FastAPI best practices
- Docker support for containerized deployment
- Health check endpoint for monitoring

## Requirements

- Python 3.8+
- Azure Cosmos DB account
- Azure IoT Hub (optional)
- Azure OpenAI service (optional)

## Setup

1. Clone this repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create an `.env` file based on the following example:
   ```
   # Server Configuration
   SERVER_PORT=8080
   API_TOKEN=your_secure_token_here
   ENVIRONMENT=development

   # Azure Cosmos DB
   COSMOS_ENDPOINT=your_cosmos_db_endpoint
   COSMOS_KEY=your_cosmos_db_key
   COSMOS_DATABASE=pichat
   COSMOS_CONTAINER_CHATS=chats
   COSMOS_CONTAINER_MESSAGES=messages
   COSMOS_CONTAINER_USERS=users
   COSMOS_CONTAINER_SETTINGS=settings
   COSMOS_CONTAINER_PROCESSED_MESSAGES=processed_messages

   # Azure OpenAI
   AZURE_OPENAI_ENDPOINT=your_openai_endpoint
   AZURE_OPENAI_KEY=your_openai_key
   AZURE_OPENAI_API_VERSION=your_api_version
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment_name

   # Azure IoT Hub
   IOT_HUB_NAME=your_iothub_name
   IOT_HUB_HOST_NAME=your_iothub_hostname
   IOT_HUB_CONSUMER_GROUP=backend
   IOT_HUB_ENABLE=true
   ```

## Running the Application

Start the development server:

```bash
python run.py
```

Or with uvicorn directly:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

## Docker Deployment

Build and run the Docker container:

```bash
docker build -t pichat-backend .
docker run -p 8080:8080 --env-file .env pichat-backend
```

## WebSocket API

The WebSocket API is available at `/ws`. You can connect to it using any WebSocket client.

### WebSocket Commands

The WebSocket API supports the following commands:

- `GET_CHATS`: Get a list of all chats
- `CREATE_CHAT`: Create a new chat
- `GET_CHAT_HISTORY`: Get the message history for a chat
- `DELETE_CHAT`: Delete a chat
- `SEND_MESSAGE`: Send a message in a chat

### Example Usage

```javascript
// Connect to WebSocket
const socket = new WebSocket('ws://localhost:8080/ws');

// Get all chats
socket.send(JSON.stringify({ type: 'GET_CHATS' }));

// Create a new chat
socket.send(JSON.stringify({ 
  type: 'CREATE_CHAT', 
  name: 'My New Chat' 
}));

// Get chat history
socket.send(JSON.stringify({ 
  type: 'GET_CHAT_HISTORY', 
  chatId: 'chat-id-here' 
}));

// Send a message
socket.send(JSON.stringify({ 
  type: 'SEND_MESSAGE', 
  chatId: 'chat-id-here', 
  message: {
    content: 'Hello, world!',
    id: 'unique-message-id'
  }
}));

// Delete a chat
socket.send(JSON.stringify({ 
  type: 'DELETE_CHAT', 
  chatId: 'chat-id-here' 
}));

// Handle responses
socket.onmessage = (event) => {
  const response = JSON.parse(event.data);
  console.log(response);
};
```

## Health Check

The application provides a health check endpoint at `/health` which returns the status of services including IoT Hub.

## Project Structure

```
PiChat/
├── app/
│   ├── models/           # Pydantic models/schemas
│   ├── services/         # Service layer
│   │   ├── cosmos_db.py  # Azure Cosmos DB service
│   │   ├── azure_iot_hub.py # Azure IoT Hub integration
│   │   └── azure_openai.py # Azure OpenAI integration
│   ├── websocket/        # WebSocket handlers
│   ├── config.py         # Application configuration
│   └── main.py           # FastAPI application
├── .env                  # Environment variables (not in repo)
├── Dockerfile            # Docker container configuration
├── .dockerignore         # Docker ignore file
├── requirements.txt      # Python dependencies
└── run.py                # Application entry point
```

## Azure Integrations

### Azure Cosmos DB

This application uses Azure Cosmos DB as its primary data store. The database and containers will be automatically created if they don't exist.

### Azure IoT Hub

The application can connect to an Azure IoT Hub to send commands to IoT devices and receive telemetry from them. Set `IOT_HUB_ENABLE=true` in your environment variables to enable this feature.

### Azure OpenAI

The application can integrate with Azure OpenAI for AI capabilities. Configure the appropriate environment variables to enable this feature. 