import { goto } from '$app/navigation';
import { user } from '$lib/stores/auth.js'; // your user store
import { page } from '$app/stores';
import { PUBLIC_INVENTORY_SERVER_URL } from '$env/static/public';

export async function logout() {
  await fetch(`${PUBLIC_INVENTORY_SERVER_URL}/logout`, {
    method: 'POST',
    credentials: 'include'
  });

  // Clear auth state
  user.set(null); 

  // Redirect to login
  goto('/login');
}
