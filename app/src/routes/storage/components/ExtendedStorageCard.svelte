<script lang="ts">
  import { Button, CloseButton, Label, Input, Textarea } from "flowbite-svelte";
  import { Undo2, Printer, Trash2, SquarePen } from "lucide-svelte";
  import type { StorageLocation } from "../services/storage.svelte";

  let { item, onClose, onUpdate, onDelete } = $props();
  let isEditing = $state(false);
  // 1. Initialize with an empty-ish object or the initial item
  let editedStorage = $state<StorageLocation>({ ...item });

  // 2. Sync editedStorage if the 'item' prop changes from the parent
  // This satisfies Svelte 5's requirement for tracking local references.
  $effect(() => {
    editedStorage = { ...item };
  });

  function handleSave() {
    onUpdate(item.id, editedStorage);
    isEditing = false;
  }
</script>

<div class="w-full p-4 bg-slate-200 dark:bg-slate-800 rounded-lg">
  <div class="flex justify-between items-center mb-6">
    <Button color="alternative" onclick={onClose}>
      <Undo2 class="mr-2 h-4 w-4" /> Back to Storage Overview
    </Button>
    <CloseButton onclick={onClose} />
  </div>

  <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
    <!-- Image Section -->
    <div>
      <div class="mt-4 flex gap-2">
        <Button color="blue" onclick={() => (isEditing = !isEditing)}>
          <SquarePen class="mr-2 h-4 w-4" /> Edit Details
        </Button>
        <Button color="red" onclick={onDelete}>
          <Trash2 class="mr-2 h-4 w-4" /> Delete
        </Button>
      </div>
    </div>

    <!-- Info Section -->
    <div class="space-y-4">
      {#if isEditing}
        <Label>Storage Location Name</Label>
        <Input bind:value={editedStorage.name} />
        <Label>Description</Label>
        <Textarea bind:value={editedStorage.description} />
        <Button onclick={handleSave}>Save Changes</Button>
      {:else}
        <h2 class="text-3xl font-bold">{item.name}</h2>
        <p class="text-gray-500">{item.description}</p>
      {/if}
    </div>
  </div>
</div>