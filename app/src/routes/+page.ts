// +page.ts  (root route — redirects / → /inventory if logged in, /login if not)
export const ssr = false;
export const prerender = false;

import { goto } from '$app/navigation';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
  const res = await fetch('/api/me', { credentials: 'include' });

  if (!res.ok) {
    await goto('/login');
    return {};
  }

  // Only the root "/" path should bounce to /inventory.
  // All other pages are guarded individually via the layout.
  await goto('/inventory');
  return {};
};