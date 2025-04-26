// WebSocket service for managing socket connection
export class SocketService {
  private static instance: SocketService;
  private socket: WebSocket | null = null;
  private listeners: Map<string, Set<(data: any) => void>> = new Map();

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
    this.socket = new WebSocket("ws://localhost:8090");

    this.socket.addEventListener("open", () => {
      console.log("WebSocket connection established");
      // Notify any listeners that we're connected
      this.notifyListeners("connection", { status: "connected" });
    });

    this.socket.addEventListener("message", this.handleMessage.bind(this));

    this.socket.addEventListener("close", () => {
      console.log("WebSocket connection closed");
      // Attempt to reconnect after a delay
      setTimeout(() => this.connect(), 3000);
    });

    this.socket.addEventListener("error", (error) => {
      console.error("WebSocket error:", error);
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

  public sendMessage(message: any): void {
    if (this.socket?.readyState === WebSocket.OPEN) {
      this.socket.send(typeof message === 'string' ? message : JSON.stringify(message));
    } else {
      console.error("WebSocket is not connected");
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
} 