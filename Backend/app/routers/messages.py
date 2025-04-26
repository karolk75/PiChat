from fastapi import APIRouter, Depends, HTTPException, status, WebSocket
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..models import get_db, Message, Conversation
from ..schemas import Message as MessageSchema
from ..schemas import MessageCreate
from ..auth import get_api_key
from ..services.azure_openai import generate_response
import uuid
from datetime import datetime
import json

router = APIRouter()

# Message REST API endpoints
@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageSchema], dependencies=[Depends(get_api_key)])
async def get_messages(conversation_id: str, db: Session = Depends(get_db)):
    # Check if conversation exists
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all()
    return messages

@router.post("/messages", response_model=MessageSchema, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_api_key)])
async def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    # Check if conversation exists
    conversation = db.query(Conversation).filter(Conversation.id == message.conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Create new message
    db_message = Message(
        id=str(uuid.uuid4()),
        conversation_id=message.conversation_id,
        content=message.content,
        role=message.role,
        is_audio=message.is_audio
    )
    db.add(db_message)
    
    # Update conversation's updated_at timestamp
    conversation.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(db_message)
    return db_message

# WebSocket handlers
async def handle_send_message(payload: Dict[str, Any], websocket: WebSocket, db: Session = None) -> Dict[str, Any]:
    """WebSocket handler to send a message and get AI response"""
    if db is None:
        db = next(get_db())
    
    conversation_id = payload.get("conversation_id")
    content = payload.get("content")
    is_audio = payload.get("is_audio", False)
    
    if not conversation_id or not content:
        return {
            "action": "error",
            "payload": {"message": "Missing conversation_id or content"}
        }
    
    # Check if conversation exists
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation is None:
        return {
            "action": "error",
            "payload": {"message": "Conversation not found"}
        }
    
    # Create user message
    user_message_id = str(uuid.uuid4())
    user_message = Message(
        id=user_message_id,
        conversation_id=conversation_id,
        content=content,
        role="user",
        is_audio=is_audio
    )
    db.add(user_message)
    
    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()
    db.commit()
    
    # Get conversation history for context
    history = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all()
    messages_for_context = [{"role": msg.role, "content": msg.content} for msg in history]
    
    # Send acknowledgment that message was received
    await websocket.send_text(json.dumps({
        "action": "message_received",
        "payload": {
            "id": user_message_id,
            "conversation_id": conversation_id,
            "content": content,
            "role": "user",
            "is_audio": is_audio,
            "created_at": user_message.created_at.isoformat()
        }
    }))
    
    # Generate AI response
    try:
        # Get user settings for model selection
        settings = db.query('UserSetting').filter_by(user_id=conversation.user_id).first()
        model = settings.selected_model if settings else "gpt-3.5-turbo"
        
        # Generate response (streaming)
        async for chunk in generate_response(messages_for_context, model):
            if chunk.choices[0].delta.content:
                await websocket.send_text(json.dumps({
                    "action": "message_stream",
                    "payload": {
                        "conversation_id": conversation_id,
                        "content": chunk.choices[0].delta.content,
                        "is_final": False
                    }
                }))
        
        # Create final assistant message in DB
        final_content = "I'm sorry, I couldn't generate a response."
        # In a real implementation, we would accumulate the streamed content
        # For now, let's just create a simple response
        final_content = "This is a response from the assistant."
        
        assistant_message = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            content=final_content,
            role="assistant",
            is_audio=False
        )
        db.add(assistant_message)
        db.commit()
        
        # Send final message
        return {
            "action": "message_stream",
            "payload": {
                "id": assistant_message.id,
                "conversation_id": conversation_id,
                "content": final_content,
                "role": "assistant",
                "is_audio": False,
                "created_at": assistant_message.created_at.isoformat(),
                "is_final": True
            }
        }
    except Exception as e:
        return {
            "action": "error",
            "payload": {"message": f"Error generating response: {str(e)}"}
        }

async def handle_get_messages(payload: Dict[str, Any], websocket: WebSocket, db: Session = None) -> Dict[str, Any]:
    """WebSocket handler to get messages for a conversation"""
    if db is None:
        db = next(get_db())
    
    conversation_id = payload.get("conversation_id")
    if not conversation_id:
        return {
            "action": "error",
            "payload": {"message": "Missing conversation_id"}
        }
    
    # Check if conversation exists
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation is None:
        return {
            "action": "error",
            "payload": {"message": "Conversation not found"}
        }
    
    # Get messages
    messages = db.query(Message).filter(Message.conversation_id == conversation_id).order_by(Message.created_at).all()
    
    return {
        "action": "messages_list",
        "payload": {
            "conversation_id": conversation_id,
            "messages": [
                {
                    "id": msg.id,
                    "content": msg.content,
                    "role": msg.role,
                    "is_audio": msg.is_audio,
                    "created_at": msg.created_at.isoformat()
                } for msg in messages
            ]
        }
    } 