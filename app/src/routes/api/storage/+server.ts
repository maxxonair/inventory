import { env } from '$env/dynamic/private';
import type { RequestHandler } from './$types';

export const GET: RequestHandler = async ({ fetch, cookies }) => {
  const INVENTORY_SERVER_URL = env.INVENTORY_SERVER_URL;
  const cookieHeader = cookies.getAll().map(c => `${c.name}=${c.value}`).join('; ');
  const res = await fetch(`${INVENTORY_SERVER_URL}/storage`, {
    headers: { cookie: cookieHeader }
  });

  return new Response(res.body, { status: res.status });
};