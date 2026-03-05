import client from './client';

export async function runAgentStep(incidentId: string, hint?: string) {
  const { data } = await client.post(`/api/incidents/${incidentId}/agent/step`, { hint });
  return data;
}

export async function sendHumanReply(incidentId: string, sender: string, body: string) {
  const { data } = await client.post(`/api/incidents/${incidentId}/human-reply`, { sender, body });
  return data;
}
