// +page.ts
export const ssr = false;
export const prerender = false;

import { goto } from '$app/navigation';
import type { PageLoad } from './$types';

export const load: PageLoad = async ({ fetch }) => {
  const res = await fetch(`/api/me`, { credentials: 'include' });

  if (!res.ok) {
    await goto('/login');
    return {}; // Prevents further execution
  }
  else { 
    await goto('/inventory');
  }

  const user = await res.json();
  return { user };
};