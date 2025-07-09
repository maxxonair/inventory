import { redirect } from '@sveltejs/kit';

/** @type {import('./$types').LayoutLoad} */
export async function load({ fetch, url }) {
  // Don't protect the login page itself
  if (url.pathname === '/login') return;

  const res = await fetch('http://localhost:5000/me', {
    credentials: 'include'
  });

  if (!res.ok) {
    throw redirect(302, '/login');
  }

  const user = await res.json();

  return { user };
}
