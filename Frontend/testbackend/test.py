#!/usr/bin/env python

import asyncio
import websockets
import os
import json
import uuid
from datetime import datetime

# In-memory database for chats and messages with test data
chats = []
chat_messages = {}  # Dict of chat_id -> list of messages

async def handle_message(websocket, message):
    """Handle different message types from the client"""
    try:
        # Check if the message is a string or JSON
        if message.startswith('{'):
            data = json.loads(message)
            message_type = data.get('type', '')
            
            # Handle different message types
            if message_type == 'GET_CHATS':
                return await get_chats(websocket)
            elif message_type == 'CREATE_CHAT':
                return await create_chat(websocket, data)
            elif message_type == 'GET_CHAT_HISTORY':
                return await get_chat_history(websocket, data)
            elif message_type == 'DELETE_CHAT':
                return await delete_chat(websocket, data)
            elif message_type == 'SEND_MESSAGE':
                return await handle_chat_message(websocket, data)
        
        # If not a recognized JSON command, treat as a simple text message
        await echo_message(websocket, message)
    
    except json.JSONDecodeError:
        # If it's not valid JSON, treat as a simple message
        await echo_message(websocket, message)

async def get_chats(websocket):
    """Send list of chats to the client"""
    response = {
        "type": "CHAT_LIST",
        "chats": chats
    }
    await websocket.send(json.dumps(response))

async def create_chat(websocket, data):
    """Create a new chat"""
    chat_id = str(uuid.uuid4())
    chat_name = data.get('name', f'Chat {len(chats) + 1}')
    
    new_chat = {
        "id": chat_id,
        "name": chat_name,
        "active": False,
        "created_at": datetime.now().isoformat()
    }
    
    chats.append(new_chat)
    chat_messages[chat_id] = []
    
    response = {
        "type": "NEW_CHAT",
        "chat": new_chat
    }
    print(response, flush=True)
    await websocket.send(json.dumps(response))

async def get_chat_history(websocket, data):
    """Get message history for a chat"""
    chat_id = data.get('chatId')
    if not chat_id or chat_id not in chat_messages:
        return
    
    response = {
        "type": "CHAT_HISTORY",
        "messages": chat_messages[chat_id]
    }
    await websocket.send(json.dumps(response))

async def delete_chat(websocket, data):
    """Delete a chat"""
    chat_id = data.get('chatId')
    if not chat_id:
        return
    
    global chats
    chats = [chat for chat in chats if chat['id'] != chat_id]
    
    if chat_id in chat_messages:
        del chat_messages[chat_id]
    
    response = {
        "type": "CHAT_DELETED",
        "chatId": chat_id
    }
    await websocket.send(json.dumps(response))

async def handle_chat_message(websocket, data):
    """Handle a message sent within a chat"""
    chat_id = data.get('chatId')
    message = data.get('message')
    
    if not chat_id or not message or chat_id not in chat_messages:
        return
    
    # Store the user message
    chat_messages[chat_id].append(message)
    
    # Generate a mock response
    trace_id = message.get('id', str(uuid.uuid4()))
    content = f"This is a response to: {message.get('content')}"
    
    # Send the assistant's response in chunks to simulate streaming
    chunks = [content[i:i+10] for i in range(0, len(content), 10)]
    
    for chunk in chunks:
        response = {
            "type": "MESSAGE",
            "content": chunk,
            "traceId": trace_id,
            "end": False
        }
        await websocket.send(json.dumps(response))
        await asyncio.sleep(0.1)  # Simulate network delay
    
    # Send final chunk to indicate end of message
    response = {
        "type": "MESSAGE",
        "content": "[END]",
        "traceId": trace_id,
        "end": True
    }
    await websocket.send(json.dumps(response))
    
    # Store the assistant response
    assistant_message = {
        "content": content,
        "role": "assistant",
        "id": trace_id
    }
    chat_messages[chat_id].append(assistant_message)

async def echo_message(websocket, message):
    """Legacy echo functionality"""
    await websocket.send(message)
    await websocket.send("[END]")

async def handler(websocket):
    try:
        # Send initial chat list when client connects
        await get_chats(websocket)
        
        async for message in websocket:
            print("Received message:", message, flush=True)
            await handle_message(websocket, message)
    except websockets.exceptions.ConnectionClosed:
        print("Client disconnected", flush=True)
    except Exception as e:
        print(f"Error: {e}", flush=True)

async def main():
    print("WebSocket server starting", flush=True)
    
    # Create some initial test chats
    if not chats:
        for i in range(1, 3):
            chat_id = str(uuid.uuid4())
            chats.append({
                "id": chat_id,
                "name": f"Test Chat {i}",
                "active": False,
                "created_at": datetime.now().isoformat()
            })
            chat_messages[chat_id] = []
    
    # Create the server
    async with websockets.serve(
        handler,
        "0.0.0.0",
        int(os.environ.get('PORT', 8090))
    ) as server:
        print("WebSocket server running on port 8090", flush=True)
        await asyncio.Future()  # run forever

if __name__ == "__main__":
    asyncio.run(main())