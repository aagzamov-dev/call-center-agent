export const API_BASE = '';  // Empty = same origin, goes through Vite proxy
export const WS_URL = `ws://${window.location.host}/ws`;

export const SEVERITY_ORDER: Record<string, number> = {
  critical: 0, high: 1, medium: 2, low: 3, info: 4,
};

export const KIND_ICONS: Record<string, string> = {
  alert: '🔔',
  agent_plan: '🤖',
  tool_result: '🔧',
  action_exec: '⚡',
  ticket: '🎫',
  message: '💬',
  human_reply: '👤',
  status_change: '🔄',
  note: '📝',
};
