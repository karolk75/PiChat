import { useState, useEffect } from 'react';
import { Chat } from '@/components/custom/sidebar';
import { useWebSocket } from '@/context/WebsocketContext';

export function useChats() {
  const [chats, setChats] = useState<Chat[]>([]);
  const [currentChatId, setCurrentChatId] = useState<string | null>(null);
  const { chatService, messageService, isConnected } = useWebSocket();

  useEffect(() => {
    const chatListCleanup = chatService.onChatList((chatList) => {
      setChats(chatList);
    });
    
    const newChatCleanup = chatService.onNewChat((chat, chatId) => {
      setChats(prev => [...prev, chat]);
      setCurrentChatId(chatId);
    });
    
    const chatDeletedCleanup = chatService.onChatDeleted((chatId) => {
      setChats(prev => prev.filter(chat => chat.id !== chatId));
      if (currentChatId === chatId) {
        setCurrentChatId(null);
      }
    });

    if (isConnected) {
      chatService.getChats().catch(err => console.error("Failed to get chats:", err));
    }
    
    return () => {
      chatListCleanup();
      newChatCleanup();
      chatDeletedCleanup();
    };
  }, [chatService, isConnected, currentChatId]);

  // Load chat history when currentChatId changes
  useEffect(() => {
    if (isConnected && currentChatId) {
      messageService.getChatHistory(currentChatId)
        .catch(err => console.error("Failed to get chat history:", err));
    }
  }, [currentChatId, messageService, isConnected]);

  const handleSelectChat = async (chatId: string | null) => {
    if (currentChatId === chatId) {
      setCurrentChatId(null);
    } else if (chatId) {
      setCurrentChatId(chatId);
    } else {
      setCurrentChatId(null);
    }
  };

  const handleCreateChat = async (name: string) => {
    try {
      await chatService.createChat(name);
    } catch (error) {
      console.error("Failed to create chat:", error);
    }
  };

  const handleDeleteChat = async (chatId: string) => {
    try {
      await chatService.deleteChat(chatId);
    } catch (error) {
      console.error("Failed to delete chat:", error);
    }
  };

  return {
    chats,
    currentChatId,
    handleSelectChat,
    handleCreateChat,
    handleDeleteChat
  };
} 