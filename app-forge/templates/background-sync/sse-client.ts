// lib/sse-client.ts
// EventSource wrapper with reconnection and typed event handling.

type EventHandler = (data: unknown) => void;

export class SSEClient {
  private eventSource: EventSource | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 10;
  private listeners: Map<string, Set<EventHandler>> = new Map();
  private url = '';
  private token = '';

  connect(url: string, token: string): void {
    this.url = url;
    this.token = token;

    this.eventSource = new EventSource(`${url}?token=${token}`);

    this.eventSource.onopen = () => {
      this.reconnectAttempts = 0;
    };

    this.eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        const handlers = this.listeners.get(data.type);
        handlers?.forEach((handler) => handler(data));
      } catch {
        // Non-JSON message, ignore
      }
    };

    this.eventSource.onerror = () => {
      this.eventSource?.close();
      this.eventSource = null;

      if (this.reconnectAttempts < this.maxReconnectAttempts) {
        const delay = Math.min(1000 * 2 ** this.reconnectAttempts, 30000);
        this.reconnectAttempts++;
        setTimeout(() => this.connect(this.url, this.token), delay);
      }
    };
  }

  on(eventType: string, handler: EventHandler): void {
    if (!this.listeners.has(eventType)) {
      this.listeners.set(eventType, new Set());
    }
    this.listeners.get(eventType)!.add(handler);
  }

  off(eventType: string, handler: EventHandler): void {
    this.listeners.get(eventType)?.delete(handler);
  }

  get isConnected(): boolean {
    return this.eventSource?.readyState === EventSource.OPEN;
  }

  disconnect(): void {
    this.eventSource?.close();
    this.eventSource = null;
    this.reconnectAttempts = 0;
  }
}

// Singleton
export const sseClient = new SSEClient();
