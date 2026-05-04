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

  // Constants
  const PRIVILEGE_MAINTAINER = 2;
  const PRIVILEGE_REPORTER = 1;

  // State
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

  // Sync edits if the parent item changes
  $effect(() => {
    if (!isEditing) {
      editedItem = {
        id:                   item.id,
        name:                 item.name                 ?? '',
        image:                item.image                ?? '',
        description:          item.description          ?? '',
        manufacturer:         item.manufacturer         ?? '',
        details:              item.details              ?? '',
        is_checked_out:       item.is_checked_out       ?? false,
        check_out_date:       item.check_out_date       ?? '',
        check_out_poc:        item.check_out_poc        ?? '',
        date_added:           item.date_added           ?? '',
        tags:                 item.tags                 ?? '',
        location:             item.location             ?? null,
        item_type:            item.item_type            ?? '',
        manufacturer_link:    item.manufacturer_link    ?? '',
        project:              item.project              ?? '',
        manufacturer_location:item.manufacturer_location?? '',
        color:                item.color                ?? '',
        material:             item.material             ?? '',
        product_use:          item.product_use          ?? '',
        number_items:         item.number_items         ?? 0,
      };
    }
  });

  // Actions
  function freshCopy(): InventoryItem {
    return {
      id:                    item.id,
      name:                  item.name                  ?? '',
      image:                 item.image                 ?? '',
      description:           item.description           ?? '',
      manufacturer:          item.manufacturer          ?? '',
      details:               item.details               ?? '',
      is_checked_out:        item.is_checked_out        ?? false,
      check_out_date:        item.check_out_date        ?? '',
      check_out_poc:         item.check_out_poc         ?? '',
      date_added:            item.date_added            ?? '',
      tags:                  item.tags                  ?? '',
      location:              item.location              ?? null,
      item_type:             item.item_type             ?? '',
      manufacturer_link:     item.manufacturer_link     ?? '',
      project:               item.project               ?? '',
      manufacturer_location: item.manufacturer_location ?? '',
      color:                 item.color                 ?? '',
      material:              item.material              ?? '',
      product_use:           item.product_use           ?? '',
      number_items:          item.number_items          ?? 0,
    };
  }

  function toggleEdit() {
    editedItem = freshCopy();
    isEditing = true;
  }

  function cancelEdit() {
    editedItem = freshCopy();
    isEditing = false;
  }

  function handleSave() {
    onUpdate(item.id, editedItem);
    isEditing = false;
  }

  function requestDelete() {
    showDeleteConfirm = true;
  }

  function cancelDelete() {
    showDeleteConfirm = false;
  }

  function confirmDelete() {
    onDelete(item.id);
    showDeleteConfirm = false;
    onClose();
  }

  async function toggleCameraVisibility() {
    showCameraStream = !showCameraStream;
    if (showCameraStream) {
      try {
        stream_error = '';
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        mediaStream = stream;
        if (videoEl) {
          videoEl.srcObject = stream;
        }
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
    if (mediaStream) {
      mediaStream.getTracks().forEach(t => t.stop());
      mediaStream = null;
    }
  }

  function captureImage() {
    if (!videoEl) return;
    const canvas = document.createElement('canvas');
    canvas.width = videoEl.videoWidth;
    canvas.height = videoEl.videoHeight;
    canvas.getContext('2d')?.drawImage(videoEl, 0, 0);
    const dataUrl = canvas.toDataURL('image/png');
    image = dataUrl;
    imageUpdated = true;
    stopCamera();
    showCameraStream = false;
  }

  function onDrop(e: DragEvent) {
    e.preventDefault();
    const file = e.dataTransfer?.files?.[0];
    if (file) processImageFile(file);
  }

  function onDragOver(e: DragEvent) {
    e.preventDefault();
  }

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

<div class="w-full max-w-full mx-auto p-4 bg-slate-200 dark:bg-slate-800 rounded-lg shadow-xl">

  <!-- EXTENDED CARD -->
  <div class="w-full">
    <div class="rounded-lg expanded w-full max-w-full mx-auto mb-6 p-4 dark:bg-slate-800 bg-slate-200">

      <!-- Header row -->
      <div class="relative flex items-center justify-between w-full flex-wrap">
        <div class="flex justify-center">
          <a
            class="font-medium hover:underline justify-center mb-4 text-xl inline-flex font-bold items-center px-8 text-stone-950 dark:text-amber-900 rounded-lg"
            href={item.manufacturer_link}
            target="_blank"
            rel="noopener noreferrer"
          >
            <h2>{item.name}</h2>
          </a>
        </div>

        <div class="flex justify-center mt-auto">
          {#if item.is_checked_out}
            <label
              for="borrowed"
              class="mb-2 p-2 bg-red-500 text-slate-900 font-semibold border border-red-900 rounded-lg"
            >Checked out by {item.check_out_poc} since {item.check_out_date}</label>
          {:else}
            <label
              for="available"
              class="mb-2 p-2 bg-green-500 text-slate-800 font-semibold border border-slate-900 rounded-lg"
            >Available</label>
          {/if}
        </div>

        <CloseButton onclick={onClose} class="mb-4 dark:text-white" />
      </div>

      <!-- Body grid: image + form -->
      <div class="mb-6 grid gap-4 grid-cols-1 md:grid-cols-2">

        <!-- Image column -->
        <div class="mb-6 flex flex-col items-center p-2 col-span-1">
          <div class="flex items-center justify-center">
            {#if imageUpdated}
              <img src={image} alt={editedItem.name} class="w-full border rounded-lg border-slate-900" />
            {:else}
              <img
                src={`${media_url}${item.image}.png`}
                alt={item.image}
                class="w-full border rounded-lg border-slate-900"
              />
            {/if}
          </div>
        </div>

        <!-- Form column -->
        <form class="p-2">
          {#if showCameraStream}
            <!-- Camera stream view -->
            <div class="mb-6 flex flex-col items-center p-2 col-span-1">
              <Label for="name" class="mb-2 block p-2">Record item image</Label>
              <Button class="w-auto border mb-2" onclick={captureImage}>capture image</Button>
              <div class="mb-6 flex flex-col items-center p-2 col-span-1 w-full h-full">
                <p class="text-red-600">{stream_error}</p>
                {#if !stream_error}
                  <div class="flex items-center justify-center w-full h-full">
                    <!-- svelte-ignore a11y_media_has_caption -->
                    <video
                      bind:this={videoEl}
                      autoplay
                      playsinline
                      class="w-full h-full max-h-[80vh] object-contain rounded-lg"
                    ></video>
                  </div>
                {/if}
              </div>
              <Button color="light" class="w-auto mb-2" onclick={toggleCameraVisibility}>close camera</Button>
              <Label class="b-2 block">{camera_error}</Label>
            </div>

          {:else}
            <!-- Fields -->
            <div class="mb-2 grid gap-2 md:grid-cols-2">

              <!-- Name -->
              <div>
                {#if isEditing}
                  <FloatingLabelInput clearable variant="outlined" bind:value={editedItem.name}
                    class="bg-white dark:bg-slate-900 rounded-lg">name</FloatingLabelInput>
                {:else}
                  <Label class="mb-2 p-2 bg-slate-50 dark:bg-slate-700 rounded-lg">
                    <span class="text-red-500">Name: </span>{item.name}
                  </Label>
                {/if}
              </div>

              <!-- Manufacturer -->
              <div>
                {#if isEditing}
                  <FloatingLabelInput clearable variant="outlined" bind:value={editedItem.manufacturer}
                    class="bg-white dark:bg-slate-900 rounded-lg">Manufacturer</FloatingLabelInput>
                {:else}
                  <Label class="mb-2 p-2 text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg">
                    <span class="text-red-500">Manufacturer: </span>{item.manufacturer}
                  </Label>
                {/if}
              </div>

              <!-- Manufacturer Link -->
              <div>
                {#if isEditing}
                  <FloatingLabelInput clearable variant="outlined" bind:value={editedItem.manufacturer_link}
                    class="bg-white dark:bg-slate-900 rounded-lg">Manufacturer Link</FloatingLabelInput>
                {:else if item.manufacturer_link}
                  <a class="font-medium hover:underline justify-center" href={item.manufacturer_link} target="_blank" rel="noopener noreferrer">
                    <Label class="mb-2 p-2 flex justify-center text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg">
                      <span class="text-indigo-600 dark:text-blue-600 font-semibold">{item.name} Product Page</span>
                    </Label>
                  </a>
                {:else}
                  <Label class="mb-2 p-2 flex justify-center text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg">
                    <span class="text-gray-500">Product Page N/A</span>
                  </Label>
                {/if}
              </div>

              <!-- Manufacturer Location -->
              <div>
                {#if isEditing}
                  <FloatingLabelInput clearable variant="outlined" bind:value={editedItem.manufacturer_location}
                    class="bg-white dark:bg-slate-900 rounded-lg">Manufacturer Location</FloatingLabelInput>
                {:else}
                  <Label class="mb-2 p-2 text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg">
                    <span class="text-red-500">Manufacturer Location: </span>{item.manufacturer_location}
                  </Label>
                {/if}
              </div>

              <!-- Count -->
              <div class="mb-4">
                {#if isEditing}
                  <Label for="number_items" class="mb-2 block">Number of Items</Label>
                  <div class="relative max-w-[12rem] min-w-[8rem] items-center mb-6">
                    <ButtonGroup>
                      <Button type="button" id="decrement-button"
                        onclick={() => editedItem.number_items = (editedItem.number_items ?? 1) - 1}>
                        <MinusOutline />
                      </Button>
                      <Input
                        bind:value={editedItem.number_items}
                        type="number"
                        id="quantity-input"
                        required
                        class="w-20"
                      />
                      <Button type="button" id="increment-button"
                        onclick={() => editedItem.number_items = (editedItem.number_items ?? 0) + 1}>
                        <PlusOutline />
                      </Button>
                    </ButtonGroup>
                  </div>
                {:else}
                  <Label class="mb-2 p-2 text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg">
                    <span class="text-red-500">Count: </span>{item.number_items}
                  </Label>
                {/if}
              </div>

              <!-- Product Type -->
              <div>
                {#if isEditing}
                  <Label>Product Type
                    <Select class="mt-2" items={categories} bind:value={editedItem.item_type} />
                  </Label>
                {:else}
                  <Label class="mb-2 p-2 bg-slate-50 dark:bg-slate-700 rounded-lg">
                    <span class="text-red-500">Product Type: </span>{item.item_type}
                  </Label>
                {/if}
              </div>

              <!-- Product Use -->
              <div>
                {#if isEditing}
                  <FloatingLabelInput clearable variant="outlined" bind:value={editedItem.product_use}
                    class="bg-white dark:bg-slate-900 rounded-lg">Product Use</FloatingLabelInput>
                {:else}
                  <Label class="mb-2 p-2 text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg">
                    <span class="text-red-500">Product Use: </span>{item.product_use}
                  </Label>
                {/if}
              </div>

              <!-- Material -->
              <div>
                {#if isEditing}
                  <FloatingLabelInput clearable variant="outlined" bind:value={editedItem.material}
                    class="bg-white dark:bg-slate-900 rounded-lg">Material</FloatingLabelInput>
                {:else}
                  <Label class="mb-2 p-2 text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg">
                    <span class="text-red-500">Material: </span>{item.material}
                  </Label>
                {/if}
              </div>

              <!-- Color -->
              <div>
                {#if isEditing}
                  <FloatingLabelInput clearable variant="outlined" bind:value={editedItem.color}
                    class="bg-white dark:bg-slate-900 rounded-lg">Product Color</FloatingLabelInput>
                {:else}
                  <Label class="mb-2 p-2 text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg">
                    <span class="text-red-500">Product Color: </span>{item.color}
                  </Label>
                {/if}
              </div>

              <!-- Project -->
              <div>
                {#if isEditing}
                  <FloatingLabelInput clearable variant="outlined" bind:value={editedItem.project}
                    class="bg-white dark:bg-slate-900 rounded-lg">Project</FloatingLabelInput>
                {:else}
                  <Label class="mb-2 p-2 text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg">
                    <span class="text-red-500">Project: </span>{item.project}
                  </Label>
                {/if}
              </div>

              <!-- Storage Location -->
              {#if isEditing}
                <div>
                  <FloatingLabelInput clearable variant="outlined" bind:value={editedItem.location}
                    class="bg-white dark:bg-slate-900 rounded-lg">Storage Location</FloatingLabelInput>
                </div>
              {:else}
                <div>
                  <Label class="mb-2 p-2 text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg">
                    <span class="text-red-500">Storage Location: </span>{item.location}
                  </Label>
                </div>
              {/if}

              <!-- Tags -->
              <div>
                {#if isEditing}
                  <FloatingLabelInput clearable variant="outlined" bind:value={editedItem.tags}
                    class="bg-white dark:bg-slate-900 rounded-lg">Tags</FloatingLabelInput>
                {:else}
                  <Label class="mb-2 p-2 text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg">
                    <span class="text-red-500">Tags: </span>{item.tags}
                  </Label>
                {/if}
              </div>

              <!-- Details (read-only display) -->
              <div>
                {#if !isEditing}
                  <Label class="mb-2 p-2 bg-slate-50 dark:bg-slate-700 rounded-lg">
                    <span class="text-red-500">Details: </span>{item.details || 'N/A'}
                  </Label>
                {/if}
              </div>
            </div>

            <!-- Details textarea + image upload (edit only) -->
            <div>
              {#if isEditing}
                <div class="mb-2 justify-center w-full">
                  <Label for="description" class="mb-2">Details</Label>
                  <Textarea
                    id="message"
                    class="w-full"
                    placeholder={item.details}
                    rows={1}
                    name="message"
                    bind:value={editedItem.details}
                  />
                </div>

                <!-- svelte-ignore a11y_interactive_supports_focus -->
                <div
                  class="items-center justify-center w-full mb-4"
                  role="region"
                  ondrop={onDrop}
                  ondragover={onDragOver}
                >
                  <label
                    for="dropzone-file"
                    class="flex flex-col items-center justify-center w-full h-16 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:hover:bg-gray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500 dark:hover:bg-gray-600"
                  >
                    <div class="flex flex-col items-center justify-center pt-5 pb-6">
                      <p class="mb-2 text-xs text-gray-500 dark:text-gray-400">
                        <span class="font-semibold">Click to upload</span> or drag and drop
                      </p>
                      <p class="text-xs text-gray-500 dark:text-gray-400">SVG, PNG, JPG</p>
                    </div>
                    <input
                      id="dropzone-file"
                      type="file"
                      class="hidden"
                      onchange={handleFileUpload}
                    />
                  </label>
                </div>
              {/if}
            </div>

            <!-- Button bar -->
            <div class="bottom-0 left-0 flex flex-wrap md:flex-nowrap w-full justify-start gap-4 pb-4 md:px-4">
              {#if isEditing}
                <Button onclick={handleSave} color="green" class="w-auto">
                  <CheckCircleOutline class="me-2 h-5 w-5" /> confirm edit
                </Button>

                {#if user_privilege >= PRIVILEGE_MAINTAINER}
                  <Button color="red" class="w-auto" onclick={requestDelete}>
                    <FolderArrowRightOutline class="me-2 h-5 w-5" /> delete item
                  </Button>
                {/if}

                <Button class="w-auto" onclick={toggleCameraVisibility}>open camera</Button>

                <Button color="light" class="w-auto" onclick={cancelEdit}>
                  <CloseOutline class="me-2 h-5 w-5" /> cancel edit
                </Button>

              {:else if showDeleteConfirm}
                <div class="mb-2 p-2 border border-red-900 bg-red-500 rounded-lg">
                  <Label class="mb-2 p-2 text-slate-950">Are you sure you want to delete this item?</Label>
                  <div class="row-span-3 md:row-span-4">
                    <Button color="red" onclick={confirmDelete} class="mb-4 w-auto border border-slate-900">
                      <ExclamationCircleOutline class="me-2 h-5 w-5" /> yes, delete
                    </Button>
                    <Button color="light" onclick={cancelDelete} class="mb-4 dark:text-white">
                      <CloseOutline class="me-2 h-5 w-5" /> cancel
                    </Button>
                  </div>
                </div>

              {:else}
                {#if item.is_checked_out}
                  <Button color="green" onclick={() => onReturn(item.id)} class="mb-4 w-auto">
                    <FolderArrowRightOutline class="me-2 h-5 w-5" /> return item
                  </Button>
                {:else}
                  <Button onclick={() => onCheckout(item.id)} class="mb-4 w-auto">
                    <CartPlusAltOutline class="me-2 h-5 w-5" /> borrow
                  </Button>
                {/if}

                <Button onclick={() => onPrint(item.id)} class="mb-4">
                  <PrinterOutline class="me-2 h-5 w-5" /> print label
                </Button>

                {#if user_privilege > PRIVILEGE_REPORTER}
                  <Button onclick={toggleEdit} class="mb-4">
                    <PenOutline class="me-2 h-5 w-5" /> edit
                  </Button>
                {/if}

                <Button color="light" onclick={onClose} class="mb-4 dark:text-white w-auto">
                  <CloseOutline class="me-2 h-5 w-5" /> close
                </Button>
              {/if}
            </div>
          {/if}
        </form>
      </div>
    </div>
  </div>
  <!-- EXTENDED CARD END -->

</div>