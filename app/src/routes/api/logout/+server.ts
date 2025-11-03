// src/routes/api/logout/+server.ts
import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ fetch, cookies }) => {
  const INVENTORY_SERVER_URL = env.INVENTORY_SERVER_URL;

  // Forward existing cookies to backend logout
  const cookieHeader = cookies.getAll().map(c => `${c.name}=${c.value}`).join('; ');
  const res = await fetch(`${INVENTORY_SERVER_URL}/logout`, {
    method: 'POST',
    headers: { cookie: cookieHeader }
  });

  // Delete local cookies — MUST specify path!
  cookies.delete('session', { path: '/' });

  return new Response(null, { status: res.status });
};