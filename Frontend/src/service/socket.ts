// WebSocket service for managing socket connection
export class SocketService {
  private static instance: SocketService;
  private socket: WebSocket | null = null;
  private listeners: Map<string, Set<(data: any) => void>> = new Map();
  private isConnecting: boolean = false;
  private messageQueue: any[] = [];
  private reconnectAttempts: number = 0;
  private maxReconnectAttempts: number = 10;
  private reconnectDelay: number = 1000;

  private constructor() {
    this.connect();
  }

  public static getInstance(): SocketService {
    if (!SocketService.instance) {
      SocketService.instance = new SocketService();
    }
    return SocketService.instance;
  }

  private connect(): void {
    if (this.socket?.readyState === WebSocket.OPEN || this.isConnecting) return;
    
    this.isConnecting = true;
    
    this.socket = new WebSocket("ws://127.0.0.1:8080/ws");

    this.socket.addEventListener("open", () => {
      console.log("WebSocket connection established");
      this.isConnecting = false;
      this.reconnectAttempts = 0;
      this.reconnectDelay = 1000;
      
      // Process any queued messages
      this.processQueue();
      
      // Notify any listeners that we're connected
      this.notifyListeners("connection", { status: "connected" });
    });

    this.socket.addEventListener("message", this.handleMessage.bind(this));

    this.socket.addEventListener("close", (event) => {
      this.isConnecting = false;
      console.log("WebSocket connection closed", event.code, event.reason);
      
      // Attempt to reconnect with exponential backoff
      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        this.reconnectAttempts++;
        const delay = Math.min(30000, this.reconnectDelay * Math.pow(1.5, this.reconnectAttempts - 1));
        
        console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
        setTimeout(() => this.connect(), delay);
      } else {
        console.error("Max reconnection attempts reached");
        this.notifyListeners("connection", { status: "failed" });
      }
    });

    this.socket.addEventListener("error", (error) => {
      console.error("WebSocket error:", error);
      this.notifyListeners("error", { error });
    });
  }

  private handleMessage(event: MessageEvent): void {
    try {
      // Try to parse as JSON first
      const data = JSON.parse(event.data);
      // Pass the parsed data to the appropriate listeners based on message type
      this.notifyListeners(data.type, data);
    } catch (error) {
      // If it's not JSON, handle as a regular message
      if (typeof event.data === 'string') {
        this.notifyListeners("text", event.data);
      }
    }
  }

  private processQueue(): void {
    if (this.messageQueue.length === 0) return;
    
    // Process all queued messages
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      this.doSendMessage(message);
    }
  }

  private doSendMessage(message: any): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(typeof message === 'string' ? message : JSON.stringify(message));
    } else {
      // If we tried to send directly but socket isn't open, add it back to the queue
      this.messageQueue.push(message);
    }
  }

  public sendMessage(message: any): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.doSendMessage(message);
    } else {
      // Queue the message if socket isn't ready
      this.messageQueue.push(message);
      
      // Try to connect if not already connecting
      if (!this.isConnecting && this.socket?.readyState !== WebSocket.CONNECTING) {
        this.connect();
      }
    }
  }

  public addListener(type: string, callback: (data: any) => void): void {
    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set());
    }
    this.listeners.get(type)?.add(callback);
  }

  public removeListener(type: string, callback: (data: any) => void): void {
    this.listeners.get(type)?.delete(callback);
  }

  private notifyListeners(type: string, data: any): void {
    this.listeners.get(type)?.forEach(callback => callback(data));
  }

  public isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN;
  }
  
  public waitForConnection(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.isConnected()) {
        resolve();
        return;
      }
      
      const connectionListener = (data: any) => {
        if (data.status === "connected") {
          this.removeListener("connection", connectionListener);
          resolve();
        } else if (data.status === "failed") {
          this.removeListener("connection", connectionListener);
          reject(new Error("Failed to connect to WebSocket"));
        }
      };
      
      this.addListener("connection", connectionListener);
      
      // Start connection if not already connecting
      if (!this.isConnecting && this.socket?.readyState !== WebSocket.CONNECTING) {
        this.connect();
      }
    });
  }
} 