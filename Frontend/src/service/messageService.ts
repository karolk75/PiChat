import { SocketService } from "./socket";
import { message } from "../interfaces/interfaces";

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
  public async sendMessage(chatId: string, message: string): Promise<void> {
    if (!chatId) {
      throw new Error("Chat ID is required to send a message");
    }

    await this.socketService
      .waitForConnection()
      .then(() => {
        this.socketService.sendMessage({
          type: "SEND_MESSAGE",
          payload: {
            chatId,
            content: message,
          },
        });
      })
      .catch((error) => {
        console.error("Failed to send message:", error);
        throw error;
      });
  }

  // Method to get chat history
  public async getChatHistory(chatId: string): Promise<void> {
    if (!chatId) return;

    await this.socketService
      .waitForConnection()
      .then(() => {
        this.socketService.sendMessage({
          type: "GET_CHAT_HISTORY",
          payload: {
            chatId,
          },
        });
      })
      .catch((error) => {
        console.error("Failed to get chat history:", error);
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

  public onMessage(
    callback: (content: string, traceId: string, end: boolean) => void
  ): () => void {
    const wrappedCallback = (data: any) => {
      callback(data.content, data.traceId, data.end === true);
    };

    this.socketService.addListener("MESSAGE", wrappedCallback);

    // Return a cleanup function
    return () => {
      this.socketService.removeListener("MESSAGE", wrappedCallback);
    };
  }

  public onFirstMessage(callback: (content: string) => void): () => void {
    const wrappedCallback = (data: any) => {
      callback(data.content);
    };

    this.socketService.addListener("FIRST_MESSAGE", wrappedCallback);

    // Return a cleanup function
    return () => {
      this.socketService.removeListener("FIRST_MESSAGE", wrappedCallback);
    };
  }

  public onError(callback: (error: string) => void): () => void {
    const wrappedCallback = (data: any) => {
      callback(data.error || "Unknown error occurred");
    };

    this.socketService.addListener("ERROR", wrappedCallback);

    // Return a cleanup function
    return () => {
      this.socketService.removeListener("ERROR", wrappedCallback);
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
