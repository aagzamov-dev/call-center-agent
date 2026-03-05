import { useEffect, useRef } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { wsManager } from './useWebSocket';

export function useIncidentStream(incidentId: string | undefined) {
  const qc = useQueryClient();
  const unsubRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    if (!incidentId) return;

    unsubRef.current = wsManager.subscribe(incidentId, () => {
      qc.invalidateQueries({ queryKey: ['timeline', incidentId] });
      qc.invalidateQueries({ queryKey: ['incident', incidentId] });
      qc.invalidateQueries({ queryKey: ['tickets', incidentId] });
      qc.invalidateQueries({ queryKey: ['messages', incidentId] });
    });

    return () => { unsubRef.current?.(); };
  }, [incidentId, qc]);
}
