import client from './client';

export async function sendMessage(message: string, channel = 'chat') {
  const { data } = await client.post('/api/chat', { message, channel });
  return data as { reply: string; ticket: Record<string, unknown> | null; kb_results_count: number };
}

export async function transcribeVoice(audio: Blob) {
  const fd = new FormData();
  fd.append('audio', audio, 'recording.webm');
  const { data } = await client.post('/api/voice/transcribe', fd);
  return data as { transcript: string; reply: string; ticket: Record<string, unknown> | null };
}
