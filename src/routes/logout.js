import { goto } from '$app/navigation';
import { user } from '$lib/stores/auth.js'; // your user store
import { page } from '$app/stores';

export async function logout() {
  await fetch('http://localhost:5000/logout', {
    method: 'POST',
    credentials: 'include'
  });

  // Clear auth state
  user.set(null); // or your store logic

  // Redirect to login
  goto('/login');
}
