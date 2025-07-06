// src/lib/stores/auth.js
import { writable } from 'svelte/store';

export const user = writable(null);

export async function fetchUser() {
  const res = await fetch('http://localhost:5000/me', {
    credentials: 'include'
  });
  if (res.ok) {
    const data = await res.json();
    user.set(data.user);
  } else {
    user.set(null);
  }
}
