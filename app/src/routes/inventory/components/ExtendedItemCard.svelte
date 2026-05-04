<script lang="ts">
  import { 
    Button, CloseButton, Label, Input, Textarea, 
    ButtonGroup, Select, FloatingLabelInput 
  } from "flowbite-svelte";
  import { 
    CheckCircleOutline, FolderArrowRightOutline, CloseOutline, 
    ExclamationCircleOutline, CartPlusAltOutline, PrinterOutline, 
    PenOutline, MinusOutline, PlusOutline 
  } from 'flowbite-svelte-icons';
  import type { InventoryItem } from "../services/inventory.svelte";

  // Props
  let { 
    item, 
    user_privilege, 
    media_url,
    onClose, 
    onUpdate, 
    onDelete, 
    onCheckout, 
    onReturn, 
    onPrint 
  } = $props();

  // Constants (Adjust based on your auth logic)
  const PRIVILEGE_MAINTAINER = 2;
  const PRIVILEGE_REPORTER = 1;

  // State
  let isEditing = $state(false);
  let showCameraStream = $state(false);
  let showDeleteConfirm = $state(false);
  let editedItem = $state<InventoryItem>({ ...item });
  let videoEl = $state<HTMLVideoElement>();

  // Sync edits if the parent item changes
$effect(() => {
  editedItem = {
    ...item,
    name: item.name ?? '',
    manufacturer: item.manufacturer ?? '',
    location: item.location ?? '',
    details: item.details ?? '',
    number_items: item.number_items ?? 0
  };
});

  // Actions
  function handleSave() {
    onUpdate(item.id, editedItem);
    isEditing = false;
  }

  function toggleCameraVisibility() {
    showCameraStream = !showCameraStream;
    // Note: You'll need to trigger your stream start/stop logic here
  }

  function handleCapture() {
    // Logic from your captureImage function
  }
</script>

