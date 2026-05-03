<script lang="ts">
  import { TableSearch, Button } from "flowbite-svelte";
  import { PlusOutline, QrCodeOutline } from "flowbite-svelte-icons";
  import { Section } from "flowbite-svelte-blocks";
  import Pagination from "./Pagination.svelte";

  // Define the props
  let { 
    storageLocations,
    totalStorageLocations,
    searchTerm = $bindable(), 
    currentPosition = $bindable(),
    onSelect, 
    onToggleDrawer 
  } = $props();

</script>

<Section name="advancedTable" sectionClass="w-full h-full bg-gray-50 dark:bg-gray-900 p-3 sm:p-5">
  <TableSearch placeholder="Search" bind:inputValue={searchTerm}>
    {#snippet header()}
      <Button onclick={() => onToggleDrawer('add_storage')}>
        <PlusOutline class="mr-2 h-3.5 w-3.5" /> Add storage location
      </Button>
      <Button onclick={() => onToggleDrawer('scan_qr')}>
        <QrCodeOutline class="mr-2 h-3.5 w-3.5" /> Scan QR
      </Button>
    {/snippet}

    <div class="grid gap-4 p-2 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5">
      {#each storageLocations as item (item.id)}
        <button 
          class="flex flex-col items-center rounded-lg bg-slate-100 dark:bg-slate-700 p-2 hover:bg-sky-300 dark:hover:bg-sky-700"
          onclick={() => onSelect(item.id)}
        >
          <div class="mt-2 font-bold text-orange-500">{item.name}</div>
        </button>
      {/each}
    </div>

    {#snippet footer()}
      <Pagination 
        totalItems={totalStorageLocations} 
        itemsPerPage={50}
        bind:currentPosition={currentPosition} 
      />
    {/snippet}
  </TableSearch>
</Section>