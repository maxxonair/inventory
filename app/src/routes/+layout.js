import { redirect } from '@sveltejs/kit';
import { PUBLIC_INVENTORY_SERVER_URL } from '$env/static/public';

/** @type {import('./$types').LayoutLoad} */
export async function load({ fetch, url }) {
  // Don't protect the login page itself
  if (url.pathname === '/login') return;

  const res = await fetch(`${PUBLIC_INVENTORY_SERVER_URL}/me`, {
    credentials: 'include'
  });

  if (!res.ok) {
    throw redirect(302, '/login');
  }

  const user = await res.json();

  return { user };
}
