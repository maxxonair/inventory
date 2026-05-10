<script>
  import Header from "./Header.svelte";
  import { onMount } from "svelte";
  import { fetchUser } from "$lib/stores/auth.js";
  import "../app.css";
  import { page } from '$app/stores';

  import { SidebarDropdownWrapper } from 'flowbite-svelte';
  import {
    HomeSolid, ArchiveSolid, CogSolid,
    ListOutline, PlusOutline,
    DownloadOutline, UserSettingsSolid
  } from 'flowbite-svelte-icons';

  let { children } = $props();
  let isMinimized = $state(false);

  const itemClass = "flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-slate-800 hover:bg-sky-100 dark:hover:bg-slate-700 dark:text-slate-300 dark:hover:text-slate-100 w-full";

  function toggleSidebar() {
    isMinimized = !isMinimized;
  }

  const isLoginPage = $derived($page.url.pathname === '/login');

  onMount(fetchUser);
</script>

{#if isLoginPage}
  {@render children()}
{:else}
  <div class="flex h-screen w-full bg-gray-50 dark:bg-gray-900 overflow-hidden">

    <!-- Sidebar -->
    <aside
      class="flex flex-col h-full transition-all duration-300 ease-in-out border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 z-40 flex-shrink-0 overflow-hidden"
      style:width={isMinimized ? '64px' : '280px'}
    >
      <div class="flex-1 px-3 py-4 overflow-y-auto overflow-x-hidden">
        <nav class="space-y-2">

          <!-- Inventory -->
          <SidebarDropdownWrapper label={isMinimized ? "" : "Inventory"} class="group">
            {#snippet icon()}<HomeSolid class="w-4 h-4 flex-shrink-0" />{/snippet}
            {#snippet arrowdown()}
              <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            {/snippet}
            {#snippet arrowup()}
              <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            {/snippet}

            <div class="pl-2 space-y-1">
              <a href="/inventory" class={itemClass}>
                <ListOutline class="w-4 h-4 flex-shrink-0" />
                {#if !isMinimized}<span>Inventory</span>{/if}
              </a>
              <a href="/inventory/add_item" class={itemClass}>
                <PlusOutline class="w-4 h-4 flex-shrink-0" />
                {#if !isMinimized}<span>Add Item</span>{/if}
              </a>
              <a href="/inventory/export_db" class={itemClass}>
                <DownloadOutline class="w-4 h-4 flex-shrink-0" />
                {#if !isMinimized}<span>Export</span>{/if}
              </a>
            </div>
          </SidebarDropdownWrapper>

          <!-- Storage Locations -->
          <SidebarDropdownWrapper label={isMinimized ? "" : "Storage Locations"} class="group">
            {#snippet icon()}<ArchiveSolid class="w-4 h-4 flex-shrink-0" />{/snippet}
            {#snippet arrowdown()}
              <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            {/snippet}
            {#snippet arrowup()}
              <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            {/snippet}

            <div class="pl-2 space-y-1">
              <a href="/storage" class={itemClass}>
                <ArchiveSolid class="w-4 h-4 flex-shrink-0" />
                {#if !isMinimized}<span>Storage Overview</span>{/if}
              </a>
              <a href="/storage/add_storage" class={itemClass}>
                <PlusOutline class="w-4 h-4 flex-shrink-0" />
                {#if !isMinimized}<span>Add Storage Location</span>{/if}
              </a>
            </div>
          </SidebarDropdownWrapper>

          <!-- Settings -->
          <SidebarDropdownWrapper label={isMinimized ? "" : "Settings"} class="group text-left">
            {#snippet icon()}<CogSolid class="w-4 h-4 flex-shrink-0" />{/snippet}
            {#snippet arrowdown()}
              <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            {/snippet}
            {#snippet arrowup()}
              <svg class="w-4 h-4 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            {/snippet}

            <div class="pl-2 space-y-1">
              <a href="/settings/user_management" class={itemClass}>
                <UserSettingsSolid class="w-4 h-4 flex-shrink-0" />
                {#if !isMinimized}<span>User Management</span>{/if}
              </a>
            </div>
          </SidebarDropdownWrapper>

        </nav>
      </div>
    </aside>

    <!-- Right side: Header + Content -->
    <div class="flex flex-col flex-1 min-w-0 overflow-hidden">
      <Header {toggleSidebar} />
      <main class="flex-1 overflow-y-auto px-4 py-6 md:px-8">
        {@render children()}
      </main>
    </div>

  </div>
{/if}