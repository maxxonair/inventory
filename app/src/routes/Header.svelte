<script lang="ts">
  import { onMount } from "svelte";
  import { page } from "$app/state";
  import { DarkMode, Button} from "flowbite-svelte";
  import { Tooltip } from 'flowbite-svelte';
  import {  ArchiveSolid, ArrowLeftToBracketOutline, OpenDoorOutline, HomeSolid } from "flowbite-svelte-icons";
  import { goto } from '$app/navigation';
  import { user, logout } from '$lib/stores/auth.js';

  let isMobile = false;

  // Redirect if user is null (in case of hot navigation after logout)
  // Access the store’s value reactively
  // const acc_user = 'mrx'; // $state(user);
  // if (!acc_user) {
  //   goto('/login');
  // }

  goto('/inventory'); // Redirect to inventory page on load, adjust as needed

  function reloadPage() {
    window.location.reload();
  }

  function gotoInventory() {
    goto('/inventory');
  }

  function gotoStorage() {
    goto('/storage');
  }

  function login() {
    goto('/login');
  }

  // Currently not used, for future use on mobile
  onMount(() => {
    const ua = navigator.userAgent;
    isMobile = /Mobi|Android|iPhone|iPad|iPod/i.test(ua);
  });

</script>

<header class="dark:bg-slate-900 bg-slate-100">
  <div class="corner">
    <DarkMode />
  </div>

  <nav>
    {#if user}
      <button aria-current={page.url.pathname === "/inventory" ? "page" : undefined} class="py2 bg-slate-600 dark:bg-slate-800 text-red-500 hover:text-white border border-gray-800 hover:bg-gray-900 focus:ring-4 focus:outline-none focus:ring-gray-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2 dark:border-gray-600 dark:text-red-600 dark:hover:text-white dark:hover:bg-gray-600 dark:focus:ring-gray-800">
        <HomeSolid class="h-6 w-6" onclick={gotoInventory}/>
        <Tooltip placement="bottom" transitionParams={{ duration: 100 }}>
          View Inventory
        </Tooltip>
      </button>
      <button aria-current={page.url.pathname === "/storage" ? "page" : undefined} class="py2 bg-slate-600 dark:bg-slate-800 text-red-500 hover:text-white border border-gray-800 hover:bg-gray-900 focus:ring-4 focus:outline-none focus:ring-gray-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2 dark:border-gray-600 dark:text-red-600 dark:hover:text-white dark:hover:bg-gray-600 dark:focus:ring-gray-800">
        <ArchiveSolid class="h-6 w-6" onclick={gotoStorage}/>
        <Tooltip placement="bottom" transitionParams={{ duration: 100 }}>
          View Storage Locations
        </Tooltip>
      </button>
    {/if}
  </nav>

  <div class="corner">
    <Button class="p-2! md-2" onclick={user ? logout : login} 
            aria-label={user ? 'Logout' : 'Login'}
            title={user ? 'Log out' : 'Log in'}>
      {#if user}
        <OpenDoorOutline class="h-6 w-6" />
        <Tooltip placement="bottom" transitionParams={{ duration: 100 }}>
            Log out
        </Tooltip>
      {:else}
        <ArrowLeftToBracketOutline class="h-6 w-6" />
        <Tooltip placement="bottom" transitionParams={{ duration: 100 }}>
            Log in
        </Tooltip>
      {/if}
    </Button>
  </div>
</header>

<style>
  header {
    display: flex;
    justify-content: space-between;
  }

  .corner {
    display: flex;
    gap: 0.5rem;
    padding: 0.5rem;
    align-items: center;
  }

  nav {
    display: flex;
    justify-content: center;
    --background: rgba(162, 162, 162, 0.7);
  }
</style>
