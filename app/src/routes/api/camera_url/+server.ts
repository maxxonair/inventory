import { json } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

const INVENTORY_SERVER_URL = env.INVENTORY_SERVER_URL;

export const GET = async ({ fetch }) => {
  const res = await fetch(`${INVENTORY_SERVER_URL}/camera_url`);
  const data = await res.json();
  return json(data);
};
