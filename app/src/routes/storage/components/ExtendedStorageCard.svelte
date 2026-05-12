<script lang="ts">
  import { Button, CloseButton, Label, Input, Textarea, Badge, Spinner } from "flowbite-svelte";
  import { Undo2, Trash2, SquarePen, Check, X, AlertTriangle } from "lucide-svelte";
  import type { StorageLocation } from "../services/storage.svelte";
  import { onMount } from "svelte";
  import { PrinterOutline } from "flowbite-svelte-icons";
  import { goto } from '$app/navigation';
  import { printQR } from '$lib/niimbot';

  let { item, onClose, onUpdate, onDelete } = $props();

  let isEditing = $state(false);
  let showDeleteConfirm = $state(false);
  let deleteError = $state("");
  let printError = $state("");
  let editedStorage = $state<StorageLocation>({ ...item });

  let locationItems = $state<{ id: number; name: string; manufacturer?: string; is_checked_out?: boolean }[]>([]);
  let locationItemsLoading = $state(true);
  let locationItemsError = $state("");

  $effect(() => {
    editedStorage = { ...item };
  });

  onMount(async () => {
    try {
      const res = await fetch(`/api/storage_items`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: item.id }),
      });
      if (!res.ok) throw new Error("Failed to fetch items");
      locationItems = await res.json();
    } catch (err) {
      locationItemsError = "Could not load items for this location.";
    } finally {
      locationItemsLoading = false;
    }
  });

  function handleSave() {
    onUpdate(item.id, editedStorage);
    isEditing = false;
  }

  function handleCancel() {
    editedStorage = { ...item };
    isEditing = false;
  }

  async function handlePrintQrLabel() {
    printError="";
    const qrString = `istr;id;${item.id}`;
    try {
      await printQR(qrString);
    } catch (printError) {
      console.error("Printer error:", printError);
      throw printError;
    }
  }

  async function confirmDelete() {
    deleteError = "";
    try {
      const res = await fetch("/api/delete_storage", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: item.id }),
      });
      if (!res.ok) throw new Error("Delete failed");
      onDelete(item.id);
      onClose();
    } catch (err) {
      deleteError = "Failed to delete this location. Please try again.";
      showDeleteConfirm = false;
    }
  }
</script>

