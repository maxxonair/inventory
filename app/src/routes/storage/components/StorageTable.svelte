<script lang="ts">
  import { Input } from "flowbite-svelte";
  import { SearchOutline } from "flowbite-svelte-icons";
  import Pagination from "./Pagination.svelte";
  import { get } from 'svelte/store';
  import { goto } from '$app/navigation';
  import { fetchUser, user } from "$lib/stores/auth.js";
  import { onMount } from "svelte";

  let {
    filteredStorageLocations,
    totalStorageLocations,
    searchTerm = $bindable(),
    currentPosition = $bindable(),
    onSelect,
  } = $props();

  onMount(async () => {
    // Wait for the session check to complete before checking auth state.
    // This prevents the race where the store is still null when the
    // Header's onMount runs and incorrectly redirects to /login.
    await fetchUser();

    // Central auth guard: redirect to /login on any protected page if not logged in.
    if (!get(user)) {
      goto('/login');
    }
  });
</script>

<div class="w-full h-full bg-gray-50 dark:bg-gray-900 p-3 sm:p-5">

  <!-- Search bar -->
  <div class="flex justify-center mb-6">
    <div class="relative w-full max-w-md">
      <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
        <SearchOutline class="h-5 w-5 text-gray-500 dark:text-gray-400" />
      </div>
      <Input type="search" placeholder="Search locations…" bind:value={searchTerm} class="pl-10" />
    </div>
  </div>

  <!-- Tile grid -->
  <div class="grid gap-4 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5">
    {#each filteredStorageLocations as item (item.id)}
      <button
        onclick={() => onSelect(item.id)}
        class="group flex flex-col bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-sm overflow-hidden hover:shadow-md hover:border-blue-400 dark:hover:border-blue-500 transition-all duration-150 text-left"
      >
        <!-- Icon area -->
        <div class="flex items-center justify-center w-full aspect-square bg-gray-100 dark:bg-gray-700 group-hover:bg-blue-50 dark:group-hover:bg-gray-600 transition-colors">
          <svg class="w-12 h-12 text-gray-400 dark:text-gray-500 group-hover:text-blue-400 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 7H4a2 2 0 00-2 2v10a2 2 0 002 2h16a2 2 0 002-2V9a2 2 0 00-2-2zm-9 9H7m6 0h-2m5-4H7"/>
          </svg>
        </div>

        <!-- Info -->
        <div class="flex flex-col gap-1 px-3 py-2.5 border-t border-gray-100 dark:border-gray-700">
          <p class="text-sm font-semibold text-gray-900 dark:text-white truncate">{item.name}</p>
          <div class="flex items-center justify-between">
            <span class="text-xs font-mono text-gray-400 dark:text-gray-500">ID: {item.id}</span>
            {#if item.date_added}
              <span class="text-xs text-gray-400 dark:text-gray-500">{item.date_added}</span>
            {/if}
          </div>
        </div>
      </button>
    {/each}
  </div>

  <div class="mt-4">
    <Pagination
      totalItems={totalStorageLocations}
      itemsPerPage={50}
      bind:currentPosition={currentPosition}
    />
  </div>
</div>