from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import logging

from app.models.websocket import WebSocketCommand
from .config import settings
from .websocket.websocket import ConnectionManager
from .websocket.websocket_handlers import register_handlers

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PiChat API", description="WebSocket API for PiChat")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize WebSocket connection manager
manager = ConnectionManager()

# Register WebSocket handlers
register_handlers(manager)

@app.get("/")
async def root():
    return {"message": "Welcome to PiChat API"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    # Accept connection without token validation in development
    if settings.ENVIRONMENT == "development" or (token and token == settings.API_TOKEN):
        await manager.connect(websocket)
    else:
        await websocket.close(code=1008)  # Policy violation
        return
    
    try:
        while True:
            # Receive JSON message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message based on action/type
            action = message_data.get("type", message_data.get("action", ""))
            
            # Handle WebSocket message format
            if action:
                if "payload" in message_data:
                    # Process using payload format
                    response = await manager.handle_message(WebSocketCommand(**message_data), websocket)
                else:
                    # Process using flat format
                    response = await manager.handle_message(WebSocketCommand(type=action, **message_data), websocket)
                
                # Send response if applicable
                if response:
                    await websocket.send_text(json.dumps(response))
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await manager.send_error(websocket, str(e))
        manager.disconnect(websocket)

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"} 