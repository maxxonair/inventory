<script>
  import { goto } from "$app/navigation";
  import { fetchUser } from "$lib/stores/auth.js";
  import {  FloatingLabelInput, Button} from 'flowbite-svelte';

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
      await fetchUser();
      goto("/");
    } else {
      error = "Invalid credentials";
    }
  }
</script>

<svelte:head>
  <title>Inventory Login</title>
  <meta name="description" content="Inventory Login page" />
</svelte:head>

<div class="flex items-center justify-center min-h-screen bg-gray-100 w-screen h-screen dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
  <form class="max-w-sm mx-auto" on:submit|preventDefault={login}>
    <div class="mb-5 flex items-center justify-center" >
      <label for="login" class="block mb-2 text-xl text-gray-900 dark:text-gray-200">Inventory Login</label>
    </div>
    <div class="mb-5">
      <FloatingLabelInput clearable 
                          variant="outlined" 
                          id="user" 
                          name="user" 
                          type="text" 
                          class="bg-white dark:bg-slate-900 rounded-lg"
                          required 
                          bind:value={username} >
        Name
      </FloatingLabelInput>
    </div>
    <div class="mb-5">
      <FloatingLabelInput clearable 
                          variant="outlined" 
                          id="password" 
                          name="password" 
                          type="password" 
                          required 
                          class="bg-white dark:bg-slate-900 rounded-lg"
                          bind:value={password} >
        Password
      </FloatingLabelInput>
    </div>
    <Button type="submit" 
            class=" w-full">
          Login
    </Button>
  </form>
</div>