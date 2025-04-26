import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as cosmos_exceptions
from azure.cosmos.partition_key import PartitionKey
from ..config import settings
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class CosmosDBService:
    def __init__(self):
        """Initialize CosmosDB client and create containers if they don't exist"""
        self.client = cosmos_client.CosmosClient(
            settings.COSMOS_ENDPOINT, 
            credential=settings.COSMOS_KEY
        )
        self.database_name = settings.COSMOS_DATABASE
        self.initialize_database()
        
    def initialize_database(self):
        """Create database and containers if they don't exist"""
        try:
            # Create or get database
            self.database = self.client.create_database_if_not_exists(id=self.database_name)
            
            # Create or get containers with appropriate partition keys
            self.chats_container = self.database.create_container_if_not_exists(
                id=settings.COSMOS_CONTAINER_CHATS,
                partition_key=PartitionKey(path="/id")
            )
            
            self.messages_container = self.database.create_container_if_not_exists(
                id=settings.COSMOS_CONTAINER_MESSAGES,
                partition_key=PartitionKey(path="/chat_id")
            )
            
            self.users_container = self.database.create_container_if_not_exists(
                id=settings.COSMOS_CONTAINER_USERS,
                partition_key=PartitionKey(path="/id")
            )
            
            self.settings_container = self.database.create_container_if_not_exists(
                id=settings.COSMOS_CONTAINER_SETTINGS,
                partition_key=PartitionKey(path="/user_id")
            )
            
            logger.info(f"CosmosDB initialization complete: {self.database_name}")
        except Exception as e:
            logger.error(f"Error initializing CosmosDB: {str(e)}")
            raise
    
    # Chat operations
    async def get_all_chats(self) -> List[Dict[str, Any]]:
        """Get all chats from the database"""
        query = "SELECT * FROM c ORDER BY c.created_at DESC"
        items = list(self.chats_container.query_items(
            query=query,
            enable_cross_partition_query=True
        ))
        return items
    
    async def create_chat(self, name: str) -> Dict[str, Any]:
        """Create a new chat"""
        chat_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        chat_item = {
            "id": chat_id,
            "name": name,
            "active": False,
            "created_at": timestamp
        }
        
        created_item = self.chats_container.create_item(body=chat_item)
        return created_item
    
    async def get_chat(self, chat_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific chat by ID"""
        try:
            chat = self.chats_container.read_item(
                item=chat_id,
                partition_key=chat_id
            )
            return chat
        except cosmos_exceptions.CosmosResourceNotFoundError:
            return None
    
    async def delete_chat(self, chat_id: str) -> bool:
        """Delete a chat and its messages"""
        try:
            # Delete the chat
            self.chats_container.delete_item(
                item=chat_id,
                partition_key=chat_id
            )
            
            # Delete all messages for this chat
            query = f"SELECT * FROM c WHERE c.chat_id = '{chat_id}'"
            messages = list(self.messages_container.query_items(
                query=query,
                partition_key=chat_id
            ))
            
            for message in messages:
                self.messages_container.delete_item(
                    item=message['id'],
                    partition_key=chat_id
                )
            
            return True
        except cosmos_exceptions.CosmosResourceNotFoundError:
            return False
    
    # Message operations
    async def get_chat_messages(self, chat_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a specific chat"""
        query = f"SELECT * FROM c WHERE c.chat_id = '{chat_id}' ORDER BY c.created_at ASC"
        messages = list(self.messages_container.query_items(
            query=query,
            partition_key=chat_id
        ))
        return messages
    
    async def add_message(self, chat_id: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """Add a message to a chat"""
        if 'id' not in message:
            message['id'] = str(uuid.uuid4())
        
        if 'created_at' not in message:
            message['created_at'] = datetime.utcnow().isoformat()
        
        message['chat_id'] = chat_id
        
        created_message = self.messages_container.create_item(body=message)
        return created_message

# Create a singleton instance
cosmos_service = CosmosDBService()

# Database dependency
def get_cosmos_db():
    return cosmos_service 