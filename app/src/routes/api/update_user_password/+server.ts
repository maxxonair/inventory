import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

export const POST: RequestHandler = async ({ request, fetch, cookies }) => {
  const INVENTORY_SERVER_URL = env.INVENTORY_SERVER_URL;
  const body = await request.text();
  const cookieHeader = cookies.getAll().map(c => `${c.name}=${c.value}`).join('; ');

  const res = await fetch(`${INVENTORY_SERVER_URL}/update_user_password`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', cookie: cookieHeader },
    body
  });

  return new Response(res.body, { status: res.status });
};
