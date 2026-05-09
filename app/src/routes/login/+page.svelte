<script>
  import { error } from '@sveltejs/kit';
  import { goto } from "$app/navigation";
  import { fetchUser } from "$lib/stores/auth.js";
  import { FloatingLabelInput, Button } from 'flowbite-svelte';

  let username = $state("");
  let password = $state("");
  let error_msg = $state("");

  async function login() {
    const res = await fetch(`api/login`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    });
    if (res.ok) {
      error_msg = "";
      await fetchUser();
      goto("/inventory");
    } else {
      const data = await res.json();
      error_msg = data.error || "Login failed";
    }
  }
</script>

<svelte:head>
  <title>Inventory Login</title>
  <meta name="description" content="Inventory Login page" />
</svelte:head>

<div class="flex items-center justify-center min-h-screen w-screen bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900">
  <div class="w-full max-w-sm mx-4">

    <!-- Card -->
    <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 border border-gray-200 dark:border-gray-700">

      <!-- Header -->
      <div class="flex flex-col items-center mb-8">
        <!-- Icon -->
        <div class="w-14 h-14 bg-blue-600 rounded-xl flex items-center justify-center mb-4 shadow-md">
          <svg class="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
          </svg>
        </div>
        <h1 class="text-2xl font-semibold text-gray-900 dark:text-white tracking-tight">Inventory</h1>
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">Sign in to your account</p>
      </div>

      <!-- Form -->
      <form on:submit|preventDefault={login} class="space-y-5">
        <FloatingLabelInput
          clearable
          variant="outlined"
          id="user"
          name="user"
          type="text"
          class="bg-white dark:bg-gray-700 rounded-lg"
          required
          bind:value={username}
        >
          Username
        </FloatingLabelInput>

        <FloatingLabelInput
          clearable
          variant="outlined"
          id="password"
          name="password"
          type="password"
          required
          class="bg-white dark:bg-gray-700 rounded-lg"
          bind:value={password}
        >
          Password
        </FloatingLabelInput>

        <!-- Error message -->
        {#if error_msg}
          <div class="flex items-center gap-2 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 text-sm rounded-lg px-4 py-3">
            <svg class="w-4 h-4 shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd" />
            </svg>
            {error_msg}
          </div>
        {/if}

        <Button type="submit" class="w-full mt-2">
          Sign in
        </Button>
      </form>
    </div>

    <!-- Footer -->
    <p class="text-center text-xs text-gray-400 dark:text-gray-600 mt-6">
      Inventory Management System
    </p>
  </div>
</div>