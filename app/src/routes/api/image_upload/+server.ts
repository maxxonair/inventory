import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request }) => {
  const INVENTORY_SERVER_URL = env.INVENTORY_SERVER_URL;
  
  // Get the raw formData from the incoming request
  const formData = await request.formData();

  // Forward it — do NOT set Content-Type header manually.
  // fetch() will set it automatically with the correct multipart boundary.
  const res = await fetch(`${INVENTORY_SERVER_URL}/image_upload`, {
    method: 'POST',
    body: formData,
  });

  const data = await res.json();
  return new Response(JSON.stringify(data), { status: res.status });
};