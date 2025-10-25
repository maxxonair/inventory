// Disable Server Side Rendering
export const ssr = false;
export const prerender = false;

import { redirect } from '@sveltejs/kit';
import { PUBLIC_INVENTORY_SERVER_URL } from '$env/static/public';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
  const res = await fetch(`${PUBLIC_INVENTORY_SERVER_URL}/me`, {
    credentials: 'include'
  });

  if (!res.ok) {
    throw redirect(302, '/login');
  }

  const response = await res.json();

  const user = response;
  
  return { user };
}