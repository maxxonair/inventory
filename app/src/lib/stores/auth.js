
import { writable } from 'svelte/store';
import { goto } from '$app/navigation';
 
export const user = writable(null);
export const message = writable('');
 
// Fetch the current logged-in user
export async function fetchUser() {
  try {
    const res = await fetch('/api/me', {
      credentials: 'include'
    });
    if (res.ok) {
      const data = await res.json();
      // /api/me now returns { id, username, user_privileges } directly
      user.set(data);
    } else {
      user.set(null);
    }
  } catch (err) {
    console.error('Error fetching user:', err);
    user.set(null);
  }
}
 
// Log user out
export async function logout() {
  try {
    const res = await fetch('/api/logout', {
      method: 'POST',
      credentials: 'include'
    });
    if (res.ok) {
      user.set(null);
      message.set('Logged out');
      goto('/login');
    } else {
      console.error('Logout failed:', await res.text());
    }
  } catch (err) {
    console.error('Error during logout:', err);
  }
}
