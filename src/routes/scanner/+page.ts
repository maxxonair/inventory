import { dev } from '$app/environment';

// we don't need any JS on this page, though we'll load
// it in dev so that we get hot module replacement
export const csr = dev;

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

  return { user };
}
