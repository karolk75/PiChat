from fastapi import WebSocket
import json
import logging
from typing import Dict, List, Any, Callable, Optional
import asyncio
from .schemas import WebSocketMessage

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # Dictionary to store active connections: {client_id: WebSocket}
        self.active_connections: Dict[str, WebSocket] = {}
        # Dictionary to register message handlers: {action: handler_function}
        self.message_handlers: Dict[str, Callable] = {}
    
    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection and store it"""
        await websocket.accept()
        # Use the WebSocket object ID as the client ID
        client_id = str(id(websocket))
        self.active_connections[client_id] = websocket
        logger.info(f"Client connected: {client_id}. Total connections: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        client_id = str(id(websocket))
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client disconnected: {client_id}. Remaining connections: {len(self.active_connections)}")
    
    def register_handler(self, action: str, handler: Callable):
        """Register a handler function for a specific WebSocket action"""
        self.message_handlers[action] = handler
        logger.info(f"Registered handler for action: {action}")
    
    async def broadcast(self, message: Dict[str, Any]):
        """Send a message to all connected clients"""
        disconnected = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to client {client_id}: {str(e)}")
                disconnected.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected:
            if client_id in self.active_connections:
                del self.active_connections[client_id]
    
    async def send_personal_message(self, message: Dict[str, Any], websocket: WebSocket):
        """Send a message to a specific client"""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error(f"Error sending personal message: {str(e)}")
            self.disconnect(websocket)
    
    async def send_error(self, websocket: WebSocket, error_message: str):
        """Send an error message to a client"""
        await self.send_personal_message(
            {"action": "error", "payload": {"message": error_message}},
            websocket
        )
    
    async def handle_message(self, message: WebSocketMessage, websocket: WebSocket) -> Optional[Dict[str, Any]]:
        """Process an incoming WebSocket message"""
        action = message.action
        
        # Check if we have a handler for this action
        if action in self.message_handlers:
            try:
                # Call the registered handler with the message payload and client websocket
                return await self.message_handlers[action](message.payload, websocket)
            except Exception as e:
                logger.error(f"Error in handler for action {action}: {str(e)}")
                await self.send_error(websocket, f"Error processing {action}: {str(e)}")
                return {"action": "error", "payload": {"message": str(e)}}
        else:
            logger.warning(f"No handler registered for action: {action}")
            await self.send_error(websocket, f"Unknown action: {action}")
            return {"action": "error", "payload": {"message": f"Unknown action: {action}"}} 