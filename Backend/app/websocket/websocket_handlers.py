import logging

from app.websocket.chat_handler import (
    handle_create_chat,
    handle_delete_chat,
    handle_get_chat_history,
    handle_get_chats,
)
from app.websocket.message_handler import handle_chat_message
from app.websocket.websocket import ConnectionManager


logger = logging.getLogger(__name__)


def register_handlers(manager: ConnectionManager):
    """Register all WebSocket message handlers with the connection manager"""

    # Register chat handlers
    manager.register_handler("GET_CHATS", handle_get_chats)
    manager.register_handler("CREATE_CHAT", handle_create_chat)
    manager.register_handler("GET_CHAT_HISTORY", handle_get_chat_history)
    manager.register_handler("DELETE_CHAT", handle_delete_chat)
    manager.register_handler("SEND_MESSAGE", handle_chat_message)

    logger.info("All WebSocket handlers registered")
