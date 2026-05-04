<script lang="ts">
  import { onMount } from "svelte";
  import StorageTable from "./components/StorageTable.svelte";
  import ExtendedStorageCard from "./components/ExtendedStorageCard.svelte";
  import { createStorageLocationStore } from "./services/storage.svelte";
  
  // --- Constants ---
  const itemsPerPage = 50;

  // 1. Initialize the store
  const storage = createStorageLocationStore();

  // 2. Component State
  let selectedStorageId = $state<number | null>(null);
  let isOpen = $state(false);
  let activeDrawer = $state<'add' | 'qr'>('add');
  let currentPosition = $state(0);

  // 3. Derived State
  let displayedItems = $derived(
    storage.filteredstorage_locations.slice(currentPosition, currentPosition + itemsPerPage)
  );

  // 4. Lifecycle
  onMount(() => {
    storage.fetchData();
  });

  // 5. Explicitly typed handlers (Fixes: "implicitly has any type")
  function handleSelect(id: number) {
    selectedStorageId = id;
  }

  function handleToggleDrawer(type: 'add' | 'qr') {
    activeDrawer = type;
    isOpen = true;
  }
</script>

{#if !selectedStorageId}
  <StorageTable 
    storageLocations={displayedItems} 
    totalStorageLocations={storage.filteredstorage_locations.length}
    bind:searchTerm={storage.searchTerm}
    bind:currentPosition={currentPosition}
    onSelect={handleSelect}
    onToggleDrawer={handleToggleDrawer}
  />
{:else}
  <ExtendedStorageCard 
    item={storage.storage_locations.find(i => i.id === selectedStorageId)} 
    onClose={() => selectedStorageId = null}
    onUpdate={storage.updateStorageLocation}
    onDelete={storage.deleteStorageLocation}
  />
{/if}
