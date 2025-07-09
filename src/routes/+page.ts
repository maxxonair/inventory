// since there's no dynamic data here, we can prerender
// it so that it gets served as a static asset in production
export const prerender = true;

import { redirect } from '@sveltejs/kit';

export async function load({ fetch }) {
  const res = await fetch('http://localhost:5000/me', {
    credentials: 'include'
  });

  if (!res.ok) {
    throw redirect(302, '/login');
  }

  const user = await res.json();

  const itemRes = await fetch('http://localhost:5000/items', {
    credentials: 'include'
  });

  if (!itemRes.ok) {
    throw redirect(302, '/login');
  }

  const items = await itemRes.json();

  return { user, items };
}