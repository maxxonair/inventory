import { writable } from 'svelte/store';
import { goto } from '$app/navigation';
import { PUBLIC_INVENTORY_SERVER_URL } from '$env/static/public';

export const user = writable(null);
export const message = writable('');

export async function fetchUser() {
  try {
    const res = await fetch(`${PUBLIC_INVENTORY_SERVER_URL}/me`, {
      credentials: 'include'
    });
    if (res.ok) {
      const data = await res.json();
      user.set(data.user);
    } else {
      user.set(null);
    }
  } catch {
    user.set(null);
  }
}

export async function logout() {
  await fetch(`${PUBLIC_INVENTORY_SERVER_URL}/logout`, {
    method: 'POST',
    credentials: 'include'
  });
  user.set(null);
  message.set('Logged out');
  goto('/login');
}
