import { SocketService } from "./socket";
import { Chat } from "@/components/custom/sidebar";

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
  public async getChats(): Promise<void> {
    await this.socketService
      .waitForConnection()
      .then(() => {
        this.socketService.sendMessage({ type: "GET_CHATS" });
      })
      .catch((error) => {
        console.error("Failed to get chats:", error);
      });
  }

  // Method to create a new chat
  public async createChat(name: string): Promise<void> {
    await this.socketService
      .waitForConnection()
      .then(() => {
        this.socketService.sendMessage({
          type: "CREATE_CHAT",
          payload: {
            name,
          },
        });
      })
      .catch((error) => {
        console.error("Failed to create chat:", error);
      });
  }

  // Method to delete a chat
  public async deleteChat(chatId: string): Promise<void> {
    await this.socketService
      .waitForConnection()
      .then(() => {
        this.socketService.sendMessage({
          type: "DELETE_CHAT",
          payload: {
            chatId,
          },
        });
      })
      .catch((error) => {
        console.error("Failed to delete chat:", error);
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

  public onConnectionStatusChange(
    callback: (status: string) => void
  ): () => void {
    const wrappedCallback = (data: any) => {
      callback(data.status);
    };

    this.socketService.addListener("connection", wrappedCallback);

    // Return a cleanup function
    return () => {
      this.socketService.removeListener("connection", wrappedCallback);
    };
  }
}
