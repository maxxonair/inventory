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

  <!-- Centered half-width search bar, no label -->
  <div class="flex justify-center mb-6">
    <div class="relative w-1/2">
      <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
        <SearchOutline class="h-5 w-5 text-gray-500 dark:text-gray-400" />
      </div>
      <Input
        type="search"
        placeholder="Search"
        bind:value={searchTerm}
        class="pl-10"
      />
    </div>
  </div>

  <!-- Full-width tile grid -->
  <div class="grid gap-4 p-2 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 w-full">
    {#each items as item (item.id)}
      <button
        class="flex flex-col items-center rounded-lg bg-slate-100 dark:bg-slate-700 p-2 hover:bg-sky-300 dark:hover:bg-sky-700"
        onclick={() => onSelect(item.id)}
      >
        <div class="mb-2 p-1 {item.is_checked_out ? 'bg-red-500' : 'bg-green-500'} rounded text-xs font-bold">
          {item.is_checked_out ? 'Checked Out' : 'Available'}
        </div>
        <img
          src="{media_url}thumbnail_{item.image}.png"
          alt={item.name}
          class="w-full rounded-lg border border-slate-900"
        />
        <div class="mt-2 font-bold text-orange-500">{item.name}</div>
        <div class="text-sm dark:text-slate-300">{item.manufacturer || 'N/A'}</div>
      </button>
    {/each}
  </div>

  <Pagination
    totalItems={totalItems}
    itemsPerPage={50}
    bind:currentPosition={currentPosition}
  />

</div>