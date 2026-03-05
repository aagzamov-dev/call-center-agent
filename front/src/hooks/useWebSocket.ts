/**
 * WebSocket singleton — one connection shared across the entire app.
 * Components call wsManager.subscribe(incidentId, callback) to get events.
 */

import { WS_URL } from '../lib/constants';

export type WsCallback = (event: Record<string, unknown>) => void;

class WsManager {
  private ws: WebSocket | null = null;
  private listeners = new Map<string, Set<WsCallback>>();
  private retry = 0;
  private statusCb: ((s: string) => void) | null = null;

  connect(onStatus?: (s: string) => void) {
    if (onStatus) this.statusCb = onStatus;
    if (this.ws?.readyState === WebSocket.OPEN) return;
    this.statusCb?.('connecting');

    try {
      const socket = new WebSocket(WS_URL);
      socket.onopen = () => { this.statusCb?.('connected'); this.retry = 0; };
      socket.onclose = () => {
        this.statusCb?.('disconnected');
        const delay = Math.min(1000 * 2 ** this.retry, 15000);
        this.retry++;
        setTimeout(() => this.connect(), delay);
      };
      socket.onerror = () => { /* onclose will fire */ };
      socket.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data);
          if (msg.type === 'event' && msg.event?.incident_id) {
            const cbs = this.listeners.get(msg.event.incident_id);
            cbs?.forEach((cb) => { try { cb(msg.event); } catch {} });
          }
        } catch {}
      };
      this.ws = socket;
    } catch {
      this.statusCb?.('disconnected');
    }
  }

  subscribe(incidentId: string, cb: WsCallback): () => void {
    if (!this.listeners.has(incidentId)) {
      this.listeners.set(incidentId, new Set());
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'sub', incident_id: incidentId }));
      }
    }
    this.listeners.get(incidentId)!.add(cb);

    return () => {
      const set = this.listeners.get(incidentId);
      set?.delete(cb);
      if (set?.size === 0) {
        this.listeners.delete(incidentId);
        if (this.ws?.readyState === WebSocket.OPEN) {
          this.ws.send(JSON.stringify({ type: 'unsub', incident_id: incidentId }));
        }
      }
    };
  }
}

export const wsManager = new WsManager();
