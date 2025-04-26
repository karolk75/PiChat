import { SocketService } from './socket';
import { Chat } from '@/components/custom/sidebar';

export class ChatService {
  private static instance: ChatService;
  private socketService: SocketService;
  
  private constructor() {
    this.socketService = SocketService.getInstance();
  }

  public static getInstance(): ChatService {
    if (!ChatService.instance) {
      ChatService.instance = new ChatService();
    }
    return ChatService.instance;
  }

  // Method to get all chats
  public getChats(): void {
    this.socketService.sendMessage({ type: "GET_CHATS" });
  }

  // Method to create a new chat
  public createChat(name: string): void {
    this.socketService.sendMessage({
      type: "CREATE_CHAT",
      name
    });
  }

  // Method to delete a chat
  public deleteChat(chatId: string): void {
    this.socketService.sendMessage({
      type: "DELETE_CHAT",
      chatId
    });
  }

  // Methods to subscribe to chat-related events
  public onChatList(callback: (chats: Chat[]) => void): () => void {
    const wrappedCallback = (data: any) => {
      callback(data.chats || []);
    };
    
    this.socketService.addListener("CHAT_LIST", wrappedCallback);
    
    // Return a cleanup function
    return () => {
      this.socketService.removeListener("CHAT_LIST", wrappedCallback);
    };
  }

  public onNewChat(callback: (chat: Chat, chatId: string) => void): () => void {
    const wrappedCallback = (data: any) => {
      callback(data.chat, data.chat.id);
    };
    
    this.socketService.addListener("NEW_CHAT", wrappedCallback);
    
    // Return a cleanup function
    return () => {
      this.socketService.removeListener("NEW_CHAT", wrappedCallback);
    };
  }

  public onChatDeleted(callback: (chatId: string) => void): () => void {
    const wrappedCallback = (data: any) => {
      callback(data.chatId);
    };
    
    this.socketService.addListener("CHAT_DELETED", wrappedCallback);
    
    // Return a cleanup function
    return () => {
      this.socketService.removeListener("CHAT_DELETED", wrappedCallback);
    };
  }
} 