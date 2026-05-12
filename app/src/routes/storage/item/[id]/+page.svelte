<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { page } from '$app/stores';
  import { get } from 'svelte/store';
  import { Spinner, Alert } from 'flowbite-svelte';
  import ExtendedStorageCard from '../../components/ExtendedStorageCard.svelte';

  const storageId = Number(get(page).params.id);

  let item         = $state<any>(null);
  let loading      = $state(true);
  let error_msg    = $state('');

  onMount(async () => {
    // Auth check
    const userRes = await fetch('/api/me', { credentials: 'include' });
    if (!userRes.ok) { goto('/login'); return; }

    // Fetch the storage location — backend now accepts ?id= query param
    try {
      const res = await fetch(`/api/storage?id=${storageId}`, { credentials: 'include' });
      if (!res.ok) {
        error_msg = res.status === 404
          ? `Storage location #${storageId} not found.`
          : 'Failed to load storage location.';
        return;
      }
      item = await res.json();
    } catch (err) {
      console.error(err);
      error_msg = 'Network error loading storage location.';
    } finally {
      loading = false;
    }
  });

  async function handleUpdate(id: number, data: any) {
    const res = await fetch('/api/update_storage', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, ...data }),
    });
    if (res.ok) {
      // Refresh item from server so card reflects saved state
      const refreshed = await fetch(`/api/storage?id=${id}`, { credentials: 'include' });
      if (refreshed.ok) item = await refreshed.json();
    }
  }

  async function handleDelete(id: number) {
    const res = await fetch('/api/delete_storage', {
      method: 'POST',
      credentials: 'include',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id }),
    });
    if (res.ok) goto('/storage');
  }

  function handleClose() {
    goto('/storage');
  }
</script>

<svelte:head>
  <title>{item?.name ?? `Storage #${storageId}`} — Inventory</title>
</svelte:head>

{#if loading}
  <div class="flex justify-center items-center h-64">
    <Spinner size="10" />
  </div>

{:else if error_msg}
  <div class="max-w-lg mx-auto mt-16">
    <Alert color="red">{error_msg}</Alert>
    <button
      class="mt-4 text-sm text-blue-600 dark:text-blue-400 hover:underline"
      onclick={() => goto('/storage')}
    >
      ← Back to Storage
    </button>
  </div>

{:else if !item}
  <div class="max-w-lg mx-auto mt-16">
    <Alert color="yellow">Storage location #{storageId} not found.</Alert>
    <button
      class="mt-4 text-sm text-blue-600 dark:text-blue-400 hover:underline"
      onclick={() => goto('/storage')}
    >
      ← Back to Storage
    </button>
  </div>

{:else}
  <ExtendedStorageCard
    {item}
    onClose={handleClose}
    onUpdate={handleUpdate}
    onDelete={handleDelete}
  />
{/if}