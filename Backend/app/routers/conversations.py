from fastapi import APIRouter, Depends, HTTPException, status, WebSocket
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from ..models import get_db, Conversation, User, Message
from ..schemas import Conversation as ConversationSchema
from ..schemas import ConversationCreate, ConversationUpdate, ConversationWithMessages
from ..auth import get_api_key
import uuid
from datetime import datetime

router = APIRouter()

# Conversations REST API endpoints
@router.get("/conversations", response_model=List[ConversationSchema], dependencies=[Depends(get_api_key)])
async def get_conversations(db: Session = Depends(get_db), user_id: str = "default"):
    conversations = db.query(Conversation).filter(Conversation.user_id == user_id).order_by(Conversation.updated_at.desc()).all()
    return conversations

@router.post("/conversations", response_model=ConversationSchema, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_api_key)])
async def create_conversation(conversation: ConversationCreate, db: Session = Depends(get_db), user_id: str = "default"):
    # Check if user exists, if not create a default user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id, username="default_user", email="default@example.com")
        db.add(user)
        db.commit()
    
    # Create new conversation
    db_conversation = Conversation(
        id=str(uuid.uuid4()),
        title=conversation.title,
        user_id=user_id
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

@router.get("/conversations/{conversation_id}", response_model=ConversationWithMessages, dependencies=[Depends(get_api_key)])
async def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation

@router.put("/conversations/{conversation_id}", response_model=ConversationSchema, dependencies=[Depends(get_api_key)])
async def update_conversation(conversation_id: str, conversation: ConversationUpdate, db: Session = Depends(get_db)):
    db_conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Update conversation
    db_conversation.title = conversation.title
    db_conversation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_conversation)
    return db_conversation

@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT, dependencies=[Depends(get_api_key)])
async def delete_conversation(conversation_id: str, db: Session = Depends(get_db)):
    db_conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if db_conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Delete conversation (cascade will delete related messages)
    db.delete(db_conversation)
    db.commit()
    return None

# WebSocket handlers
async def handle_get_conversations(payload: Dict[str, Any], websocket: WebSocket, db: Session = None) -> Dict[str, Any]:
    """WebSocket handler to get conversations"""
    if db is None:
        db = next(get_db())
    
    user_id = payload.get("user_id", "default")
    conversations = db.query(Conversation).filter(Conversation.user_id == user_id).order_by(Conversation.updated_at.desc()).all()
    
    return {
        "action": "conversations_list",
        "payload": {
            "conversations": [
                {
                    "id": conv.id,
                    "title": conv.title,
                    "created_at": conv.created_at.isoformat(),
                    "updated_at": conv.updated_at.isoformat()
                } for conv in conversations
            ]
        }
    }

async def handle_create_conversation(payload: Dict[str, Any], websocket: WebSocket, db: Session = None) -> Dict[str, Any]:
    """WebSocket handler to create a conversation"""
    if db is None:
        db = next(get_db())
    
    title = payload.get("title", "New Conversation")
    user_id = payload.get("user_id", "default")
    
    # Check if user exists, if not create a default user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        user = User(id=user_id, username="default_user", email="default@example.com")
        db.add(user)
        db.commit()
    
    # Create new conversation
    conversation_id = str(uuid.uuid4())
    conversation = Conversation(
        id=conversation_id,
        title=title,
        user_id=user_id
    )
    db.add(conversation)
    db.commit()
    
    return {
        "action": "conversation_created",
        "payload": {
            "id": conversation.id,
            "title": conversation.title,
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat()
        }
    } 