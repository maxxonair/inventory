<script lang="ts">
  import {
    Button, CloseButton, Label, Input, Textarea, Badge, Select, ButtonGroup
  } from "flowbite-svelte";
  import {
    CheckCircleOutline, FolderArrowRightOutline, CloseOutline,
    ExclamationCircleOutline, CartPlusAltOutline, PrinterOutline,
    PenOutline, MinusOutline, PlusOutline
  } from 'flowbite-svelte-icons';
  import { Undo2 } from "lucide-svelte";
  import type { InventoryItem } from "../services/inventory.svelte";
  import FieldRow from './FieldRow.svelte';
  import { onMount } from "svelte";
  import { media_url, captureImage, uploadImage, item_categories } from "../services/inventory.svelte";
  import { goto } from "$app/navigation";

  let {
    item,
    user_privilege,
    image_updated,
    onClose,
    onUpdate,
    onDelete,
    onCheckout,
    onReturn,
    onPrint,
  }: {
    item: InventoryItem;
    user_privilege: number;
    onClose: () => void;
    onUpdate: (id: number, data: InventoryItem) => Promise<String>;
    onDelete: (id: number) => void;
    onCheckout: (id: number) => void;
    onReturn: (id: number) => void;
    onPrint: (id: number) => Promise<String>;
  } = $props();

  const PRIVILEGE_MAINTAINER = 2;
  const PRIVILEGE_REPORTER = 1;

  let isEditing = $state(false);
  let showCameraStream = $state(false);
  let imageExpanded = $state(false);
  let showDeleteConfirm = $state(false);
  let editedItem = $state<InventoryItem>({ ...item });
  let videoEl = $state<HTMLVideoElement | undefined>(undefined);
  let image = $state(item.image ?? '');
  let tmp_image = $state('');
  let mediaStream = $state<MediaStream | null>(null);
  let storageLocations = $state<{ value: number; name: string }[]>([]);
  let storageLocationsError = $state("");
  let editTagList: string[] = $state([]);
  let editTagInput: string = $state('');

  // Process error strings
  let save_error = $state("");
  let stream_error = $state('');
  let camera_error = $state('');
  let print_error = $state("");

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
  function requestDelete() { showDeleteConfirm = true; }
  function cancelDelete() { showDeleteConfirm = false; }
  function confirmDelete() { onDelete(item.id); showDeleteConfirm = false; onClose(); }

  // Action Handlers
  function handleSave() { save_error = String(onUpdate(item.id, editedItem)); isEditing = false; }
  async function handlePrintQrLabel() {print_error = String(onPrint(item.id))}
  async function handleFileUpload(e: Event) {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (file) await processImageFile(file);
  }
  async function handleImageCapture() {
    const result = await captureImage(videoEl);
    camera_error = result.error;

    if (camera_error === "") {
      editedItem.image = result.image;
      image_updated = true;
      stopCamera();
      showCameraStream = false;
    }
  }

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
      if (res.status === 401) {goto('/login');}
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

  async function processImageFile(file: File) {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = (e) => {
      tmp_image = e.target?.result as string;
    }
    const formData = new FormData();
    formData.append("avatar", file);
    const result = await uploadImage(formData);
    if (camera_error === "") {
      image = result.image;
      image_updated = true;
      editedItem = { ...editedItem, image };
    }
  }

  // Ensure URLs have a protocol for proper linking by prepending "https://" if 
  // missing. Otherwise links are interpreted as relative paths and will break
  // when the base URL isn't the root.
  function normalizeUrl(url: any): string {
    if (!url) return '';
    if (!/^https?:\/\//i.test(url)) {
      return `https://${url}`;
    }
    return url;
  }

  // Sync editTagList from editedItem.tags whenever editing is toggled on
  $effect(() => {
    if (isEditing) {
      editTagList = editedItem.tags
        ? editedItem.tags.split(',').map(t => t.trim()).filter(Boolean)
        : [];
      editTagInput = '';
    }
  });

  // Keep editedItem.tags in sync as pills change
  $effect(() => {
    editedItem.tags = editTagList.join(', ');
  });

  function addEditTag() {
    const tag = editTagInput.trim();
    if (tag && !editTagList.includes(tag)) {
      editTagList = [...editTagList, tag];
    }
    editTagInput = '';
  }

  function removeEditTag(index: number) {
    editTagList = editTagList.filter((_, i) => i !== index);
  }

  function handleEditTagKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      addEditTag();
    } else if (e.key === 'Backspace' && editTagInput === '' && editTagList.length > 0) {
      editTagList = editTagList.slice(0, -1);
    }
  }

</script>

