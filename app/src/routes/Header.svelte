<script lang="ts">
  import { onMount } from "svelte";
  import { page } from '$app/stores';
  import { DarkMode } from "flowbite-svelte";
  import { Tooltip } from 'flowbite-svelte';
  import { CloseSidebarSolid, QrCodeOutline, ArrowLeftToBracketOutline, OpenDoorOutline } from "flowbite-svelte-icons";
  import { goto } from '$app/navigation';
  import { user, logout } from '$lib/stores/auth.js';
  import { get } from 'svelte/store';

  let isMobile = false;
  let activePage = $state("");
  let { toggleSidebar } = $props();
  let previousPath = $state('/');

  const currentPath = $derived($page.url.pathname);

  $effect(() => {
    if (currentPath === '/') activePage = "Inventory Management System";
    else if (currentPath === '/inventory') activePage = "Inventory";
    else if (currentPath === '/inventory/add_item') activePage = "Add Inventory Item";
    else if (currentPath === '/inventory/scan_qr') activePage = "Scan QR Label";
    else if (currentPath === '/storage') activePage = "Storage Locations";
    else if (currentPath === '/storage/add_storage') activePage = "Add Storage Location";
    else if (currentPath === '/settings') activePage = "Settings";
    else activePage = "App";
  });

  function login() {
    goto('/login');
  }

  function toggleQRScanner() {
    if (currentPath === '/inventory/scan_qr') {
      goto(previousPath);
    } else {
      previousPath = currentPath;
      goto('/inventory/scan_qr');
    }
  }

  onMount(() => {
    isMobile = /Mobi|Android|iPhone|iPad|iPod/i.test(navigator.userAgent);

    // Read the actual store value, not the store object
    const currentUser = get(user);
    if (!currentUser) {
      goto('/login');
    }
    // Removed the else goto('/inventory') — no need to redirect
    // if the user is already authenticated and on a valid page
  });
</script>

<header class="dark:bg-slate-900 bg-slate-100">
  <div class="corner">
    <button 
      class="py2 px-1 py-1 bg-slate-600 dark:bg-slate-800 text-slate-100 hover:text-white border border-gray-800 hover:bg-gray-900 focus:ring-4 focus:outline-none focus:ring-gray-300 font-medium rounded-lg text-sm text-center me-2 mb-2 dark:border-gray-600 dark:text-slate-100 dark:hover:text-white dark:hover:bg-gray-600 dark:focus:ring-gray-800"
    >
    <CloseSidebarSolid class="p-2! md-2" onclick={toggleSidebar}/>
    </button>
  </div>

  <nav>
    <div class="py2 text-slate-900 dark:text-slate-200 text-lg">
      {activePage || "Inventory Management System"}
    </div>
  </nav>

  <div class="corner">
    <div class="py2 px-1 py-1">
      <DarkMode />
    </div>

    <button 
      class="py2 px-1 py-1 bg-slate-600 dark:bg-slate-800 text-slate-100 hover:text-white border border-gray-800 hover:bg-gray-900 focus:ring-4 focus:outline-none focus:ring-gray-300 font-medium rounded-lg text-sm text-center me-2 mb-2 dark:border-gray-600 dark:text-slate-100 dark:hover:text-white dark:hover:bg-gray-600 dark:focus:ring-gray-800">
      <QrCodeOutline class="p-2! md-2" onclick={toggleQRScanner}/>
      <Tooltip placement="bottom" transitionParams={{ duration: 100 }}>
        Scan QR Code
      </Tooltip>
    </button>

    <button class="py2 px-1 py-1 bg-sky-600 dark:bg-sky-800 text-sky-100 hover:text-white border border-gray-800 hover:bg-gray-900 focus:ring-4 focus:outline-none focus:ring-gray-300 font-medium rounded-lg text-sm text-center me-2 mb-2 dark:border-gray-600 dark:text-sky-100 dark:hover:text-white dark:hover:bg-gray-600 dark:focus:ring-gray-800">
      {#if user}
        <OpenDoorOutline class="p-1! md-1" onclick={logout}/>
        <Tooltip placement="bottom" transitionParams={{ duration: 100 }}>
            Log out
        </Tooltip>
      {:else}
        <ArrowLeftToBracketOutline class="p-1! md-1" onclick={login}/>
        <Tooltip placement="bottom" transitionParams={{ duration: 100 }}>
            Log in
        </Tooltip>
      {/if}
    </button>

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
    gap: 0.5rem;
    padding: 0.5rem;
    --background: rgba(162, 162, 162, 0.7);
  }
</style>
