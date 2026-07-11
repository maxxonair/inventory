<script>
  import Header from "./Header.svelte";
  import { onMount } from "svelte";
  import { fetchUser, user } from "$lib/stores/auth.js";
  import { get } from 'svelte/store';
  import { goto } from '$app/navigation';
  import "../app.css";
  import { page } from '$app/stores';
  import { PRIVILEGE_ORDER } from './settings/settings.svelte';

  import { SidebarDropdownWrapper } from 'flowbite-svelte';
  import {
    HomeSolid, ArchiveSolid, CogSolid,
    ListOutline, PlusOutline,
    DownloadOutline, UserSettingsSolid,
    TagOutline
  } from 'flowbite-svelte-icons';

  let { children } = $props();
  let isMinimized = $state(false);

  function privilegeFromId(id) {
    return PRIVILEGE_ORDER[id] ?? 'GUEST';
  }

  // The auth store may hold either a string privilege or the raw DB integer
  // (user_privileges), so normalise it the same way the settings pages do.
  function normaliseUser(raw) {
    if (!raw) return null;
    const priv = raw.privilege ?? raw.user_privileges;
    return {
      id: raw.id,
      username: raw.username,
      privilege: typeof priv === 'number' ? privilegeFromId(priv) : priv,
    };
  }

  function rank(p) {
    return PRIVILEGE_ORDER.indexOf(p);
  }

  // Reads $user live (auto-subscribed store), so this stays correct once
  // fetchUser() resolves after mount and whenever the store changes.
  function isAtLeast(p) {
    const currentUser = normaliseUser($user);
    return currentUser ? rank(currentUser.privilege) >= rank(p) : false;
  }

  const itemClass = "flex items-center gap-2 px-3 py-2 rounded-lg text-sm text-slate-800 hover:bg-sky-100 dark:hover:bg-slate-700 dark:text-slate-300 dark:hover:text-slate-100 w-full";

  function toggleSidebar() {
    isMinimized = !isMinimized;
  }

  const isLoginPage = $derived($page.url.pathname === '/login');

  onMount(async () => {
    // Wait for the session check to complete before checking auth state.
    // This prevents the race where the store is still null when the
    // Header's onMount runs and incorrectly redirects to /login.
    await fetchUser();

    // Central auth guard: redirect to /login on any protected page if not logged in.
    if (!isLoginPage && !get(user)) {
      goto('/login');
    }
  });
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

          <!-- Settings (hidden entirely below DEVELOPER, since that's the
               lowest threshold of anything it can contain) -->
          {#if isAtLeast('DEVELOPER')}
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
                {#if isAtLeast('DEVELOPER')}
                  <a href="/settings/user_management" class={itemClass}>
                    <UserSettingsSolid class="w-4 h-4 flex-shrink-0" />
                    {#if !isMinimized}<span>User Management</span>{/if}
                  </a>
                {/if}
                {#if isAtLeast('MAINTAINER')}
                  <a href="/settings/categories" class={itemClass}>
                    <TagOutline class="w-4 h-4 flex-shrink-0" />
                    {#if !isMinimized}<span>Categories</span>{/if}
                  </a>
                {/if}
              </div>
            </SidebarDropdownWrapper>
          {/if}

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