<div class="w-full bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">

  <!-- Top bar -->
  <div class="flex justify-between items-center px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
    <Button color="alternative" size="sm" onclick={onClose}>
      <Undo2 class="mr-2 h-4 w-4" /> Back to Storage Overview
    </Button>
    <div class="flex items-center gap-2">
      {#if showDeleteConfirm}
        <!-- intentionally empty — confirmation is inline below -->
      {:else if isEditing}
        <Button color="green" size="sm" onclick={handleSave}>
          <Check class="mr-2 h-4 w-4" /> Save Changes
        </Button>
        <Button color="alternative" size="sm" onclick={handleCancel}>
          <X class="mr-2 h-4 w-4" /> Cancel
        </Button>
      {:else}
        <Button color="blue" size="sm" onclick={() => (isEditing = true)}>
          <SquarePen class="mr-2 h-4 w-4" /> Edit
        </Button>
        <Button color="red" size="sm" onclick={() => (showDeleteConfirm = true)}>
          <Trash2 class="mr-2 h-4 w-4" /> Delete
        </Button>
      {/if}
      <Button color="blue" size="sm" onclick={handlePrintQrLabel}>
          <PrinterOutline class="mr-2 h-4 w-4" /> Print Label
        </Button>
      <CloseButton onclick={onClose} class="ml-2" />
    </div>
  </div>

  <!-- Delete error banner -->
  {#if deleteError}
    <div class="flex items-center gap-2 px-6 py-3 text-sm text-red-800 bg-red-50 dark:bg-gray-800 dark:text-red-400 border-b border-red-200 dark:border-red-800">
      <svg class="w-4 h-4 shrink-0" fill="currentColor" viewBox="0 0 20 20">
        <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5Zm1 13a1 1 0 1 1-2 0 1 1 0 0 1 2 0Zm-1-8a1 1 0 0 1 1 1v3a1 1 0 1 1-2 0V6.5a1 1 0 0 1 1-1Z"/>
      </svg>
      {deleteError}
    </div>
  {/if}

  <!-- Print (QR Label) error banner -->
  {#if printError}
    <div class="flex items-center gap-2 px-6 py-3 text-sm text-red-800 bg-red-50 dark:bg-gray-800 dark:text-red-400 border-b border-red-200 dark:border-red-800">
      <svg class="w-4 h-4 shrink-0" fill="currentColor" viewBox="0 0 20 20">
        <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5Zm1 13a1 1 0 1 1-2 0 1 1 0 0 1 2 0Zm-1-8a1 1 0 0 1 1 1v3a1 1 0 1 1-2 0V6.5a1 1 0 0 1 1-1Z"/>
      </svg>
      {printError}
    </div>
  {/if}

  <!-- Delete confirmation panel -->
  {#if showDeleteConfirm}
    <div class="flex flex-col items-center justify-center gap-5 px-6 py-12 bg-red-50 dark:bg-gray-800 border-b border-red-100 dark:border-gray-700">
      <div class="flex items-center justify-center w-14 h-14 rounded-full bg-red-100 dark:bg-red-900">
        <Trash2 class="w-7 h-7 text-red-600 dark:text-red-400" />
      </div>
      <div class="text-center">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">Delete "{item.name}"?</h3>
        <p class="mt-1 text-sm text-gray-500 dark:text-gray-400 max-w-sm">
          This will permanently remove this storage location from the database. This action cannot be undone.
        </p>
        {#if locationItems.length > 0}
          <p class="mt-2 text-sm font-medium text-red-600 dark:text-red-400">
            Warning: {locationItems.length} item{locationItems.length === 1 ? '' : 's'} are currently stored here.
          </p>
        {/if}
      </div>
      <div class="flex gap-3">
        <Button color="red" onclick={confirmDelete}>
          <Trash2 class="mr-2 h-4 w-4" /> Yes, delete permanently
        </Button>
        <Button color="alternative" onclick={() => (showDeleteConfirm = false)}>
          <X class="mr-2 h-4 w-4" /> Cancel
        </Button>
      </div>
    </div>

  {:else}
    <div class="flex flex-col md:flex-row">

      <!-- Left: icon + meta -->
      <div class="md:w-64 lg:w-80 shrink-0 bg-gray-100 dark:bg-gray-800 flex flex-col items-center justify-center p-8 border-b md:border-b-0 md:border-r border-gray-200 dark:border-gray-700 gap-4">
        <div class="w-32 h-32 rounded-2xl bg-gray-200 dark:bg-gray-700 flex items-center justify-center shadow-inner">
          <svg class="w-16 h-16 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 7H4a2 2 0 00-2 2v10a2 2 0 002 2h16a2 2 0 002-2V9a2 2 0 00-2-2zm-9 9H7m6 0h-2m5-4H7"/>
          </svg>
        </div>
        <Badge color="dark" class="text-xs font-mono">ID: {item.id}</Badge>
        {#if item.date_added}
          <p class="text-xs text-gray-400 dark:text-gray-500">Added {item.date_added}</p>
        {/if}

        <!-- Item count -->
        <div class="w-full pt-4 border-t border-gray-200 dark:border-gray-700 text-center">
          <p class="text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-1">Items stored</p>
          {#if locationItemsLoading}
            <Spinner size="4" />
          {:else if locationItemsError}
            <p class="text-xs text-red-500">—</p>
          {:else}
            <p class="text-3xl font-bold text-gray-900 dark:text-white">{locationItems.length}</p>
            {#if locationItems.filter(i => i.is_checked_out).length > 0}
              <p class="text-xs text-gray-400 dark:text-gray-500 mt-1">
                {locationItems.filter(i => i.is_checked_out).length} checked out
              </p>
            {/if}
          {/if}
        </div>
      </div>

      <!-- Right: info / edit + items list -->
      <div class="flex-1 p-6 lg:p-8 flex flex-col gap-6">

        {#if isEditing}
          <div class="space-y-5 max-w-lg">
            <div>
              <Label for="loc-name" class="mb-1.5 text-sm font-medium text-gray-700 dark:text-gray-300">Location Name</Label>
              <Input id="loc-name" bind:value={editedStorage.name} placeholder="e.g. Warehouse A — Shelf 3" />
            </div>
            <div>
              <Label for="loc-desc" class="mb-1.5 text-sm font-medium text-gray-700 dark:text-gray-300">Description</Label>
              <Textarea id="loc-desc" bind:value={editedStorage.description} rows={4} placeholder="Notes about capacity, access, temperature…" />
            </div>
          </div>
        {:else}
          <div>
            <h2 class="text-2xl font-semibold text-gray-900 dark:text-white">{item.name}</h2>
            <p class="mt-1 text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
              {item.description || "No description provided."}
            </p>
          </div>

          {#if item.tags}
            <div class="pt-4 border-t border-gray-100 dark:border-gray-700">
              <p class="text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-2">Tags</p>
              <div class="flex flex-wrap gap-2">
                {#each item.tags.split(',') as tag}
                  <Badge color="blue">{tag.trim()}</Badge>
                {/each}
              </div>
            </div>
          {/if}
        {/if}

        <!-- Items at this location -->
        <div class="pt-4 border-t border-gray-100 dark:border-gray-700">
          <p class="text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-3">Items at this location</p>

          {#if locationItemsLoading}
            <div class="flex items-center gap-2 text-sm text-gray-400">
              <Spinner size="4" /> Loading…
            </div>
          {:else if locationItemsError}
            <p class="text-sm text-red-500">{locationItemsError}</p>
          {:else if locationItems.length === 0}
            <p class="text-sm text-gray-400 dark:text-gray-500 italic">No items stored here yet.</p>
          {:else}
            <div class="divide-y divide-gray-100 dark:divide-gray-700 rounded-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
              {#each locationItems as locationItem}
                <div
                  role="button"
                  tabindex="0"
                  class="flex items-center justify-between px-4 py-2.5 bg-white dark:bg-gray-900 hover:bg-sky-50 dark:hover:bg-gray-800 transition-colors cursor-pointer"
                  onclick={() => goto(`/inventory/item/${locationItem.id}`)}
                  onkeydown={(e) => e.key === 'Enter' && goto(`/inventory/item/${locationItem.id}`)}
                >
                  <div class="min-w-0">
                    <p class="text-sm font-medium text-gray-900 dark:text-white truncate">{locationItem.name}</p>
                    {#if locationItem.manufacturer}
                      <p class="text-xs text-gray-400 dark:text-gray-500 truncate">{locationItem.manufacturer}</p>
                    {/if}
                  </div>
                  <Badge color={locationItem.is_checked_out ? "red" : "green"} class="ml-3 shrink-0">
                    {locationItem.is_checked_out ? "Checked out" : "Available"}
                  </Badge>
                </div>
              {/each}
            </div>
          {/if}
        </div>

      </div>
    </div>
  {/if}
</div>