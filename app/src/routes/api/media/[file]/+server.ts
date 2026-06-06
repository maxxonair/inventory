import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ params, fetch, cookies }) => {
  const INVENTORY_SERVER_URL = env.INVENTORY_SERVER_URL;
  const cookieHeader = cookies.getAll().map(c => `${c.name}=${c.value}`).join('; ');
  
  const file = params.file; // catches everything after /api/media/

  const res = await fetch(`${INVENTORY_SERVER_URL}/media/${file}`, {
    headers: { cookie: cookieHeader }
  });

  if (!res.ok) {
    return new Response(null, { status: res.status });
  }

  return new Response(res.body, {
    status: res.status,
    headers: {
      'Content-Type': res.headers.get('Content-Type') || 'image/png',
      'Cache-Control': res.headers.get('Cache-Control') || 'no-cache'
    }
  });
};