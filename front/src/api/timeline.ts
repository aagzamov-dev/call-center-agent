import client from './client';

export async function getTimeline(incidentId: string, kind?: string) {
  const params: Record<string, string> = {};
  if (kind) params.kind = kind;
  const { data } = await client.get(`/api/incidents/${incidentId}/timeline`, { params });
  return data;
}
