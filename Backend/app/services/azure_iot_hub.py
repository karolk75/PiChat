import asyncio
import json
import logging
import os
import base64
import hmac
import hashlib
import urllib.parse
import time
import uuid
from typing import Any, Dict, List

from azure.eventhub.aio import EventHubConsumerClient
import aiohttp

from ..config import settings
from ..models.iot_message import IoTHubRequest, IoTHubResponse
from .cosmos_db import cosmos_service
from .azure_openai import openai_service

logger = logging.getLogger(__name__)

# Reduce noise from Azure libraries - adding these filters here
logging.getLogger('azure').setLevel(logging.WARNING)
logging.getLogger('azure.eventhub').setLevel(logging.WARNING)
logging.getLogger('azure.eventhub._pyamqp').setLevel(logging.WARNING)
logging.getLogger('uamqp').setLevel(logging.WARNING)

class IoTHubService:
    def __init__(self, connection_manager=None):
        """Initialize the IoT Hub service with EventHub consumer client"""
        self.consumer_group = settings.IOT_HUB_CONSUMER_GROUP
        self.event_hub_conn_str = settings.EVENT_HUB_COMPATIBLE_CONN_STR
        self.hostname = settings.IOT_HUB_HOST_NAME
        self.client = None
        self.device_client_cache = {}
        self.running = False
        self.task = None
        self.connection_manager = connection_manager
        
        # Extract hub name and credentials from connection string
        try:
            conn_parts = {}
            for part in self.event_hub_conn_str.split(';'):
                if '=' in part:
                    key, value = part.split('=', 1)
                    conn_parts[key] = value
            
            self.shared_access_key_name = conn_parts.get('SharedAccessKeyName')
            self.shared_access_key = conn_parts.get('SharedAccessKey')
                
            logger.info(f"IoT Hub initialized with hub name: {self.hub_name}, access key name: {self.shared_access_key_name}")
                
        except Exception as e:
            logger.error(f"Failed to parse connection string: {str(e)}")
            self.hub_name = settings.IOT_HUB_NAME
            self.hostname = f"{self.hub_name}.azure-devices.net" if self.hub_name else None
        
        # Extract EventHub name from connection string if available
        self.eventhub_name = None
        if self.event_hub_conn_str:
            try:
                for part in self.event_hub_conn_str.split(';'):
                    if part.startswith('EntityPath='):
                        self.eventhub_name = part.split('=', 1)[1]
                        break
            except Exception as e:
                logger.error(f"Failed to extract EventHub name: {str(e)}")
        
    async def start(self):
        """Start listening for messages from IoT Hub"""
        if self.running:
            logger.info("IoT Hub service is already running")
            return
            
        if not settings.IOT_HUB_ENABLE:
            logger.info("IoT Hub service is disabled")
            return
            
        if not self.event_hub_conn_str:
            logger.error("IoT Hub connection string not provided")
            return
            
        try:
            # Use the event hub compatible connection string directly if available
            if self.event_hub_conn_str and self.eventhub_name:
                logger.info(f"Using Event Hub compatible connection string with EventHub: {self.eventhub_name}")
                conn_str = self.event_hub_conn_str
                eventhub_name = self.eventhub_name
            else:
                # Fall back to IoT Hub connection string
                logger.info("Using IoT Hub connection string")
                conn_str = self.event_hub_conn_str
                eventhub_name = "$Default"  # IoT Hub's built-in EventHub
            
            # Create EventHub client from connection string
            self.client = EventHubConsumerClient.from_connection_string(
                conn_str=conn_str,
                consumer_group=self.consumer_group,
                eventhub_name=eventhub_name
            )
            
            # Start processing messages in the background
            self.running = True
            self.task = asyncio.create_task(self._process_events())
            
            # Start periodic cleanup of old processed messages (runs every 24 hours)
            self.cleanup_task = asyncio.create_task(self._cleanup_processed_messages())
            
            logger.info(f"IoT Hub service started with consumer group: {self.consumer_group}")
        except Exception as e:
            logger.error(f"Failed to start IoT Hub service: {str(e)}")
            self.running = False
            
    async def stop(self):
        """Stop the IoT Hub service"""
        if not self.running:
            return
            
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        
        # Also cancel the cleanup task if it exists
        if hasattr(self, 'cleanup_task') and self.cleanup_task:
            self.cleanup_task.cancel()
            try:
                await self.cleanup_task
            except asyncio.CancelledError:
                pass
            
        if self.client:
            await self.client.close()
            self.client = None
            
        logger.info("IoT Hub service stopped")
    
    async def _process_events(self):
        """Process events from IoT Hub"""
        async def on_event(partition_context, event):
            """Process a single event"""
            try:
                # Extract device ID from the connection
                device_id = event.system_properties.get(b'iothub-connection-device-id', b'unknown-device').decode()
                
                # Check if we've already processed this event
                event_id = event.system_properties.get(b'message-id')
                if event_id:
                    event_id = event_id.decode()
                    # Use Cosmos DB to check if we've already processed this message
                    if await cosmos_service.is_message_processed(event_id):
                        logger.debug(f"Skipping already processed event {event_id} from device {device_id}")
                        await partition_context.update_checkpoint(event)
                        return
                    
                    # Mark this message as processed in Cosmos DB
                    await cosmos_service.mark_message_processed(event_id, device_id)
                
                # Parse message body - improved JSON parsing from test file
                try:
                    if isinstance(event.body, bytes):
                        message_body = json.loads(event.body.decode('utf-8'))
                    elif hasattr(event, 'body_as_json') and callable(event.body_as_json):
                        message_body = event.body_as_json()
                    elif isinstance(event.body, str):
                        message_body = json.loads(event.body)
                    else:
                        message_body = {"raw_data": str(event.body)}
                        logger.warning(f"Received event with unexpected body type: {type(event.body)}")
                except Exception as e:
                    logger.warning(f"Error parsing message body: {e}")
                    message_body = {"error": "Failed to parse message", "raw_data": str(event.body)}
                
                logger.info(f"Received message from device {device_id}: {message_body}")
                
                # Process the message
                await self._handle_device_message(device_id, message_body)
                
                # Update checkpoint
                await partition_context.update_checkpoint(event)
            except Exception as e:
                logger.error(f"Error processing IoT Hub event: {str(e)}")
        
        try:
            async with self.client:
                await self.client.receive(on_event=on_event, starting_position="-1")
        except asyncio.CancelledError:
            logger.info("IoT Hub event processing cancelled")
        except Exception as e:
            logger.error(f"Error in IoT Hub event loop: {str(e)}")
            
    async def _handle_device_message(self, device_id: str, message_data: Dict[str, Any]):
        """Handle a message from a device"""
        try:
            # Parse the request
            request = IoTHubRequest(**message_data)
            
            # Create or get chat ID
            chat_id = await self._ensure_chat_exists(device_id)
            
            # Store the message in Cosmos DB
            user_message = {
                "role": "user",
                "content": request.message,
                "device_id": device_id
            }
            await cosmos_service.add_message(chat_id, user_message)
            
            # Generate response with OpenAI
            messages = request.conversation if request.conversation else await self._get_chat_history(chat_id)
            
            # If no existing conversation, create a new one with the current message
            if not messages:
                messages = [{"role": "user", "content": request.message}]
            
            # Generate streaming response
            full_response = ""
            async for chunk in openai_service.generate_response(messages):
                if not chunk.choices:
                    continue
                
                chunk_message = chunk.choices[0].delta.content
                if chunk_message:
                    full_response += chunk_message
            
            # Store assistant response in Cosmos DB
            assistant_message = {
                "role": "assistant",
                "content": full_response
            }
            await cosmos_service.add_message(chat_id, assistant_message)
            
            # Send response back to device
            await self._send_response_to_device(device_id, full_response, chat_id)
            
            # Broadcast message to WebSocket clients if connection manager exists
            if self.connection_manager:
                await self._broadcast_to_websocket(device_id, request.message, full_response, chat_id)
            
        except Exception as e:
            logger.error(f"Error handling device message: {str(e)}")
            # Try to send error response back to device
            error_message = f"Error processing your message: {str(e)}"
            await self._send_response_to_device(device_id, error_message, "error")
    
    async def _ensure_chat_exists(self, device_id: str) -> str:
        """Ensure a chat exists for the device or create a new one"""
        # Query for existing chat with this device ID
        chats = await cosmos_service.get_all_chats()
        for chat in chats:
            if chat.get("device_id") == device_id and chat.get("active", False):
                return chat["id"]
        
        # Create a new chat for this device
        chat_name = f"IoT Device Chat - {device_id}"
        new_chat = await cosmos_service.create_chat(chat_name)
        
        # Add device_id and set as active
        new_chat["device_id"] = device_id
        new_chat["active"] = True
        
        # Update the chat with device info
        await cosmos_service.update_chat(new_chat["id"], new_chat)
        
        return new_chat["id"]
    
    async def _get_chat_history(self, chat_id: str) -> List[Dict[str, str]]:
        """Get chat history in OpenAI message format"""
        messages = await cosmos_service.get_chat_messages(chat_id)
        
        # Convert to OpenAI format
        openai_messages = []
        for msg in messages:
            if "role" in msg and "content" in msg:
                openai_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        return openai_messages
    
    async def _send_response_to_device(self, device_id: str, response: str, chat_id: str):
        """Send a response back to the device using REST API"""
        try:
            # Create a response object
            response_obj = IoTHubResponse(
                response=response,
                conversation_id=chat_id
            )
            
            # Serialize to JSON - handle datetime serialization issue
            try:
                payload = json.dumps(response_obj.dict())
            except TypeError as e:
                if "not JSON serializable" in str(e):
                    # Create a custom encoder for handling datetime objects
                    class DateTimeEncoder(json.JSONEncoder):
                        def default(self, obj):
                            import datetime
                            if isinstance(obj, (datetime.date, datetime.datetime)):
                                return obj.isoformat()
                            return super().default(obj)
                    
                    payload = json.dumps(response_obj.dict(), cls=DateTimeEncoder)
                else:
                    raise
            
            # Use REST API approach for sending cloud-to-device messages
            # This is more reliable and doesn't depend on Azure CLI being installed
            
            # Log credentials for debugging
            logger.debug(f"Hub Name: {self.hub_name}, Key Name: {self.shared_access_key_name}")
            
            if not self.hub_name or not self.shared_access_key or not self.shared_access_key_name:
                # Check environment directly as fallback
                self.hub_name = self.hub_name or os.getenv("IOT_HUB_NAME")
                self.shared_access_key_name = self.shared_access_key_name or "service"
                self.shared_access_key = self.shared_access_key or os.getenv("IOT_HUB_SERVICE_KEY")
                
                # Log attempt to use fallback
                logger.info(f"Using fallback IoT Hub credentials - Name: {self.hub_name}")
                
                if not all([self.hub_name, self.shared_access_key_name, self.shared_access_key]):
                    missing = []
                    if not self.hub_name: missing.append("hub_name")
                    if not self.shared_access_key_name: missing.append("shared_access_key_name")
                    if not self.shared_access_key: missing.append("shared_access_key")
                    raise ValueError(f"Missing required IoT Hub credentials: {', '.join(missing)}")
            
            # Ensure we have the full hostname (not just the prefix)
            hostname = self.hostname if hasattr(self, 'hostname') and self.hostname else f"{self.hub_name}.azure-devices.net"
            
            # Generate SAS token for authentication
            # Create SAS token that expires in 1 hour
            token_expiry = int(time.time() + 3600)
            resource_uri = f"{hostname}/devices/{device_id}/messages/devicebound"
            
            # Properly encode the resource URI first
            quoted_resource_uri = urllib.parse.quote_plus(resource_uri)
            
            # Create the string to sign
            to_sign = f"{quoted_resource_uri}\n{token_expiry}"
            
            # Create signature
            signature = base64.b64encode(
                hmac.HMAC(
                    base64.b64decode(self.shared_access_key), 
                    to_sign.encode('utf-8'), 
                    hashlib.sha256
                ).digest()
            ).decode('utf-8')
            
            # Create SAS token
            token = f"SharedAccessSignature sr={quoted_resource_uri}&sig={urllib.parse.quote(signature)}&se={token_expiry}&skn={self.shared_access_key_name}"
            
            # Send message using REST API
            url = f"https://{hostname}/devices/{device_id}/messages/devicebound?api-version=2020-03-13"
            headers = {
                "Authorization": token,
                "Content-Type": "application/json",
                "iothub-app-contenttype": "application/json"
            }
            
            logger.info(f"Sending message to device {device_id} via REST API at {url}")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=payload, headers=headers) as response:
                    if response.status >= 400:
                        error_text = await response.text()
                        raise Exception(f"Error sending message via REST API: {response.status} - {error_text}")
            
            logger.info(f"Response sent to device {device_id}")
        except Exception as e:
            logger.error(f"Error sending response to device {device_id}: {str(e)}")

    async def _cleanup_processed_messages(self):
        """Periodically clean up old processed message records"""
        # Keep processed messages for 7 days by default
        days_to_keep = 7
        cleanup_interval = 24 * 60 * 60  # 24 hours in seconds
        
        while self.running:
            try:
                # Delete old processed message records
                deleted_count = await cosmos_service.delete_old_processed_messages(days_to_keep)
                if deleted_count > 0:
                    logger.info(f"Deleted {deleted_count} old processed message records")
                
                # Wait for the next cleanup interval
                await asyncio.sleep(cleanup_interval)
            except asyncio.CancelledError:
                # Task was cancelled, exit gracefully
                logger.info("Processed messages cleanup task cancelled")
                return
            except Exception as e:
                logger.error(f"Error in processed messages cleanup: {str(e)}")
                # If an error occurs, wait before retrying
                await asyncio.sleep(60)  # Wait 1 minute before retrying

    async def _broadcast_to_websocket(self, device_id: str, user_message: str, assistant_response: str, chat_id: str):
        """Broadcast the message and response to all connected WebSocket clients"""
        try:
            if not self.connection_manager:
                return
                
            # First, add the user message to the chat history for frontend clients
            # This mimics what happens when a message is sent from the frontend
            user_message_id = str(uuid.uuid4())
            user_payload = {
                "type": "FIRST_MESSAGE",
                "content": user_message,
                "traceId": user_message_id,
                "end": True
            }
            
            # Wait a moment to mimic the usual message flow
            await asyncio.sleep(0.5)
            
            # Broadcast user message with MESSAGE type
            await self.connection_manager.broadcast(user_payload)
            
            # Now broadcast the assistant response with the same format that 
            # message_handler.py uses for consistency
            trace_id = str(uuid.uuid4())
            
            # Split the response into smaller chunks to simulate streaming
            # This makes it work with the frontend's existing typing effect
            chunk_size = 8  # Characters per chunk
            response_chunks = [assistant_response[i:i+chunk_size] for i in range(0, len(assistant_response), chunk_size)]
            
            # Send each chunk with the MESSAGE type
            for i, chunk in enumerate(response_chunks):
                is_last_chunk = i == len(response_chunks) - 1
                
                message_payload = {
                    "type": "MESSAGE",
                    "content": chunk,
                    "traceId": trace_id,
                    "end": is_last_chunk
                }
                
                await self.connection_manager.broadcast(message_payload)
                
                # Small delay to simulate typing
                if not is_last_chunk:
                    await asyncio.sleep(0.05)
                    
            logger.info(f"Broadcasted IoT message and response from device {device_id} to WebSocket clients")
        except Exception as e:
            logger.error(f"Error broadcasting to WebSocket: {str(e)}")

# Create a singleton instance
iot_hub_service = IoTHubService()

def get_iot_hub_service():
    """Get the IoT Hub service instance"""
    return iot_hub_service

def set_connection_manager(connection_manager):
    """Set the WebSocket connection manager for the IoT Hub service"""
    global iot_hub_service
    iot_hub_service.connection_manager = connection_manager
    logger.info("WebSocket connection manager set for IoT Hub service") 