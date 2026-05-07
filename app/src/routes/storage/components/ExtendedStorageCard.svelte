<script lang="ts">
  import { Button, CloseButton, Label, Input, Textarea, Badge } from "flowbite-svelte";
  import { Undo2, Trash2, SquarePen, Check, X } from "lucide-svelte";
  import type { StorageLocation } from "../services/storage.svelte";

  let { item, onClose, onUpdate, onDelete } = $props();

  let isEditing = $state(false);
  let editedStorage = $state<StorageLocation>({ ...item });

  $effect(() => {
    editedStorage = { ...item };
  });

  function handleSave() {
    onUpdate(item.id, editedStorage);
    isEditing = false;
  }

  function handleCancel() {
    editedStorage = { ...item };
    isEditing = false;
  }
</script>

<div class="w-full bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">

  <!-- Top bar -->
  <div class="flex justify-between items-center px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
    <Button color="alternative" size="sm" onclick={onClose}>
      <Undo2 class="mr-2 h-4 w-4" /> Back to Storage Overview
    </Button>
    <div class="flex items-center gap-2">
      {#if isEditing}
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
        <Button color="red" size="sm" onclick={onDelete}>
          <Trash2 class="mr-2 h-4 w-4" /> Delete
        </Button>
      {/if}
      <CloseButton onclick={onClose} class="ml-2" />
    </div>
  </div>

  <div class="flex flex-col md:flex-row">

    <!-- Left: Image + ID badge -->
    <div class="md:w-64 lg:w-80 shrink-0 bg-gray-100 dark:bg-gray-800 flex flex-col items-center justify-center p-8 border-b md:border-b-0 md:border-r border-gray-200 dark:border-gray-700 gap-4">
      <div class="w-32 h-32 rounded-2xl bg-gray-200 dark:bg-gray-700 flex items-center justify-center shadow-inner">
        <!-- Placeholder icon; swap for <img> when you have a real image source -->
        <svg class="w-16 h-16 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M20 7H4a2 2 0 00-2 2v10a2 2 0 002 2h16a2 2 0 002-2V9a2 2 0 00-2-2zm-9 9H7m6 0h-2m5-4H7"/>
        </svg>
      </div>
      <Badge color="dark" class="text-xs font-mono">ID: {item.id}</Badge>
      {#if item.date_added}
        <p class="text-xs text-gray-400 dark:text-gray-500">Added {item.date_added}</p>
      {/if}
    </div>

    <!-- Right: Info / Edit fields -->
    <div class="flex-1 p-6 lg:p-8">
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
        <div class="space-y-1 mb-6">
          <h2 class="text-2xl font-semibold text-gray-900 dark:text-white">{item.name}</h2>
          <p class="text-sm text-gray-500 dark:text-gray-400 leading-relaxed">
            {item.description || "No description provided."}
          </p>
        </div>

        <!-- Meta grid -->
        {#if item.tags}
          <div class="mt-6 pt-6 border-t border-gray-100 dark:border-gray-700">
            <p class="text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-2">Tags</p>
            <div class="flex flex-wrap gap-2">
              {#each item.tags.split(',') as tag}
                <Badge color="blue">{tag.trim()}</Badge>
              {/each}
            </div>
          </div>
        {/if}
      {/if}
    </div>
  </div>
</div>