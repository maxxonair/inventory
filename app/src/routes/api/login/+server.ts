// src/routes/api/login/+server.ts
import { json } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request, fetch }) => {
  const INVENTORY_SERVER_URL = env.INVENTORY_SERVER_URL;
  const credentials = await request.json();

  const res = await fetch(`${INVENTORY_SERVER_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(credentials)
  });

  const data = await res.json();

  // Forward the Set-Cookie header exactly as Flask sends it
  const headers: Record<string, string> = {};
  const setCookie = res.headers.get('set-cookie');
  if (setCookie) headers['set-cookie'] = setCookie;

  return json(data, { status: res.status, headers });
};
