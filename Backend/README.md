# PiChat Backend

A modular FastAPI-based backend for PiChat with WebSocket support and Azure Cosmos DB integration.

## Features

- RESTful API endpoints for chat management
- WebSocket support for real-time messaging
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

## API Documentation

Once the application is running, you can access the Swagger UI documentation at:

```
http://localhost:8080/docs
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

## Project Structure

```
PiChat/
├── app/
│   ├── routers/          # API route definitions
│   ├── schemas/          # Pydantic models
│   ├── services/         # Service layer
│   ├── config.py         # Application configuration
│   ├── main.py           # FastAPI application
│   ├── models.py         # Database models (legacy)
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