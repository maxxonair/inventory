import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ fetch }) => {
  const INVENTORY_CAMERA_URL = env.INVENTORY_CAMERA_URL;
  // Connect privately to your Flask camera stream
  const res = await fetch(`${INVENTORY_CAMERA_URL}/stream`, {
    method: 'GET'
  });

  // Forward the response as a live stream
  return new Response(res.body, {
    status: res.status,
    headers: {
      'Content-Type': res.headers.get('Content-Type') || 'multipart/x-mixed-replace; boundary=frame',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
    }
  });
};
