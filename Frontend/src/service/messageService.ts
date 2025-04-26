import { SocketService } from './socket';
import { v4 as uuidv4 } from 'uuid';
import { message } from '../interfaces/interfaces';

export class MessageService {
  private static instance: MessageService;
  private socketService: SocketService;
  
  private constructor() {
    this.socketService = SocketService.getInstance();
  }

  public static getInstance(): MessageService {
    if (!MessageService.instance) {
      MessageService.instance = new MessageService();
    }
    return MessageService.instance;
  }

  // Method to send a message in a specific chat
  public sendMessage(chatId: string, content: string): string {
    if (!chatId) {
      throw new Error("Chat ID is required to send a message");
    }
    
    const traceId = uuidv4();
    const message = { content, role: "user", id: traceId };

    this.socketService.sendMessage({
      type: "SEND_MESSAGE",
      chatId,
      message
    });

    return traceId;
  }

  // Method to get chat history
  public getChatHistory(chatId: string): void {
    if (!chatId) return;
    
    this.socketService.sendMessage({
      type: "GET_CHAT_HISTORY",
      chatId
    });
  }

  // Event listeners for messages
  public onChatHistory(callback: (messages: message[]) => void): () => void {
    const wrappedCallback = (data: any) => {
      callback(data.messages || []);
    };
    
    this.socketService.addListener("CHAT_HISTORY", wrappedCallback);
    
    // Return a cleanup function
    return () => {
      this.socketService.removeListener("CHAT_HISTORY", wrappedCallback);
    };
  }

  public onMessage(callback: (content: string, traceId: string, end: boolean) => void): () => void {
    const wrappedCallback = (data: any) => {
      callback(data.content, data.traceId, data.end === true);
    };
    
    this.socketService.addListener("MESSAGE", wrappedCallback);
    
    // Return a cleanup function
    return () => {
      this.socketService.removeListener("MESSAGE", wrappedCallback);
    };
  }

  public onTextMessage(callback: (text: string) => void): () => void {
    this.socketService.addListener("text", callback);
    
    // Return a cleanup function
    return () => {
      this.socketService.removeListener("text", callback);
    };
  }
} 