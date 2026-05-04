<script lang="ts">
  import { onMount } from "svelte";
  import { page } from '$app/stores';
  import { DarkMode} from "flowbite-svelte";
  import { Tooltip } from 'flowbite-svelte';
  import {  CloseSidebarSolid, QrCodeOutline, ArrowLeftToBracketOutline, OpenDoorOutline, HomeSolid, GoToNextCellOutline } from "flowbite-svelte-icons";
  import { goto } from '$app/navigation';
  import { user, logout } from '$lib/stores/auth.js';
  import { browser } from '$app/environment';

  // Access the store’s value reactively
  const acc_user = $state(user);

  let isMobile = false;
  let activePage = $state("");
  let { toggleSidebar } = $props();
  let previousPath = $state('/');

  // Redirect if user is null (in case of hot navigation after logout)
  if (!acc_user) {login();}else{goto('/inventory');}

  // Use $derived to automatically update the activePage label based on the URL
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

  function reloadPage() {
    window.location.reload();
  }

  function login() {
    goto('/login');
  }


  function toggleQRScanner() {
    const currentPath = $page.url.pathname;
    if (browser) {
      if (currentPath === '/inventory/scan_qr') {
        goto(previousPath);
      } else {
        previousPath = currentPath;
        goto('/inventory/scan_qr');
      }
    }
  }

  // Currently not used, for future use on mobile
  onMount(() => {
    const ua = navigator.userAgent;
    isMobile = /Mobi|Android|iPhone|iPad|iPod/i.test(ua);
  });

</script>

<header class="dark:bg-slate-900 bg-slate-100">
  <div class="corner">
    <!-- <DarkMode /> -->
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
