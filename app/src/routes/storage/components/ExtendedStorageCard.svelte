<script lang="ts">
  import { Button, CloseButton, Label, Input, Textarea } from "flowbite-svelte";
  import { Undo2, Printer, Trash2, SquarePen } from "lucide-svelte";
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
</script>

<div class="w-full p-6 bg-slate-200 dark:bg-slate-800 rounded-lg">
  <!-- Header -->
  <div class="flex justify-between items-center mb-6">
    <Button color="alternative" onclick={onClose}>
      <Undo2 class="mr-2 h-4 w-4" /> Back to Storage Overview
    </Button>
    <CloseButton onclick={onClose} />
  </div>

  <!-- Body -->
  <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
    <!-- Actions Section -->
    <div class="flex gap-2 mt-4">
      <Button color="blue" onclick={() => (isEditing = !isEditing)}>
        <SquarePen class="mr-2 h-4 w-4" /> Edit Details
      </Button>
      <Button color="red" onclick={onDelete}>
        <Trash2 class="mr-2 h-4 w-4" /> Delete
      </Button>
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