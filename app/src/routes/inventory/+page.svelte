<script lang="ts">
  import { onMount } from "svelte";
  import InventoryTable from "./components/InventoryTable.svelte";
  import ExtendedItemCard from "./components/ExtendedItemCard.svelte";
  import { createInventoryStore } from "./services/inventory.svelte";
  
  // --- Constants ---
  const itemsPerPage = 50;

  // 1. Initialize the store
  const inventory = createInventoryStore();

  // 2. Component State
  let selectedItemId = $state<number | null>(null);
  let isOpen = $state(false);
  let activeDrawer = $state<'add' | 'qr'>('add');
  let currentPosition = $state(0);

  // 3. Derived State
  let displayedItems = $derived(
    inventory.filteredItems.slice(currentPosition, currentPosition + itemsPerPage)
  );

  // 4. Lifecycle
  onMount(() => {
    inventory.fetchData();
  });

  // 5. Explicitly typed handlers (Fixes: "implicitly has any type")
  function handleSelect(id: number) {
    selectedItemId = id;
  }

  function handleToggleDrawer(type: 'add' | 'qr') {
    activeDrawer = type;
    isOpen = true;
  }
</script>

{#if !selectedItemId}
  <InventoryTable 
    items={displayedItems} 
    totalItems={inventory.filteredItems.length}
    bind:searchTerm={inventory.searchTerm}
    bind:currentPosition={currentPosition}
    onSelect={handleSelect}
  />
{:else}
  <ExtendedItemCard 
    item={inventory.items.find(i => i.id === selectedItemId)} 
    onClose={() => selectedItemId = null}
    onUpdate={inventory.updateItem}
    onDelete={inventory.deleteItem}
  />
{/if}
