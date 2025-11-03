// Disable Server Side Rendering
export const ssr = false;
export const prerender = false;

import { redirect } from '@sveltejs/kit';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
  const res = await fetch(`/api/me`, { credentials: 'include' });
  if (!res.ok) throw redirect(302, '/login');
  const user = await res.json();
  return { user };
};