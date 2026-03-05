import client from './client';

export async function listIncidents(status?: string) {
  const params: Record<string, string> = {};
  if (status) params.status = status;
  const { data } = await client.get('/api/incidents', { params });
  return data;
}

export async function getIncident(id: string) {
  const { data } = await client.get(`/api/incidents/${id}`);
  return data;
}
