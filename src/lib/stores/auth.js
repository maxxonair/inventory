import { writable } from 'svelte/store';

export const user = writable(null);
export const message = writable(null);

export async function fetchUser() {
  try {
    const res = await fetch('http://localhost:5000/me', {
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
  await fetch('http://localhost:5000/logout', {
    method: 'POST',
    credentials: 'include'
  });
  user.set(null);
  message.set('Logged out');
}
