import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # Server configuration
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8080"))
    API_TOKEN: str = os.getenv("API_TOKEN", "your_secure_token_here")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Azure Cosmos DB configuration
    COSMOS_ENDPOINT: str = os.getenv("COSMOS_ENDPOINT", "")
    COSMOS_KEY: str = os.getenv("COSMOS_KEY", "")
    COSMOS_DATABASE: str = os.getenv("COSMOS_DATABASE", "pichat")
    COSMOS_CONTAINER_CHATS: str = os.getenv("COSMOS_CONTAINER_CHATS", "chats")
    COSMOS_CONTAINER_MESSAGES: str = os.getenv("COSMOS_CONTAINER_MESSAGES", "messages")
    COSMOS_CONTAINER_USERS: str = os.getenv("COSMOS_CONTAINER_USERS", "users")
    COSMOS_CONTAINER_SETTINGS: str = os.getenv("COSMOS_CONTAINER_SETTINGS", "settings")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create settings instance
settings = Settings() 