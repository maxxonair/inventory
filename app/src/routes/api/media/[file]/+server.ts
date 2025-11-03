// /api/media/+server.ts
import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';


export const GET: RequestHandler = async ({ params, fetch }) => {
  const INVENTORY_SERVER_URL = env.INVENTORY_SERVER_URL;
  const file = params.file; // e.g. "abc123.png"

  const res = await fetch(`${INVENTORY_SERVER_URL}/media/${file}`);

  return new Response(res.body, {
    status: res.status,
    headers: {
      'Content-Type': res.headers.get('Content-Type') || 'image/png',
      'Cache-Control': res.headers.get('Cache-Control') || 'no-cache'
    }
  });
};