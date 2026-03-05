import client from './client';

export async function injectAlert(alert: {
  alert_id: string; host: string; service: string;
  severity: string; title: string; description: string; tags?: Record<string, string>;
}) {
  const { data } = await client.post('/api/alerts', alert);
  return data;
}
