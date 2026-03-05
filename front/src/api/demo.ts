import client from './client';

export async function listScenarios() {
  const { data } = await client.get('/api/demo/scenarios');
  return data;
}

export async function runScenario(name: string) {
  const { data } = await client.post(`/api/demo/scenarios/${name}`);
  return data;
}
