<script lang="ts">
  import { onMount } from "svelte";
  import { page } from "$app/state";
  import * as XLSX from 'xlsx';
  import { LogIn, LogOut, PlusCircle, ScanQrCode, FolderDown, Home } from 'lucide-svelte';
  // import logo from "$lib/images/svelte-logo.svg";
  import { user, logout } from '$lib/stores/auth.js';

  let isMobile = false;

  // Redirect if user is null (in case of hot navigation after logout)
  import { goto } from '$app/navigation';
  if (!user) {
    goto('/login');
  }

  function login() {
    goto('/login');
  }

  async function downloadExcel() {
    const itemRes = await fetch('http://localhost:5000/items', {
      credentials: 'include'
    });

    const items = await itemRes.json();
    if (!items.length) return;

    // Convert JSON to worksheet
    const worksheet = XLSX.utils.json_to_sheet(items);

    // Create a new workbook and append the worksheet
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, 'Inventory');

    // Generate timestamped filename
    const now = new Date();
    const timestamp = now.toISOString().replace(/[:.]/g, '-');
    const filename = `inventory-${timestamp}.xlsx`;

    // Write the workbook to a blob and trigger download
    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
    const blob = new Blob([excelBuffer], { type: 'application/octet-stream' });

    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  async function downloadCSV() {
    const itemRes = await fetch('http://localhost:5000/items', {
      credentials: 'include'
    });

    const items = await itemRes.json();

    // Exit if list is empty
    if (!items.length) return;

    // Extract CSV headers
    const headers = Object.keys(items[0]);

    // Format rows
    const csvRows = [
      headers.join(','), // header row
      ...items.map(item =>
        headers.map(header => `"${item[header] ?? ''}"`).join(',')
      )
    ];

    const csvContent = csvRows.join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);

    // Generate timestamped filename
    const now = new Date();
    const timestamp = now.toISOString().replace(/[:.]/g, '-');
    const filename = `inventory-${timestamp}.csv`;

    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  onMount(() => {
    const ua = navigator.userAgent;
    isMobile = /Mobi|Android|iPhone|iPad|iPod/i.test(ua);
  });

  // This protection is currently needed until /me stops returning 200 for logged 
  // out users
  $: isLoggedIn = $user !== null;
</script>

<header>
  <div class="corner">
  {#if isLoggedIn}
    <button class="download-button" on:click={downloadExcel}>
     <FolderDown size={20} />
    </button>
  {/if}
  </div>

  <nav>
    <svg viewBox="0 0 2 3" aria-hidden="true">
      <path d="M0,0 L1,2 C1.5,3 1.5,3 2,3 L2,0 Z" />
    </svg>
    <ul>
      {#if isLoggedIn}
        <li aria-current={page.url.pathname === "/scanner" ? "page" : undefined}>
          <a href="/scanner" aria-label="Scanner" title="Open QR Scanner">
            <ScanQrCode size={20} />
          </a>
        </li>
        <li aria-current={page.url.pathname === "/" ? "home" : undefined}>
          <a href="/" title="Inventory Home">
            <Home size={20} />
            <p class="button-label">Inventory</p>
          </a>
        </li>
        <li aria-current={page.url.pathname === "/studio" ? "page" : undefined}>
          <a href="/studio" aria-label="Studio" title="Add Item Section">
            <PlusCircle size={20} />
          </a>
        </li>
      {/if}
    </ul>
    <svg viewBox="0 0 2 3" aria-hidden="true">
      <path d="M0,0 L0,3 C0.5,3 0.5,3 1,2 L2,0 Z" />
    </svg>
  </nav>


  <div class="corner">

  <button class="icon-button" 
          on:click={isLoggedIn ? logout : login} 
          aria-label={isLoggedIn ? 'Logout' : 'Login'}
          title={isLoggedIn ? 'Log out' : 'Log in'}>
  {#if isLoggedIn}
    <LogOut class="icon" />
  {:else}
    <LogIn class="icon" />
  {/if}
</button>
  </div>
</header>

<style>
  header {
    display: flex;
    justify-content: space-between;
  }

  .tooltip-container {
    position: relative;
    display: inline-block;
  }

  .tooltip-text {
    visibility: hidden;
    background-color: black;
    color: white;
    text-align: center;
    border-radius: 4px;
    padding: 5px 8px;
    position: absolute;
    z-index: 1;
    bottom: 125%; /* Position above */
    left: 50%;
    transform: translateX(-50%);
    opacity: 0;
    transition: opacity 0.2s;
    white-space: nowrap;
  }

  .tooltip-container:hover .tooltip-text {
    visibility: visible;
    opacity: 1;
  }

  .corner {
    display: flex;
    gap: 0.5rem; /* space between buttons */
    align-items: center; /* optional: vertically align icons */
    justify-content: flex-end; /* if you want them to align right in the header */
  }

  .corner button {
    display: flex;
    gap: 0.5rem; /* space between buttons */
    align-items: center; /* optional: vertically align icons */
    justify-content: flex-end; /* if you want them to align right in the header */
  }

  .download-button{
    background-color: #252525;
    color:  #fa8d1f;
    border: none;
    border-radius: 9999px;
    padding: 0.5rem;
    margin: 0 auto 1rem; 
    cursor: pointer;
    transition: background-color 0.2s ease;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  }

  .button-label{
    color:  #fa8d1f;
  }

  .corner a {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 100%;
  }

  .corner img {
    width: 2em;
    height: 2em;
    object-fit: contain;
  }

  nav {
    display: flex;
    justify-content: center;
    --background: rgba(225, 225, 225, 0.7);
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

  nav a {
    display: flex;
    height: 100%;
    align-items: center;
    padding: 0 0.5rem;
    color: var(--color-text);
    font-weight: 700;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    text-decoration: none;
    transition: color 0.2s linear;
  }

  a:hover {
    color: var(--color-theme-1);
  }

  .icon-button {
    background-color: #f19812;
    border: none;
    border-radius: 9999px;
    padding: 0.5rem;
    cursor: pointer;
    transition: background-color 0.2s ease;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  }

  .icon-button:hover {
    background-color: #e0e0e0;
  }

  .icon {
    width: 24px;
    height: 24px;
    stroke: #333;
  }
</style>
