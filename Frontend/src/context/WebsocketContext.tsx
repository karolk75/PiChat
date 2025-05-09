import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { SocketService } from '../service/socket';
import { ChatService } from '../service/chatService';
import { MessageService } from '../service/messageService';

// WebSocket context type
interface WebSocketContextType {
  socketService: SocketService;
  chatService: ChatService;
  messageService: MessageService;
  isConnected: boolean;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'failed';
}

// Create context with default values
const WebSocketContext = createContext<WebSocketContextType | undefined>(undefined);

// Provider component props
interface WebSocketProviderProps {
  children: ReactNode;
}

// Provider component
export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'failed'>('connecting');
  
  // Get service instances
  const socketService = SocketService.getInstance();
  const chatService = ChatService.getInstance();
  const messageService = MessageService.getInstance();
  
  useEffect(() => {
    // Listen for connection status changes
    const handleConnection = (data: any) => {
      setConnectionStatus(data.status);
    };
    
    socketService.addListener('connection', handleConnection);
    
    // Listen for error to set failed status
    const handleError = () => {
      setConnectionStatus('disconnected');
    };
    
    socketService.addListener('error', handleError);
    
    // Cleanup listeners
    return () => {
      socketService.removeListener('connection', handleConnection);
      socketService.removeListener('error', handleError);
    };
  }, [socketService]);
  
  // Context value
  const contextValue: WebSocketContextType = {
    socketService,
    chatService,
    messageService,
    isConnected: connectionStatus === 'connected',
    connectionStatus,
  };
  
  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  );
};

// Custom hook to use the WebSocket context
export const useWebSocket = (): WebSocketContextType => {
  const context = useContext(WebSocketContext);
  
  if (context === undefined) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  
  return context;
}; 