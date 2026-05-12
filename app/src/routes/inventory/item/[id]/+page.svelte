<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { get } from 'svelte/store';
  import { Spinner, Alert } from 'flowbite-svelte';
  import ExtendedItemCard from '../../components/ExtendedItemCard.svelte';
  import { createInventoryStore } from '../../services/inventory.svelte';

  const itemId = Number(get(page).params.id);
  const inventory = createInventoryStore();

  // Once fetchData completes, find the specific item from the loaded list
  let item = $derived(inventory.items.find(i => i.id === itemId) ?? null);

  onMount(async () => {
    // fetchData loads user, user_privilege, and all items in one go
    await inventory.fetchData();
  });

  async function handleUpdate(id: number, data: any): Promise<String> {
    return await inventory.updateItem(id, data);
  }

  async function handleDelete(id: number) {
    await inventory.deleteItem(id);
    goto('/inventory');
  }

  function handleClose() {
    goto('/inventory');
  }
</script>

<svelte:head>
  <title>{item?.name ?? `Item #${itemId}`} — Inventory</title>
</svelte:head>

{#if inventory.loading}
  <div class="flex justify-center items-center h-64">
    <Spinner size="10" />
  </div>

{:else if inventory.error_msg}
  <div class="max-w-lg mx-auto mt-16">
    <Alert color="red">{inventory.error_msg}</Alert>
    <button
      class="mt-4 text-sm text-blue-600 dark:text-blue-400 hover:underline"
      onclick={() => goto('/inventory')}
    >
      ← Back to Inventory
    </button>
  </div>

{:else if !item}
  <div class="max-w-lg mx-auto mt-16">
    <Alert color="yellow">Item #{itemId} not found.</Alert>
    <button
      class="mt-4 text-sm text-blue-600 dark:text-blue-400 hover:underline"
      onclick={() => goto('/inventory')}
    >
      ← Back to Inventory
    </button>
  </div>

{:else}
  <ExtendedItemCard
    {item}
    user_privilege={inventory.user_privilege}
    image_updated={inventory.image_updated}
    onClose={handleClose}
    onUpdate={handleUpdate}
    onDelete={handleDelete}
    onCheckout={inventory.checkoutItem}
    onReturn={inventory.returnItem}
    onPrint={inventory.printItemQrLabel}
  />
{/if}