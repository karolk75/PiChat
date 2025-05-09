from datetime import datetime
from typing import Any, Dict

from fastapi import WebSocket

from app.services.cosmos_db import CosmosDBService, get_cosmos_db

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def handle_get_chats(payload: Dict[str, Any], websocket: WebSocket, db: CosmosDBService = None) -> Dict[str, Any]:
    """WebSocket handler to get all chats"""
    if db is None:
        db = get_cosmos_db()
    
    chats = await db.get_all_chats()
    
    return {
        "type": "CHAT_LIST",
        "chats": chats
    }

async def handle_create_chat(payload: Dict[str, Any], websocket: WebSocket, db: CosmosDBService = None) -> Dict[str, Any]:
    """WebSocket handler to create a new chat"""
    if db is None:
        db = get_cosmos_db()
    
    chat_name = payload.get('name', f'Chat {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    new_chat = await db.create_chat(chat_name)
    
    return {
        "type": "NEW_CHAT",
        "chat": new_chat
    }

async def handle_get_chat_history(payload: Dict[str, Any], websocket: WebSocket, db: CosmosDBService = None) -> Dict[str, Any]:
    """WebSocket handler to get chat history"""
    if db is None:
        db = get_cosmos_db()
    
    chat_id = payload.get('chatId')
    if not chat_id:
        return {"type": "ERROR", "error": "Chat ID is required"}
    
    messages = await db.get_chat_messages(chat_id)
    
    return {
        "type": "CHAT_HISTORY",
        "messages": messages
    }

async def handle_delete_chat(payload: Dict[str, Any], websocket: WebSocket, db: CosmosDBService = None) -> Dict[str, Any]:
    """WebSocket handler to delete a chat"""
    if db is None:
        db = get_cosmos_db()
    
    chat_id = payload.get('chatId')
    if not chat_id:
        return {"type": "ERROR", "error": "Chat ID is required"}
    
    await db.delete_chat(chat_id)
    
    return {
        "type": "CHAT_DELETED",
        "chatId": chat_id
    }