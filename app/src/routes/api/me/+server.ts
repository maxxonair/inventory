// src/routes/api/me/+server.ts
import { env } from '$env/dynamic/private';
import type { RequestHandler } from '@sveltejs/kit';

export const GET: RequestHandler = async ({ fetch, request }) => {
  const INVENTORY_SERVER_URL = env.INVENTORY_SERVER_URL;

  // Forward the request body and headers (cookies) from the client
  const res = await fetch(`${INVENTORY_SERVER_URL}/me`, {
    method: 'GET',
    headers: request.headers
  });

  const body = await res.text();
  return new Response(body, { status: res.status });
};
