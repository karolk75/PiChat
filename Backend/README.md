# PiChat Backend

A streamlined WebSocket-based backend for PiChat with Azure Cosmos DB integration.

## Features

- WebSocket API for real-time chat messaging
- Azure Cosmos DB integration for cloud-native NoSQL storage
- Structured project layout following FastAPI best practices
- Authentication using API tokens

## Requirements

- Python 3.8+
- Azure Cosmos DB account

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
4. Create an `.env` file based on `env.example`:
   ```bash
   cp env.example .env
   ```
5. Update the `.env` file with your Azure Cosmos DB credentials

## Running the Application

Start the development server:

```bash
python run.py
```

Or with uvicorn directly:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
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

## Project Structure

```
PiChat/
├── app/
│   ├── schemas/          # Pydantic models
│   ├── services/         # Service layer
│   ├── config.py         # Application configuration
│   ├── main.py           # FastAPI application
│   ├── websocket.py      # WebSocket connection manager
│   └── websocket_handlers.py  # WebSocket message handlers
├── .env                  # Environment variables (not in repo)
├── env.example           # Example environment variables
├── requirements.txt      # Python dependencies
└── run.py                # Application entry point
```

## Azure Cosmos DB Integration

This application uses Azure Cosmos DB as its primary data store. Make sure to configure the following environment variables:

```
COSMOS_ENDPOINT=your_cosmos_db_endpoint
COSMOS_KEY=your_cosmos_db_key
COSMOS_DATABASE=pichat
COSMOS_CONTAINER_CHATS=chats
COSMOS_CONTAINER_MESSAGES=messages
COSMOS_CONTAINER_USERS=users
COSMOS_CONTAINER_SETTINGS=settings
```

The application will automatically create the database and containers if they don't exist. 