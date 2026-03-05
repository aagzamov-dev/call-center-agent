import { create } from 'zustand';

interface AppState {
  wsStatus: 'connecting' | 'connected' | 'disconnected';
  setWsStatus: (s: AppState['wsStatus']) => void;
}

export const useAppStore = create<AppState>((set) => ({
  wsStatus: 'disconnected',
  setWsStatus: (wsStatus) => set({ wsStatus }),
}));
