from .websocket import ConnectionManager
from .routers.conversations import handle_get_conversations, handle_create_conversation
from .routers.messages import handle_send_message, handle_get_messages
from .routers.settings_router import handle_get_settings, handle_update_settings
from .routers.chats import handle_get_chats, handle_create_chat, handle_get_chat_history, handle_delete_chat, handle_chat_message
from .services.azure_speech import text_to_speech, speech_to_text
import base64
import logging
import json
from fastapi import WebSocket
from typing import Dict, Any

logger = logging.getLogger(__name__)

def register_handlers(manager: ConnectionManager):
    """Register all WebSocket message handlers with the connection manager"""
    
    # Register conversation handlers (legacy)
    manager.register_handler("get_conversations", handle_get_conversations)
    manager.register_handler("create_conversation", handle_create_conversation)
    
    # Register message handlers (legacy)
    manager.register_handler("send_message", handle_send_message)
    manager.register_handler("get_messages", handle_get_messages)
    
    # Register settings handlers (legacy)
    manager.register_handler("get_settings", handle_get_settings)
    manager.register_handler("update_settings", handle_update_settings)
    
    # Register new chat handlers
    manager.register_handler("GET_CHATS", handle_get_chats)
    manager.register_handler("CREATE_CHAT", handle_create_chat)
    manager.register_handler("GET_CHAT_HISTORY", handle_get_chat_history)
    manager.register_handler("DELETE_CHAT", handle_delete_chat)
    manager.register_handler("SEND_MESSAGE", handle_chat_message)
    
    # Register speech handlers
    manager.register_handler("text_to_speech", handle_text_to_speech)
    manager.register_handler("speech_to_text", handle_speech_to_text)
    
    logger.info("All WebSocket handlers registered")

# Speech service handlers
async def handle_text_to_speech(payload: Dict[str, Any], websocket: WebSocket) -> Dict[str, Any]:
    """WebSocket handler for text to speech conversion"""
    try:
        text = payload.get("text")
        voice_gender = payload.get("voice_gender", "female")
        voice_accent = payload.get("voice_accent", "polish")
        
        if not text:
            return {
                "action": "error",
                "payload": {"message": "Missing text parameter"}
            }
        
        # Convert text to speech
        audio_data = await text_to_speech(text, voice_gender, voice_accent)
        
        # Encode audio data as base64
        audio_base64 = base64.b64encode(audio_data).decode("utf-8")
        
        # Return response
        return {
            "action": "text_to_speech_result",
            "payload": {
                "text": text,
                "audio_data": audio_base64,
                "format": "wav" 
            }
        }
    except Exception as e:
        logger.error(f"Error in text_to_speech handler: {str(e)}")
        return {
            "action": "error",
            "payload": {"message": f"Error converting text to speech: {str(e)}"}
        }

async def handle_speech_to_text(payload: Dict[str, Any], websocket: WebSocket) -> Dict[str, Any]:
    """WebSocket handler for speech to text conversion"""
    try:
        audio_base64 = payload.get("audio_data")
        
        if not audio_base64:
            return {
                "action": "error",
                "payload": {"message": "Missing audio_data parameter"}
            }
        
        # Decode base64 audio data
        audio_data = base64.b64decode(audio_base64)
        
        # Convert speech to text
        text = await speech_to_text(audio_data)
        
        # Return response
        return {
            "action": "speech_to_text_result",
            "payload": {
                "text": text
            }
        }
    except Exception as e:
        logger.error(f"Error in speech_to_text handler: {str(e)}")
        return {
            "action": "error",
            "payload": {"message": f"Error converting speech to text: {str(e)}"}
        } 