<script lang="ts">
  import {
    Button, CloseButton, Label, Input, Textarea, Badge, Select, ButtonGroup
  } from "flowbite-svelte";
  import {
    CheckCircleOutline, FolderArrowRightOutline, CloseOutline,
    ExclamationCircleOutline, CartPlusAltOutline, PrinterOutline,
    PenOutline, MinusOutline, PlusOutline
  } from 'flowbite-svelte-icons';
  import type { InventoryItem } from "../services/inventory.svelte";
  import FieldRow from './FieldRow.svelte';
  import { onMount } from "svelte";

  let {
    item,
    user_privilege,
    media_url,
    categories = [],
    onClose,
    onUpdate,
    onDelete,
    onCheckout,
    onReturn,
    onPrint
  }: {
    item: InventoryItem;
    user_privilege: number;
    media_url: string;
    categories?: { value: string; name: string }[];
    onClose: () => void;
    onUpdate: (id: number | string, data: InventoryItem) => void;
    onDelete: (id: number | string) => void;
    onCheckout: (id: number | string) => void;
    onReturn: (id: number | string) => void;
    onPrint: (id: number | string) => void;
  } = $props();

  const PRIVILEGE_MAINTAINER = 2;
  const PRIVILEGE_REPORTER = 1;

  let isEditing = $state(false);
  let showCameraStream = $state(false);
  let showDeleteConfirm = $state(false);
  let editedItem = $state<InventoryItem>({ ...item });
  let videoEl = $state<HTMLVideoElement | undefined>(undefined);
  let imageUpdated = $state(false);
  let image = $state(item.image ?? '');
  let stream_error = $state('');
  let camera_error = $state('');
  let mediaStream = $state<MediaStream | null>(null);
  let storageLocations = $state<{ value: number; name: string }[]>([]);
  let storageLocationsError = $state("");

  $effect(() => {
    if (!isEditing) editedItem = freshCopy();
  });

  function freshCopy(): InventoryItem {
    return {
      id: item.id,
      name: item.name ?? '',
      image: item.image ?? '',
      description: item.description ?? '',
      manufacturer: item.manufacturer ?? '',
      details: item.details ?? '',
      is_checked_out: item.is_checked_out ?? false,
      check_out_date: item.check_out_date ?? '',
      check_out_poc: item.check_out_poc ?? '',
      date_added: item.date_added ?? '',
      tags: item.tags ?? '',
      location: item.location ?? 0,
      item_type: item.item_type ?? '',
      manufacturer_link: item.manufacturer_link ?? '',
      project: item.project ?? '',
      manufacturer_location: item.manufacturer_location ?? '',
      color: item.color ?? '',
      material: item.material ?? '',
      product_use: item.product_use ?? '',
      number_items: item.number_items ?? 0,
    };
  }

  function toggleEdit() { editedItem = freshCopy(); isEditing = true; }
  function cancelEdit() { editedItem = freshCopy(); isEditing = false; }
  function handleSave() { onUpdate(item.id, editedItem); isEditing = false; }
  function requestDelete() { showDeleteConfirm = true; }
  function cancelDelete() { showDeleteConfirm = false; }
  function confirmDelete() { onDelete(item.id); showDeleteConfirm = false; onClose(); }

  async function toggleCameraVisibility() {
    showCameraStream = !showCameraStream;
    if (showCameraStream) {
      try {
        stream_error = '';
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        mediaStream = stream;
        if (videoEl) videoEl.srcObject = stream;
      } catch (err) {
        stream_error = 'Could not access camera.';
        camera_error = String(err);
        showCameraStream = false;
      }
    } else {
      stopCamera();
    }
  }

  function stopCamera() {
    mediaStream?.getTracks().forEach(t => t.stop());
    mediaStream = null;
  }

  function captureImage() {
    if (!videoEl) return;
    const canvas = document.createElement('canvas');
    canvas.width = videoEl.videoWidth;
    canvas.height = videoEl.videoHeight;
    canvas.getContext('2d')?.drawImage(videoEl, 0, 0);
    image = canvas.toDataURL('image/png');
    imageUpdated = true;
    stopCamera();
    showCameraStream = false;
  }

  function getStorageLocationName(id: any) {
    return storageLocations.find((sl) => sl.value === id)?.name ?? '—';
  }

  function onDrop(e: DragEvent) {
    e.preventDefault();
    const file = e.dataTransfer?.files?.[0];
    if (file) processImageFile(file);
  }

  function onDragOver(e: DragEvent) { e.preventDefault(); }

  onMount(async () => {
    try {
      const res = await fetch("/api/storage_locations");
      if (!res.ok) throw new Error("Failed to fetch storage locations");
      const data = await res.json();
      storageLocations = data.map((sl: { id: number; name: string }) => ({
        value: sl.id,
        name: sl.name,
      }));
    } catch (err) {
      storageLocationsError = "Could not load storage locations.";
    }
  });

  function handleFileUpload(e: Event) {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (file) processImageFile(file);
  }

  function processImageFile(file: File) {
    const reader = new FileReader();
    reader.onload = (e) => {
      image = e.target?.result as string;
      imageUpdated = true;
      editedItem = { ...editedItem, image };
    };
    reader.readAsDataURL(file);
  }
