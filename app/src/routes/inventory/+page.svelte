<script lang="ts">
  import { onMount } from "svelte";
  import InventoryTable from "./components/InventoryTable.svelte";
  import ExtendedItemCard from "./components/ExtendedItemCard.svelte";
  import { createInventoryStore } from "./services/inventory.svelte";

  const itemsPerPage = 50;
  const inventory = createInventoryStore();

  let selectedItemId  = $state<number | null>(null);
  let currentPosition = $state(0);
  let storageLocations = $state<{ id: number; name: string }[]>([]);

  let displayedItems = $derived(
    inventory.filteredItems.slice(currentPosition, currentPosition + itemsPerPage)
  );

  // Resolve location IDs to names using fetched storageLocations
  let allStorageLocations = $derived(
    storageLocations
      .filter(sl => inventory.items.some(i => i.location === sl.id))
      .map(sl => ({ value: sl.id, name: sl.name }))
  );

  let allManufacturer = $derived(
    [...new Set(inventory.items.map(i => i.manufacturer).filter(Boolean))] as string[]
  );

  let allTags = $derived(
    [...new Set(
      inventory.items
        .flatMap(i => i.tags?.split(",").map((t: string) => t.trim()) ?? [])
        .filter(Boolean)
    )]
  );

  onMount(async () => {
    inventory.fetchData();
    try {
      const res = await fetch("/api/storage_locations");
      if (res.ok) storageLocations = await res.json();
    } catch (err) {
      console.error("Failed to fetch storage locations", err);
    }
  });

  function handleSelect(id: number) { selectedItemId = id; }
</script>

{#if !selectedItemId}
  <InventoryTable
    items={displayedItems}
    totalItems={inventory.filteredItems.length}
    bind:searchTerm={inventory.searchTerm}
    bind:currentPosition={currentPosition}
    onSelect={handleSelect}
    allStorageLocations={allStorageLocations}
    allManufacturer={allManufacturer}
    allTags={allTags}
  />
{:else}
  {@const selectedItem = inventory.items.find(i => i.id === selectedItemId)}
  {#if selectedItem}
    <ExtendedItemCard
      item={selectedItem}
      user_privilege={inventory.user_privilege}
      image_updated={inventory.image_updated}
      onClose={() => (selectedItemId = null)}
      onUpdate={inventory.updateItem}
      onDelete={inventory.deleteItem}
      onCheckout={inventory.checkoutItem}
      onReturn={inventory.returnItem}
      onPrint={inventory.printItemQrLabel}
    />
  {/if}
{/if}