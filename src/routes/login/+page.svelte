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

<!-- <form on:submit|preventDefault={login}>
  <input type="text" bind:value={username} placeholder="Username" />
  <input type="password" bind:value={password} placeholder="Password" />
  <button class="px-8 py-2 rounded-full bg-gradient-to-b from-blue-500 to-blue-600 text-white focus:ring-2 focus:ring-blue-400 hover:shadow-xl transition duration-200">
    Login
  </button>
  {#if error}<p class="text-red-500">{error}</p>{/if}
</form> -->

<div class="page-container">
  <form class="login-box" on:submit|preventDefault={login}>
    <input
      type="text"
      placeholder="User Name"
      bind:value={username}
      required
    />
    <input
      type="password"
      placeholder="Password"
      bind:value={password}
      required
    />
    <button type="submit" class="px-8 py-2 rounded-full bg-gradient-to-b from-blue-500 to-blue-600 text-white focus:ring-2 focus:ring-blue-400 hover:shadow-xl transition duration-200">
      Log In
    </button>
    {#if error}<p class="text-red-500">{error}</p>{/if}
  </form>
</div>

<style>
  .page-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100vh; /* full viewport height */
  }

  .login-box {
    background-color: white;
    padding: 2rem;
    border-radius: 1rem;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 400px;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  input {
    padding: 0.75rem;
    border: 1px solid #ccc;
    border-radius: 0.5rem;
    font-size: 1rem;
    background-color: #eef2f7;
  }

  input:focus {
    background-color: #ffffff;
    border-color: #2c7be5;
    outline: none;
  }

  button {
    padding: 0.75rem;
    background-color: #2a2b2a;
    color: white;
    font-weight: bold;
    border: none;
    border-radius: 0.5rem;
    cursor: pointer;
    transition: background-color 0.2s;
  }

  button:hover {
    background-color: #e59500;
  }

  .error {
    color: red;
    margin-top: 10px;
  }
</style>
    