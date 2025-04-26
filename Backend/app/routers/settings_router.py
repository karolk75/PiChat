from fastapi import APIRouter, Depends, HTTPException, status, WebSocket
from sqlalchemy.orm import Session
from typing import Dict, Any
from ..models import get_db, UserSetting, User
from ..schemas import UserSettings, UserSettingsUpdate
from ..auth import get_api_key
import uuid

router = APIRouter()

@router.get("/settings/{user_id}", response_model=UserSettings, dependencies=[Depends(get_api_key)])
async def get_user_settings(user_id: str, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user settings
    settings = db.query(UserSetting).filter(UserSetting.user_id == user_id).first()
    if settings is None:
        # Create default settings if not exist
        settings = UserSetting(
            id=str(uuid.uuid4()),
            user_id=user_id
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return settings

@router.put("/settings/{user_id}", response_model=UserSettings, dependencies=[Depends(get_api_key)])
async def update_user_settings(user_id: str, settings_update: UserSettingsUpdate, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get or create user settings
    db_settings = db.query(UserSetting).filter(UserSetting.user_id == user_id).first()
    if db_settings is None:
        db_settings = UserSetting(
            id=str(uuid.uuid4()),
            user_id=user_id
        )
        db.add(db_settings)
    
    # Update settings
    db_settings.selected_model = settings_update.selected_model
    db_settings.voice_gender = settings_update.voice_settings.gender
    db_settings.voice_accent = settings_update.voice_settings.accent
    
    db.commit()
    db.refresh(db_settings)
    return db_settings

# WebSocket handlers
async def handle_get_settings(payload: Dict[str, Any], websocket: WebSocket, db: Session = None) -> Dict[str, Any]:
    """WebSocket handler to get user settings"""
    if db is None:
        db = next(get_db())
    
    user_id = payload.get("user_id", "default")
    
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        # Create default user if not exists
        user = User(id=user_id, username="default_user", email="default@example.com")
        db.add(user)
        db.commit()
    
    # Get or create user settings
    settings = db.query(UserSetting).filter(UserSetting.user_id == user_id).first()
    if settings is None:
        settings = UserSetting(
            id=str(uuid.uuid4()),
            user_id=user_id
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    
    return {
        "action": "settings",
        "payload": {
            "selected_model": settings.selected_model,
            "voice_settings": {
                "gender": settings.voice_gender,
                "accent": settings.voice_accent
            }
        }
    }

async def handle_update_settings(payload: Dict[str, Any], websocket: WebSocket, db: Session = None) -> Dict[str, Any]:
    """WebSocket handler to update user settings"""
    if db is None:
        db = next(get_db())
    
    user_id = payload.get("user_id", "default")
    selected_model = payload.get("selected_model")
    voice_settings = payload.get("voice_settings", {})
    
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        # Create default user if not exists
        user = User(id=user_id, username="default_user", email="default@example.com")
        db.add(user)
        db.commit()
    
    # Get or create user settings
    settings = db.query(UserSetting).filter(UserSetting.user_id == user_id).first()
    if settings is None:
        settings = UserSetting(
            id=str(uuid.uuid4()),
            user_id=user_id
        )
        db.add(settings)
    
    # Update settings
    if selected_model:
        settings.selected_model = selected_model
    
    if voice_settings:
        if "gender" in voice_settings:
            settings.voice_gender = voice_settings["gender"]
        if "accent" in voice_settings:
            settings.voice_accent = voice_settings["accent"]
    
    db.commit()
    db.refresh(settings)
    
    return {
        "action": "settings_updated",
        "payload": {
            "selected_model": settings.selected_model,
            "voice_settings": {
                "gender": settings.voice_gender,
                "accent": settings.voice_accent
            }
        }
    } 