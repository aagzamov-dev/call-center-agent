import client from './client';

export async function sendEmail(body: { incident_id: string; to: string; cc?: string; subject: string; body: string }) {
  const { data } = await client.post('/api/email/send', body);
  return data;
}

export async function sendChat(body: { incident_id: string; channel: string; message: string }) {
  const { data } = await client.post('/api/chat/send', body);
  return data;
}

export async function transcribeVoice(audio: Blob, incidentId?: string, sender?: string) {
  const fd = new FormData();
  fd.append('audio', audio, 'recording.webm');
  const params = new URLSearchParams();
  if (incidentId) params.set('incident_id', incidentId);
  if (sender) params.set('sender', sender);
  const { data } = await client.post(`/api/voice/transcribe?${params}`, fd);
  return data;
}

export async function getMessages(incidentId: string, channel?: string) {
  const params: Record<string, string> = {};
  if (channel) params.channel = channel;
  const { data } = await client.get(`/api/incidents/${incidentId}/messages`, { params });
  return data;
}
