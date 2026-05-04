<script lang="ts">
  import { TableSearch, Button } from "flowbite-svelte";
  import { PlusOutline, QrCodeOutline } from "flowbite-svelte-icons";
  import { Section } from "flowbite-svelte-blocks";
  import Pagination from "./Pagination.svelte";

  // Define the props
  let { 
    items,           // The ALREADY sliced/paginated items to display
    totalItems,
    searchTerm = $bindable(), 
    currentPosition = $bindable(),
    onSelect, 
    onToggleDrawer 
  } = $props();

  const media_url = `/api/media/`;
</script>

<Section name="advancedTable" sectionClass="w-full h-full bg-gray-50 dark:bg-gray-900 p-3 sm:p-5">
  <TableSearch placeholder="        Search" bind:inputValue={searchTerm}>

    <div class="grid gap-4 p-2 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5">
      {#each items as item (item.id)}
        <button 
          class="flex flex-col items-center rounded-lg bg-slate-100 dark:bg-slate-700 p-2 hover:bg-sky-300 dark:hover:bg-sky-700"
          onclick={() => onSelect(item.id)}
        >
          <div class="mb-2 p-1 {item.is_checked_out ? 'bg-red-500' : 'bg-green-500'} rounded text-xs font-bold">
            {item.is_checked_out ? 'Checked Out' : 'Available'}
          </div>
          <img src="{media_url}thumbnail_{item.image}.png" alt={item.name} class="w-full rounded-lg border border-slate-900" />
          <div class="mt-2 font-bold text-orange-500">{item.name}</div>
          <div class="text-sm dark:text-slate-300">{item.manufacturer || 'N/A'}</div>
        </button>
      {/each}
    </div>

    {#snippet footer()}
      <Pagination 
        totalItems={totalItems} 
        itemsPerPage={50}
        bind:currentPosition={currentPosition} 
      />
    {/snippet}
  </TableSearch>
</Section>