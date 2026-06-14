import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request, cookies }) => {
  const INVENTORY_SERVER_URL = env.INVENTORY_SERVER_URL;

  const formData = await request.formData();
  const cookieHeader = cookies.getAll().map(c => `${c.name}=${c.value}`).join('; ');

  const res = await fetch(`${INVENTORY_SERVER_URL}/image_upload`, {
    method: 'POST',
    body: formData,
    headers: {
      cookie: cookieHeader
    }
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: 'Upload failed' }));
    return new Response(JSON.stringify(error), { status: res.status });
  }

  const data = await res.json();
  return new Response(JSON.stringify(data), { status: res.status });
};