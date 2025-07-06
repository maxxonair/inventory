<script>
  import { goto } from "$app/navigation";
  import { fetchUser } from "$lib/stores/auth.js"; // your shared auth state

  let username = "";
  let password = "";
  let error = "";

  async function login() {
    const res = await fetch("http://localhost:5000/login", {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    });

    if (res.ok) {
      await fetchUser(); // update global auth state
      goto("/"); // 🔁 redirect to home page
    } else {
      error = "Invalid credentials";
    }
  }
</script>

<form on:submit|preventDefault={login}>
  <input type="text" bind:value={username} placeholder="Username" />
  <input type="password" bind:value={password} placeholder="Password" />
  <button type="submit">Login</button>
  {#if error}<p class="text-red-500">{error}</p>{/if}
</form>