<div class="w-full max-w-full mx-auto p-4 bg-slate-200 dark:bg-slate-800 rounded-lg shadow-xl">
  
  <!-- Header Bar -->
  <div class="relative flex items-center justify-between w-full flex-wrap mb-6 border-b pb-4 border-slate-300 dark:border-slate-700">
    <div class="flex flex-col">
      <h2 class="text-2xl font-bold text-stone-950 dark:text-white">
        {item.name}
      </h2>
      <p class="text-sm text-gray-500">{item.manufacturer}</p>
    </div>

    <div class="flex items-center gap-4">
      {#if item.is_checked_out}
        <span class="p-2 bg-red-500 text-white text-xs font-bold rounded-lg border border-red-900">
          Checked out by {item.check_out_poc}
        </span>
      {:else}
        <span class="p-2 bg-green-500 text-slate-800 text-xs font-bold rounded-lg border border-slate-900">
          Available
        </span>
      {/if}
      <CloseButton onclick={onClose} class="dark:text-white" />
    </div>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    
    <!-- LEFT COLUMN: Image / Camera -->
    <div class="flex flex-col items-center">
      {#if showCameraStream}
        <div class="w-full aspect-video bg-black rounded-lg overflow-hidden relative border-2 border-dashed border-red-500">
          <video bind:this={videoEl} autoplay playsinline class="w-full h-full object-cover">
             <track kind="captions" />
          </video>
          <div class="absolute bottom-4 w-full flex justify-center gap-2">
            <Button size="xs" color="red" onclick={handleCapture}>Capture</Button>
            <Button size="xs" color="light" onclick={toggleCameraVisibility}>Close Camera</Button>
          </div>
        </div>
      {:else}
        <img
          src={`${media_url}${item.image}.png`}
          alt={item.name}
          class="w-full max-h-[400px] object-contain border rounded-lg border-slate-900 bg-white"
        />
        {#if isEditing}
           <Button color="light" class="mt-4 w-full" onclick={toggleCameraVisibility}>
             Change Image (Camera)
           </Button>
        {/if}
      {/if}
    </div>

    <!-- RIGHT COLUMN: Form / Info -->
    <div class="space-y-4">
      <div class="grid gap-4 grid-cols-1 sm:grid-cols-2">
        {#if isEditing}
          <!-- Edit Mode Fields -->
          <div class="col-span-2">
            <FloatingLabelInput variant="outlined" bind:value={editedItem.name}>Name</FloatingLabelInput>
          </div>
          <FloatingLabelInput variant="outlined" bind:value={editedItem.manufacturer}>Manufacturer</FloatingLabelInput>
          <FloatingLabelInput variant="outlined" bind:value={editedItem.location}>Storage Location</FloatingLabelInput>
          
          <div class="col-span-2">
             <Label class="mb-2">Item Details</Label>
             <Textarea bind:value={editedItem.details} rows={3} />
          </div>

          <div class="flex flex-col gap-2">
            <Label>Count</Label>
            <ButtonGroup>
              <Button onclick={() => (editedItem.number_items -= 1)}><MinusOutline /></Button>
              <Input type="number" bind:value={editedItem.number_items} class="w-20 text-center" />
              <Button onclick={() => (editedItem.number_items += 1)}><PlusOutline /></Button>
            </ButtonGroup>
          </div>
        {:else}
          <!-- View Mode Fields -->
          <div class="p-3 bg-slate-50 dark:bg-slate-700 rounded-lg border border-slate-300 dark:border-slate-600">
            <span class="text-red-500 text-xs font-bold block">Manufacturer</span>
            <span class="dark:text-white">{item.manufacturer}</span>
          </div>
          <div class="p-3 bg-slate-50 dark:bg-slate-700 rounded-lg border border-slate-300 dark:border-slate-600">
            <span class="text-red-500 text-xs font-bold block">Location</span>
            <span class="dark:text-white">{item.location}</span>
          </div>
          <div class="p-3 bg-slate-50 dark:bg-slate-700 rounded-lg border border-slate-300 dark:border-slate-600 col-span-2">
            <span class="text-red-500 text-xs font-bold block">Details</span>
            <p class="dark:text-white text-sm">{item.details || 'No details provided.'}</p>
          </div>
          <div class="p-3 bg-slate-50 dark:bg-slate-700 rounded-lg border border-slate-300 dark:border-slate-600">
            <span class="text-red-500 text-xs font-bold block">Stock Count</span>
            <span class="dark:text-white">{item.number_items} units</span>
          </div>
        {/if}
      </div>

      <!-- Action Footer -->
      <div class="flex flex-wrap gap-2 pt-6 border-t border-slate-300 dark:border-slate-700">
        {#if isEditing}
          <Button color="green" onclick={handleSave}>
            <CheckCircleOutline class="me-2 h-5 w-5" /> Confirm Edit
          </Button>
          <Button color="light" onclick={() => isEditing = false}>
            <CloseOutline class="me-2 h-5 w-5" /> Cancel
          </Button>
        {:else if showDeleteConfirm}
          <div class="flex items-center gap-4 p-2 bg-red-100 dark:bg-red-900/30 rounded-lg w-full">
            <span class="text-red-700 dark:text-red-400 font-bold text-sm">Permanently delete?</span>
            <Button color="red" size="xs" onclick={onDelete}>Yes, Delete</Button>
            <Button color="light" size="xs" onclick={() => showDeleteConfirm = false}>Cancel</Button>
          </div>
        {:else}
          <!-- Standard View Actions -->
          {#if item.is_checked_out}
            <Button color="green" onclick={() => onReturn(item.id)}>
              <FolderArrowRightOutline class="me-2 h-5 w-5" /> Return
            </Button>
          {:else}
            <Button color="blue" onclick={() => onCheckout(item.id)}>
              <CartPlusAltOutline class="me-2 h-5 w-5" /> Borrow
            </Button>
          {/if}

          <Button color="alternative" onclick={() => onPrint(item.id)}>
            <PrinterOutline class="me-2 h-5 w-5" /> Label
          </Button>

          {#if user_privilege > PRIVILEGE_REPORTER}
            <Button color="light" onclick={() => isEditing = true}>
              <PenOutline class="me-2 h-5 w-5" /> Edit
            </Button>
          {/if}

          {#if user_privilege >= PRIVILEGE_MAINTAINER}
            <Button color="red" onclick={() => showDeleteConfirm = true}>
              <FolderArrowRightOutline class="me-2 h-5 w-5 rotate-90" /> Delete
            </Button>
          {/if}
        {/if}
      </div>
    </div>
  </div>
</div>