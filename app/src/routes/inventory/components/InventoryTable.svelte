<script lang="ts">
  import { Input } from "flowbite-svelte";
  import { SearchOutline } from "flowbite-svelte-icons";
  import Pagination from "./Pagination.svelte";

  let {
    items,
    totalItems,
    searchTerm = $bindable(),
    currentPosition = $bindable(),
    onSelect,
  } = $props();

  const media_url = `/api/media/`;
</script>

<div class="w-full h-full bg-gray-50 dark:bg-gray-900 p-3 sm:p-5">

  <!-- Search bar -->
  <div class="flex justify-center mb-6">
    <div class="relative w-full max-w-md">
      <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
        <SearchOutline class="h-5 w-5 text-gray-500 dark:text-gray-400" />
      </div>
      <Input type="search" placeholder="Search items…" bind:value={searchTerm} class="pl-10" />
    </div>
  </div>

  <!-- Tile grid -->
  <div class="grid gap-4 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5">
    {#each items as item (item.id)}
      <button
        onclick={() => onSelect(item.id)}
        class="group flex flex-col bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-sm overflow-hidden hover:shadow-md hover:border-blue-400 dark:hover:border-blue-500 transition-all duration-150 text-left"
      >
        <!-- Image -->
        <div class="relative w-full aspect-square bg-gray-100 dark:bg-gray-700 overflow-hidden">
          <img
            src="{media_url}thumbnail_{item.image}.png"
            alt={item.name}
            class="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-150"
          />
          <!-- Availability badge overlaid on image -->
          <span class="absolute top-2 right-2 text-xs font-semibold px-2 py-0.5 rounded-full
            {item.is_checked_out
              ? 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
              : 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'}">
            {item.is_checked_out ? 'Checked out' : 'Available'}
          </span>
        </div>

        <!-- Info -->
        <div class="flex flex-col gap-0.5 px-3 py-2.5 border-t border-gray-100 dark:border-gray-700">
          <p class="text-sm font-semibold text-gray-900 dark:text-white truncate">{item.name}</p>
          <p class="text-xs text-gray-500 dark:text-gray-400 truncate">{item.manufacturer || '—'}</p>
        </div>
      </button>
    {/each}
  </div>

  <Pagination
    totalItems={totalItems}
    itemsPerPage={50}
    bind:currentPosition={currentPosition}
  />
</div>