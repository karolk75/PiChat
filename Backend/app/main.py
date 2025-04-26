from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json
from typing import Dict, List, Any
import logging
from .config import settings
from .models import SessionLocal, engine, Base
from .schemas import WebSocketMessage
from .websocket import ConnectionManager
from .routers import conversations, messages, users, settings_router
from .auth import get_api_key
from .websocket_handlers import register_handlers

# Initialize logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PiChat API", description="WebSocket and REST API for PiChat")

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

# Include routers
app.include_router(conversations.router, prefix="/api", tags=["conversations"])
app.include_router(messages.router, prefix="/api", tags=["messages"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(settings_router.router, prefix="/api", tags=["settings"])

@app.get("/")
async def root():
    return {"message": "Welcome to PiChat API"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str = None):
    # Validate API token
    if not token or token != settings.API_TOKEN:
        await websocket.close(code=1008)  # Policy violation
        return
    
    # Accept connection
    await manager.connect(websocket)
    
    try:
        while True:
            # Receive JSON message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message based on action
            message = WebSocketMessage(**message_data)
            response = await manager.handle_message(message, websocket)
            
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