</script>

<div class="w-full bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">

  <!-- Top bar -->
  <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 flex-wrap gap-3">

    <!-- Title + status -->
    <div class="flex items-center gap-3 flex-wrap">
      <a href={item.manufacturer_link} target="_blank" rel="noopener noreferrer"
        class="text-lg font-semibold text-gray-900 dark:text-white hover:underline">
        {item.name}
      </a>
      {#if item.is_checked_out}
        <Badge color="red">Checked out — {item.check_out_poc} since {item.check_out_date}</Badge>
      {:else}
        <Badge color="green">Available</Badge>
      {/if}
      {#if item.date_added}
        <span class="text-xs text-gray-400 dark:text-gray-500 font-mono">ID: {item.id} · Added {item.date_added}</span>
      {/if}
    </div>

    <!-- Action buttons -->
    <div class="flex items-center gap-2 flex-wrap">
      {#if showDeleteConfirm}
        <span class="text-sm font-medium text-red-600 dark:text-red-400">Delete this item?</span>
        <Button color="red" size="sm" onclick={confirmDelete}>
          <ExclamationCircleOutline class="mr-1.5 h-4 w-4" /> Yes, delete
        </Button>
        <Button color="alternative" size="sm" onclick={cancelDelete}>
          <CloseOutline class="mr-1.5 h-4 w-4" /> Cancel
        </Button>

      {:else if isEditing}
        <Button color="green" size="sm" onclick={handleSave}>
          <CheckCircleOutline class="mr-1.5 h-4 w-4" /> Save changes
        </Button>
        <Button color="alternative" size="sm" onclick={toggleCameraVisibility}>
          {showCameraStream ? 'Close camera' : 'Open camera'}
        </Button>
        {#if user_privilege >= PRIVILEGE_MAINTAINER}
          <Button color="red" size="sm" onclick={requestDelete}>
            <ExclamationCircleOutline class="mr-1.5 h-4 w-4" /> Delete
          </Button>
        {/if}
        <Button color="alternative" size="sm" onclick={cancelEdit}>
          <CloseOutline class="mr-1.5 h-4 w-4" /> Cancel
        </Button>

      {:else}
        {#if item.is_checked_out}
          <Button color="green" size="sm" onclick={() => onReturn(item.id)}>
            <FolderArrowRightOutline class="mr-1.5 h-4 w-4" /> Return
          </Button>
        {:else}
          <Button color="blue" size="sm" onclick={() => onCheckout(item.id)}>
            <CartPlusAltOutline class="mr-1.5 h-4 w-4" /> Borrow
          </Button>
        {/if}
        <Button color="alternative" size="sm" onclick={() => onPrint(item.id)}>
          <PrinterOutline class="mr-1.5 h-4 w-4" /> Print label
        </Button>
        <!-- {#if user_privilege > PRIVILEGE_REPORTER} -->
         <!-- TODO add back guardrails -->
          <Button color="alternative" size="sm" onclick={toggleEdit}>
            <PenOutline class="mr-1.5 h-4 w-4" /> Edit
          </Button>
        <!-- {/if} -->
      {/if}
      <CloseButton onclick={onClose} class="dark:text-white ml-1" />
    </div>
  </div>

  <!-- Body -->
  <div class="flex flex-col md:flex-row">

    <!-- Left: image panel -->
    <div class="md:w-64 lg:w-80 shrink-0 bg-gray-100 dark:bg-gray-800 flex flex-col items-center justify-start p-6 gap-4 border-b md:border-b-0 md:border-r border-gray-200 dark:border-gray-700">
      {#if showCameraStream}
        <div class="w-full flex flex-col items-center gap-3">
          <p class="text-sm font-medium text-gray-700 dark:text-gray-300">Capture item image</p>
          {#if stream_error}
            <p class="text-sm text-red-500">{stream_error}</p>
          {:else}
            <!-- svelte-ignore a11y_media_has_caption -->
            <video bind:this={videoEl} autoplay playsinline
              class="w-full rounded-lg border border-gray-300 dark:border-gray-600"></video>
          {/if}
          {#if camera_error}
            <p class="text-xs text-gray-400">{camera_error}</p>
          {/if}
          <Button size="sm" onclick={captureImage} class="w-full">Capture</Button>
          <Button color="alternative" size="sm" onclick={toggleCameraVisibility} class="w-full">Cancel</Button>
        </div>
      {:else}
        <div class="w-full aspect-square rounded-xl overflow-hidden bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
          <img
            src={imageUpdated ? image : `${media_url}${item.image}.png`}
            alt={item.name}
            class="w-full h-full object-contain"
          />
        </div>

        {#if isEditing}
          <!-- Drop zone -->
          <label for="dropzone-file"
            class="flex flex-col items-center justify-center w-full h-24 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
            ondrop={onDrop}
            ondragover={onDragOver}
          >
            <p class="text-xs text-gray-500 dark:text-gray-400 text-center px-2">
              <span class="font-semibold">Click to upload</span> or drag & drop<br/>
              <span class="text-gray-400">SVG, PNG, JPG</span>
            </p>
            <input id="dropzone-file" type="file" class="hidden" onchange={handleFileUpload} />
          </label>
        {/if}
      {/if}
    </div>

    <!-- Right: fields -->
    <div class="flex-1 p-6 lg:p-8">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-4">

        <!-- Name -->
        <FieldRow label="Name" editing={isEditing}>
          {#snippet editSlot()}<Input bind:value={editedItem.name} />{/snippet}
          {#snippet viewSlot()}<span>{item.name}</span>{/snippet}
        </FieldRow>

        <!-- Manufacturer -->
        <FieldRow label="Manufacturer" editing={isEditing}>
          {#snippet editSlot()}<Input bind:value={editedItem.manufacturer} />{/snippet}
          {#snippet viewSlot()}<span>{item.manufacturer || '—'}</span>{/snippet}
        </FieldRow>

        <!-- Manufacturer Link -->
        <FieldRow label="Product Page" editing={isEditing}>
          {#snippet editSlot()}<Input bind:value={editedItem.manufacturer_link} placeholder="https://…" />{/snippet}
          {#snippet viewSlot()}
            {#if item.manufacturer_link}
              <a href={item.manufacturer_link} target="_blank" rel="noopener noreferrer"
                class="text-blue-600 dark:text-blue-400 hover:underline text-sm">
                {item.name} product page ↗
              </a>
            {:else}
              <span class="text-gray-400">N/A</span>
            {/if}
          {/snippet}
        </FieldRow>

        <!-- Manufacturer Location -->
        <FieldRow label="Manufacturer Location" editing={isEditing}>
          {#snippet editSlot()}<Input bind:value={editedItem.manufacturer_location} />{/snippet}
          {#snippet viewSlot()}<span>{item.manufacturer_location || '—'}</span>{/snippet}
        </FieldRow>

        <!-- Count -->
        <FieldRow label="Count" editing={isEditing}>
          {#snippet editSlot()}
            <ButtonGroup>
              <Button type="button" onclick={() => editedItem.number_items = (editedItem.number_items ?? 1) - 1}>
                <MinusOutline class="h-4 w-4" />
              </Button>
              <Input bind:value={editedItem.number_items} type="number" class="w-20 text-center" />
              <Button type="button" onclick={() => editedItem.number_items = (editedItem.number_items ?? 0) + 1}>
                <PlusOutline class="h-4 w-4" />
              </Button>
            </ButtonGroup>
          {/snippet}
          {#snippet viewSlot()}<span>{item.number_items}</span>{/snippet}
        </FieldRow>

        <!-- Product Type -->
        <FieldRow label="Product Type" editing={isEditing}>
          {#snippet editSlot()}
            <Select items={categories} bind:value={editedItem.item_type} />
          {/snippet}
          {#snippet viewSlot()}<span>{item.item_type || '—'}</span>{/snippet}
        </FieldRow>

        <!-- Product Use -->
        <FieldRow label="Product Use" editing={isEditing}>
          {#snippet editSlot()}<Input bind:value={editedItem.product_use} />{/snippet}
          {#snippet viewSlot()}<span>{item.product_use || '—'}</span>{/snippet}
        </FieldRow>

        <!-- Material -->
        <FieldRow label="Material" editing={isEditing}>
          {#snippet editSlot()}<Input bind:value={editedItem.material} />{/snippet}
          {#snippet viewSlot()}<span>{item.material || '—'}</span>{/snippet}
        </FieldRow>

        <!-- Color -->
        <FieldRow label="Color" editing={isEditing}>
          {#snippet editSlot()}<Input bind:value={editedItem.color} />{/snippet}
          {#snippet viewSlot()}<span>{item.color || '—'}</span>{/snippet}
        </FieldRow>

        <!-- Project -->
        <FieldRow label="Project" editing={isEditing}>
          {#snippet editSlot()}<Input bind:value={editedItem.project} />{/snippet}
          {#snippet viewSlot()}<span>{item.project || '—'}</span>{/snippet}
        </FieldRow>

        <!-- Storage Location -->
        <FieldRow label="Storage Location" editing={isEditing}>
          {#snippet editSlot()}
            {#if storageLocationsError}
              <p class="text-xs text-red-500">{storageLocationsError}</p>
            {:else if storageLocations.length === 0}
              <p class="text-xs text-gray-400 dark:text-gray-500 italic">
                Loading locations…
              </p>
            {:else}
              <Select
                items={[...storageLocations]}
                bind:value={editedItem.location}
              />
            {/if}
          {/snippet}
          {#snippet viewSlot()}
            <span>{getStorageLocationName(editedItem.location)}</span>
          {/snippet}
        </FieldRow>

        <!-- Tags -->
        <FieldRow label="Tags" editing={isEditing}>
          {#snippet editSlot()}<Input bind:value={editedItem.tags} placeholder="comma, separated" />{/snippet}
          {#snippet viewSlot()}
            {#if item.tags}
              <div class="flex flex-wrap gap-1 mt-1">
                {#each item.tags.split(',') as tag}
                  <Badge color="blue">{tag.trim()}</Badge>
                {/each}
              </div>
            {:else}
              <span class="text-gray-400">—</span>
            {/if}
          {/snippet}
        </FieldRow>

        <!-- Details (full width) -->
        <div class="sm:col-span-2">
          <p class="text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-1.5">Details</p>
          {#if isEditing}
            <Textarea bind:value={editedItem.details} rows={3} placeholder="Additional notes…" class="w-full" />
          {:else}
            <p class="text-sm text-gray-700 dark:text-gray-300 leading-relaxed">
              {item.details || '—'}
            </p>
          {/if}
        </div>

      </div>
    </div>
  </div>
</div>
