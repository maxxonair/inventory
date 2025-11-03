import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

/**
 * Proxy Server-Sent Events from backend to frontend
 */
export const GET: RequestHandler = async ({ fetch, request, cookies }) => {
  const INVENTORY_SERVER_URL = env.INVENTORY_SERVER_URL;

  // Forward browser cookies to backend
  const cookieHeader = cookies.getAll()
    .map(c => `${c.name}=${c.value}`)
    .join('; ');

  // Connect to backend SSE stream
  const backendResponse = await fetch(`${INVENTORY_SERVER_URL}/qr_events`, {
    headers: { Cookie: cookieHeader },
  });

  if (!backendResponse.ok || !backendResponse.body) {
    return new Response('Failed to connect to backend events', { status: 502 });
  }

  // Pipe backend stream directly to the frontend
  return new Response(backendResponse.body, {
    status: 200,
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      Connection: 'keep-alive',
      // Optional: allow CORS if frontend served from different origin
      'Access-Control-Allow-Origin': '*',
    },
  });
};