<div class="w-full bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">

  <!-- Top bar -->
  <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 flex-wrap gap-3">
    <!-- Return to Overview -->
    <Button color="alternative" size="sm" onclick={onClose}>
      <Undo2 class="mr-2 h-4 w-4" /> Back to Inventory Overview
    </Button>
    
    <!-- Title + status -->
    <div class="flex items-center gap-3 flex-wrap">
      <a href={normalizeUrl(item.manufacturer_link)} target="_blank" rel="noopener noreferrer"
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
        <Button color="blue" size="sm" onclick={handlePrintQrLabel}>
          <PrinterOutline class="mr-1.5 h-4 w-4" /> Print label
        </Button>
        {#if user_privilege > PRIVILEGE_REPORTER}
          <Button color="primary" size="sm" onclick={toggleEdit}>
            <PenOutline class="mr-1.5 h-4 w-4" /> Edit
          </Button>
        {/if}
      {/if}
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
          <Button size="sm" onclick={handleImageCapture} class="w-full">Capture</Button>
          <Button color="alternative" size="sm" onclick={toggleCameraVisibility} class="w-full">Cancel</Button>
        </div>
      {:else}
        <!-- svelte-ignore a11y_click_events_have_key_events a11y_no_noninteractive_element_interactions -->
        <div
          class="w-full aspect-square rounded-xl overflow-hidden bg-gray-200 dark:bg-gray-700 flex items-center justify-center cursor-zoom-in"
          onclick={() => (imageExpanded = true)}
          title="Click to enlarge"
          role="button"
          tabindex="0"
          onkeydown={(e) => e.key === 'Enter' && (imageExpanded = true)}
        >
          <img
            src={image_updated ? tmp_image : `${media_url}${item.image}.png`}
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
              <a href={normalizeUrl(item.manufacturer_link)} target="_blank" rel="noopener noreferrer"
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
            <Select items={item_categories} bind:value={editedItem.item_type} />
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
            {#if editedItem.location}
              <a href="/storage/item/{editedItem.location}" class="text-blue-500 hover:underline">
                {getStorageLocationName(editedItem.location)}
              </a>
            {:else}
              <span class="text-gray-400 italic">No location set</span>
            {/if}
          {/snippet}
        </FieldRow>

        <!-- Tags -->
        <FieldRow label="Tags" editing={isEditing}>
          {#snippet editSlot()}
            <div>
              <!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
              <div
                class="flex flex-wrap gap-1.5 items-center min-h-[42px] w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus-within:ring-1 focus-within:ring-blue-500 focus-within:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white p-2 cursor-text"
                onclick={() => document.getElementById('edit-tag-input')?.focus()}
              >
                {#each editTagList as tag, i}
                  <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300">
                    {tag}
                    <button
                      type="button"
                      onclick={() => removeEditTag(i)}
                      class="inline-flex items-center p-0.5 text-blue-400 hover:bg-blue-200 hover:text-blue-900 dark:hover:bg-blue-800 dark:hover:text-blue-300 rounded-full"
                      aria-label="Remove tag {tag}"
                    >
                      <svg class="w-2 h-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M6 18L18 6M6 6l12 12"/>
                      </svg>
                    </button>
                  </span>
                {/each}
                <input
                  id="edit-tag-input"
                  type="text"
                  bind:value={editTagInput}
                  onkeydown={handleEditTagKeydown}
                  placeholder={editTagList.length === 0 ? "Type and press Enter…" : ""}
                  class="flex-1 min-w-[120px] bg-transparent border-none outline-none text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 p-0"
                />
              </div>
              <p class="mt-1 text-xs text-gray-400 dark:text-gray-500">
                Press <kbd class="px-1 py-0.5 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-200 rounded dark:bg-gray-600 dark:text-gray-100 dark:border-gray-500">Enter</kbd>
                or <kbd class="px-1 py-0.5 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-200 rounded dark:bg-gray-600 dark:text-gray-100 dark:border-gray-500">,</kbd>
                to add · Backspace to remove
              </p>
            </div>
          {/snippet}
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

<!-- Lightbox overlay -->
{#if imageExpanded}
  <!-- svelte-ignore a11y_click_events_have_key_events a11y_no_noninteractive_element_interactions -->
  <div
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm cursor-zoom-out"
    onclick={() => (imageExpanded = false)}
    role="button"
    tabindex="0"
    onkeydown={(e) => e.key === 'Escape' && (imageExpanded = false)}
    title="Click to close"
  >
    <img
      src={image_updated ? tmp_image : `${media_url}${item.image}.png`}
      alt={item.name}
      class="max-w-[90vw] max-h-[90vh] rounded-xl object-contain shadow-2xl"
    />
    <button
      class="absolute top-4 right-4 text-white bg-black/50 hover:bg-black/70 rounded-full p-2 transition-colors"
      onclick={() => (imageExpanded = false)}
      aria-label="Close enlarged image"
    >
      <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  </div>
{/if}