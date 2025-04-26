from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime, Enum, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import uuid
from datetime import datetime
import enum
from .config import settings

# Create SQLAlchemy engine and session
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Helper function to generate UUIDs
def generate_uuid():
    return str(uuid.uuid4())

# Enums for database models
class ModelType(enum.Enum):
    GPT4 = "gpt-4"
    GPT35 = "gpt-3.5-turbo"

class VoiceGender(enum.Enum):
    MALE = "male"
    FEMALE = "female"

class VoiceAccent(enum.Enum):
    POLISH = "polish"
    US = "us"
    UK = "uk"

# Database Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversations = relationship("Conversation", back_populates="user")
    settings = relationship("UserSetting", back_populates="user", uselist=False)

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String(200), default="New Conversation")
    user_id = Column(String, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    conversation_id = Column(String, ForeignKey("conversations.id"))
    content = Column(Text)
    role = Column(String(20))  # 'user' or 'assistant'
    is_audio = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

class UserSetting(Base):
    __tablename__ = "user_settings"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    selected_model = Column(String, default=ModelType.GPT35.value)
    voice_gender = Column(String, default=VoiceGender.FEMALE.value)
    voice_accent = Column(String, default=VoiceAccent.POLISH.value)
    
    # Relationships
    user = relationship("User", back_populates="settings")

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 