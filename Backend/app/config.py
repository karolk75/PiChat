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
    COSMOS_CONTAINER_PROCESSED_MESSAGES: str = os.getenv("COSMOS_CONTAINER_PROCESSED_MESSAGES", "processed_messages")
    
    # Azure OpenAI configuration
    AZURE_OPENAI_ENDPOINT: str = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    AZURE_OPENAI_KEY: str = os.getenv("AZURE_OPENAI_KEY", "")
    AZURE_OPENAI_API_VERSION: str = os.getenv("AZURE_OPENAI_API_VERSION", "")
    AZURE_OPENAI_DEPLOYMENT_NAME: str = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "")
    
    # Azure IoT Hub configuration
    IOT_HUB_NAME: str = os.getenv("IOT_HUB_NAME", "")
    IOT_HUB_HOST_NAME: str = os.getenv("IOT_HUB_HOST_NAME", "")
    EVENT_HUB_COMPATIBLE_CONN_STR: str = os.getenv("EVENT_HUB_COMPATIBLE_CONN_STR", "")
    IOT_HUB_CONSUMER_GROUP: str = os.getenv("IOT_HUB_CONSUMER_GROUP", "backend")
    IOT_HUB_ENABLE: bool = os.getenv("IOT_HUB_ENABLE", "true").lower() == "true"
    USE_AZURE_CLI_FOR_C2D: bool = os.getenv("USE_AZURE_CLI_FOR_C2D", "false").lower() == "true"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create settings instance
settings = Settings() 