import { useState, useEffect } from 'react';
import { message } from '@/interfaces/interfaces';
import { useWebSocket } from '@/context/WebsocketContext';
import { v4 as uuidv4 } from 'uuid';

export function useMessages(currentChatId: string | null) {
  const [messages, setMessages] = useState<message[]>([]);
  const [question, setQuestion] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [showSuggestions, setShowSuggestions] = useState<boolean>(true);
  const [messageBuffer, setMessageBuffer] = useState<{content: string, traceId: string | null}>({content: "", traceId: null});
  
  const { messageService } = useWebSocket();

  // Setup message-related listeners
  useEffect(() => {
    const chatHistoryCleanup = messageService.onChatHistory((messageHistory) => {
      setMessages(messageHistory);
    });

    const onFirstMessage = messageService.onFirstMessage((content) => {
      setMessages(prev => [...prev, { content: content, role: "user" }]);
    });
    
    const messageCleanup = messageService.onMessage((content, traceId, end) => {
      setIsLoading(false);
      
      if (content === "[END]" && end) {
        return;
      }
      
      // Add incoming content to buffer
      setMessageBuffer(prev => ({
        content: prev.content + content,
        traceId: traceId
      }));
    });
    
    const errorCleanup = messageService.onError((error) => {
      setIsLoading(false);
      console.error("Error from server:", error);
    });
    
    const textMessageCleanup = messageService.onTextMessage((text) => {
      if (text === "[END]") {
        setIsLoading(false);
        return;
      }
      
      // Add incoming text to buffer
      const traceId = uuidv4();
      setMessageBuffer(prev => {
        const updatedTraceId = prev.content.length === 0 ? traceId : prev.traceId;
        return {
          content: prev.content + text,
          traceId: updatedTraceId
        };
      });
    });
    
    return () => {
      chatHistoryCleanup();
      onFirstMessage();
      messageCleanup();
      errorCleanup();
      textMessageCleanup();
    };
  }, [messageService]);

  // if we have messages, don't show suggestions
  useEffect(() => {
    if (messages.length > 0) {
      setShowSuggestions(false);
    } else {
      setShowSuggestions(true);
    }
  }, [messages]);

  // Helper function to get the last character from messages
  const getLastCharFromMessages = () => {
    if (messages.length === 0) return '';
    
    const lastMessage = messages[messages.length - 1];
    if (lastMessage.role !== 'assistant') return '';
    
    const content = lastMessage.content;
    return content.length > 0 ? content[content.length - 1] : '';
  };

  // Create typing effect from buffer to messages
  useEffect(() => {
    if (!messageBuffer.content) return;
    
    if (messageBuffer.content.length === 0) return;
    
    const chunkSize = Math.floor(Math.random() * 4) + 1;
    const chunk = messageBuffer.content.substring(0, chunkSize);
    const remaining = messageBuffer.content.substring(chunkSize);
    
    let typingSpeed = Math.floor(Math.random() * 80) + 20;
    
    const lastCharInMessages = getLastCharFromMessages();
    const hasPunctuation = /[.!?,;:]/.test(lastCharInMessages);
    
    if (hasPunctuation) {
      typingSpeed += Math.floor(Math.random() * 150) + 150;
    }
    
    const timer = setTimeout(() => {
      setMessages(prev => {
        const lastMessage = prev[prev.length - 1];
        const isAppending = lastMessage?.role === "assistant" && lastMessage.id === messageBuffer.traceId;
        
        if (isAppending) {
          const updatedMessages = [...prev];
          updatedMessages[prev.length - 1] = {
            ...lastMessage,
            content: lastMessage.content + chunk
          };
          return updatedMessages;
        } else {
          return [
            ...prev,
            { 
              content: chunk, 
              role: "assistant", 
              id: messageBuffer.traceId || undefined 
            }
          ];
        }
      });
      
      setMessageBuffer({
        content: remaining,
        traceId: messageBuffer.traceId
      });
    }, typingSpeed);
    
    return () => clearTimeout(timer);
  }, [messageBuffer]);

  // Function to handle submitting a message
  const handleSubmit = async (text?: string) => {
    if (isLoading || !currentChatId) return;
    
    const messageText = text || question;
    if (!messageText.trim()) return;
    
    setIsLoading(true);
    
    try {
      // Add user message to state immediately
      setMessages(prev => [...prev, { content: messageText, role: "user" }]);
      
      // Send the message to the backend
      await messageService.sendMessage(currentChatId, messageText);
      setQuestion("");
    } catch (error) {
      console.error("Failed to send message:", error);
      setIsLoading(false);
    }
  };

  // Function to clear messages
  const clearMessages = () => {
    setMessages([]);
    setShowSuggestions(true);
  };

  return {
    messages,
    question,
    setQuestion,
    isLoading,
    showSuggestions,
    setShowSuggestions,
    handleSubmit,
    clearMessages
  };
} 