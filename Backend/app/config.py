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
    
    # Azure OpenAI configuration
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_KEY: str = os.getenv("AZURE_OPENAI_KEY", "")
    AZURE_OPENAI_DEPLOYMENT_GPT4: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_GPT4", "")
    AZURE_OPENAI_DEPLOYMENT_GPT35: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_GPT35", "")
    
    # Azure Speech configuration
    AZURE_SPEECH_KEY: str = os.getenv("AZURE_SPEECH_KEY", "")
    AZURE_SPEECH_REGION: str = os.getenv("AZURE_SPEECH_REGION", "")
    
    # Azure Cosmos DB configuration
    COSMOS_ENDPOINT: str = os.getenv("COSMOS_ENDPOINT", "")
    COSMOS_KEY: str = os.getenv("COSMOS_KEY", "")
    COSMOS_DATABASE: str = os.getenv("COSMOS_DATABASE", "pichat")
    COSMOS_CONTAINER_CHATS: str = os.getenv("COSMOS_CONTAINER_CHATS", "chats")
    COSMOS_CONTAINER_MESSAGES: str = os.getenv("COSMOS_CONTAINER_MESSAGES", "messages")
    COSMOS_CONTAINER_USERS: str = os.getenv("COSMOS_CONTAINER_USERS", "users")
    COSMOS_CONTAINER_SETTINGS: str = os.getenv("COSMOS_CONTAINER_SETTINGS", "settings")
    
    # Legacy Database configuration (PostgreSQL)
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_NAME: str = os.getenv("DB_NAME", "pichat")
    DB_USER: str = os.getenv("DB_USER", "pichat_admin")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "secure_password")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    
    # Generate DATABASE_URL for SQLAlchemy (legacy)
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create settings instance
settings = Settings() 