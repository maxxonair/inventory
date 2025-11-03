import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request, fetch }) => {
  const INVENTORY_SERVER_URL = env.INVENTORY_SERVER_URL;
  const formData = await request.formData();

  const res = await fetch(`${INVENTORY_SERVER_URL}/image_upload`, {
    method: 'POST',
    body: formData
  });

  return new Response(res.body, { status: res.status });
};
