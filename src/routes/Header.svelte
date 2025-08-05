<script lang="ts">
  import { onMount } from "svelte";
  import { page } from "$app/state";
  import { LogIn, LogOut, PlusCircle, ScanQrCode, FolderDown, Home } from 'lucide-svelte';
  // import logo from "$lib/images/svelte-logo.svg";
  import { user, logout } from '$lib/stores/auth.js';
  import { DarkMode, Button} from "flowbite-svelte";
  import {  ArrowLeftToBracketOutline, OpenDoorOutline, HomeSolid } from "flowbite-svelte-icons";

  let isMobile = false;

  // Redirect if user is null (in case of hot navigation after logout)
  import { goto } from '$app/navigation';
  if (!user) {
    goto('/login');
  }

  function reloadPage() {
    window.location.reload();
  }

  function login() {
    goto('/login');
  }

  onMount(() => {
    const ua = navigator.userAgent;
    isMobile = /Mobi|Android|iPhone|iPad|iPod/i.test(ua);
  });

  // This protection is currently needed until /me stops returning 200 for logged 
  // out users
  $: isLoggedIn = $user !== null;
</script>

<header class="dark:bg-slate-900 bg-slate-100">
  <div class="corner">
  <DarkMode />
  </div>

  <nav>
    <svg viewBox="0 0 2 3" aria-hidden="true">
      <path d="M0,0 L1,2 C1.5,3 1.5,3 2,3 L2,0 Z" />
    </svg>
    <ul>
      {#if isLoggedIn}

        <!--   Add additional pages here  -->

        <!-- <li aria-current={page.url.pathname === "/scanner" ? "page" : undefined}>
          <a href="/scanner" aria-label="Scanner" title="Open QR Scanner">
            <ScanQrCode size={20} />
          </a>
        </li> -->

        <li aria-current={page.url.pathname === "/" ? "home" : undefined}>
          <button class="p-2! bg-slate-600 dark:bg-slate-800 text-red-500 hover:text-white border border-gray-800 hover:bg-gray-900 focus:ring-4 focus:outline-none focus:ring-gray-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center me-2 mb-2 dark:border-gray-600 dark:text-red-600 dark:hover:text-white dark:hover:bg-gray-600 dark:focus:ring-gray-800">
            <HomeSolid class="h-6 w-6" onclick={reloadPage}/>
          </button>
        </li>

      {/if}
    </ul>
    <svg viewBox="0 0 2 3" aria-hidden="true">
      <path d="M0,0 L0,3 C0.5,3 0.5,3 1,2 L2,0 Z" />
    </svg>
  </nav>


  <div class="corner">

  <Button class="p-2! md-2" onclick={isLoggedIn ? logout : login} 
          aria-label={isLoggedIn ? 'Logout' : 'Login'}
          title={isLoggedIn ? 'Log out' : 'Log in'}>
    {#if isLoggedIn}
      <OpenDoorOutline class="h-6 w-6" />
    {:else}
      <ArrowLeftToBracketOutline class="h-6 w-6" />
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
    gap: 0.5rem; /* space between buttons */
    padding: 0.5rem;
    align-items: center; /* optional: vertically align icons */
    justify-content: flex-end; /* if you want them to align right in the header */
  }

  nav {
    display: flex;
    justify-content: center;
    --background: rgba(162, 162, 162, 0.7);
  }

  svg {
    width: 2em;
    height: 3em;
    display: block;
  }

  path {
    fill: var(--background);
  }

  ul {
    position: relative;
    padding: 0;
    margin: 0;
    height: 3em;
    display: flex;
    justify-content: center;
    align-items: center;
    list-style: none;
    background: var(--background);
    background-size: contain;
  }

  li {
    position: relative;
    height: 100%;
  }

  li[aria-current="page"]::before {
    --size: 6px;
    content: "";
    width: 0;
    height: 0;
    position: absolute;
    top: 0;
    left: calc(50% - var(--size));
    border: var(--size) solid transparent;
    border-top: var(--size) solid var(--color-theme-1);
  }
</style>
