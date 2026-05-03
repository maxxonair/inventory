<script lang="ts">
  import { Label, Input, Textarea, Button, Select, ButtonGroup } from "flowbite-svelte";
  import { MinusOutline, PlusOutline } from "flowbite-svelte-icons";
  import { onMount, onDestroy } from "svelte";

  let { 
    onAdd, 
    onCancel = () => {}
  } = $props();

  // --- Form State ---
  let name = $state("");
  let manufacturer = $state("");
  let manufacturer_link = $state("");
  let manufacturer_location = $state("");
  let number_items = $state(1);
  let item_type = $state("");
  let location = $state("");
  let tags = $state("");
  let material = $state("");
  let color = $state("");
  let project = $state("");
  let product_use = $state("");
  let details = $state("");
  let image = $state(""); // Stores the ID or filename of the uploaded/captured image

  // --- UI/Camera State ---
  let showCameraStream = $state(false);
  let videoEl = $state<HTMLVideoElement | null>(null);
  let stream_error = $state("");
  let camera_error = $state("");
  let media_url = "/api/media/";

  const categories = [
    { value: "Fabric", name: "Fabric" },
    { value: "Flooring", name: "Flooring" },
    { value: "Furniture", name: "Furniture" }
  ];

  // --- Camera Logic ---
  async function toggleCameraVisibility() {
    showCameraStream = !showCameraStream;
    if (showCameraStream) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoEl) videoEl.srcObject = stream;
      } catch (err) {
        stream_error = "Could not access camera.";
      }
    } else {
      stopCamera();
    }
  }

  function stopCamera() {
    if (videoEl?.srcObject) {
      const tracks = (videoEl.srcObject as MediaStream).getTracks();
      tracks.forEach(track => track.stop());
    }
  }

  async function captureImage() {
    // Logic to capture frame from videoEl and upload to /api/upload
    // Then set: image = response.id;
    showCameraStream = false;
    stopCamera();
  }

  // --- File Logic ---
  function handleFileUpload(e: Event) {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (file) {
      // Logic to upload file...
    }
  }

  function onDrop(e: DragEvent) {
    e.preventDefault();
    const file = e.dataTransfer?.files[0];
    if (file) { /* Logic to upload file... */ }
  }

  function onDragOver(e: DragEvent) { e.preventDefault(); }

  function handleSubmit(e: Event) {
    e.preventDefault();
    onAdd({
      name, manufacturer, manufacturer_link, manufacturer_location,
      number_items, item_type, location, tags, material, color,
      project, product_use, details, image
    });
  }

  onDestroy(stopCamera);
</script>

<form onsubmit={handleSubmit} class="mb-2">
  {#if showCameraStream}
    <div class="mb-6 flex flex-col items-center p-2">
      <Label class="mb-2 block p-2">Capture Product Image</Label>
      <Button class="w-full border mb-2" onclick={captureImage}>capture image</Button>
      
      <div class="mb-6 flex flex-col items-center p-2 w-full h-full">
        <p class="text-red-600">{stream_error}</p>
        {#if !stream_error}
          <div class="flex items-center justify-center w-full h-full">
            <!-- svelte-ignore a11y_media_has_caption -->
            <video bind:this={videoEl} autoplay playsinline class="rounded-lg w-full max-h-[80vh] object-contain"></video>
          </div>
        {/if}
      </div>
      
      <Button color="light" class="w-full mb-2" onclick={toggleCameraVisibility}>close camera</Button>
      <Label class="b-2 block">{camera_error}</Label>
    </div>
  {:else}
    <div class="mb-4 p-2 gap-1">
      <div class="mb-4 grid gap-4 md:grid-cols-2">
        <!-- Image Preview -->
        <div class="flex justify-center items-center bg-slate-900 rounded-lg min-h-[220px]">
          {#if image}
            <img src="{media_url}{image}.png" alt="Preview" class="max-w-[220px] max-h-[220px] object-contain" />
          {:else}
            <span class="text-gray-500">No Image</span>
          {/if}
        </div>

        <!-- Primary Fields -->
        <div class="space-y-4">
          <div>
            <Label for="name" class="mb-2">Name</Label>
            <Input id="name" bind:value={name} required placeholder="Item name" />
          </div>
          <div>
            <Label for="manufacturer" class="mb-2">Manufacturer</Label>
            <Input id="manufacturer" bind:value={manufacturer} placeholder="Item manufacturer" />
          </div>
        </div>
      </div>

      <!-- Links and Locations -->
      <div class="grid gap-4 md:grid-cols-2 mt-4">
        <div>
          <Label for="m_link" class="mb-2">Manufacturer Link</Label>
          <Input id="m_link" bind:value={manufacturer_link} placeholder="URL" />
        </div>
        <div>
          <Label for="m_loc" class="mb-2">Manufacturer Location</Label>
          <Input id="m_loc" bind:value={manufacturer_location} placeholder="Location" />
        </div>
      </div>

      <!-- Dropzone -->
      <div class="mt-6 w-full" role="region" ondrop={onDrop} ondragover={onDragOver}>
        <label for="dropzone-file" class="flex flex-col items-center justify-center w-full h-24 border-2 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 border-gray-300">
          <div class="flex flex-col items-center justify-center pt-5 pb-6">
            <p class="text-xs text-gray-500"><span class="font-semibold">Click to upload</span> or drag and drop</p>
          </div>
          <input id="dropzone-file" type="file" class="hidden" onchange={handleFileUpload} />
        </label>
      </div>

      <!-- Item Meta Grid -->
      <div class="grid gap-4 md:grid-cols-2 mt-6">
        <div>
          <Label class="mb-2">Number of Items</Label>
          <ButtonGroup>
            <Button onclick={() => number_items--}><MinusOutline /></Button>
            <Input type="number" bind:value={number_items} class="w-20 text-center" />
            <Button onclick={() => number_items++}><PlusOutline /></Button>
          </ButtonGroup>
        </div>
        <div>
          <Label class="mb-2">Item Type</Label>
          <Select items={categories} bind:value={item_type} />
        </div>
        <div><Label class="mb-2">Storage Location</Label><Input bind:value={location} /></div>
        <div><Label class="mb-2">Tags</Label><Input bind:value={tags} /></div>
        <div><Label class="mb-2">Material</Label><Input bind:value={material} /></div>
        <div><Label class="mb-2">Color</Label><Input bind:value={color} /></div>
        <div><Label class="mb-2">Project</Label><Input bind:value={project} /></div>
        <div><Label class="mb-2">Product Use</Label><Input bind:value={product_use} /></div>
      </div>

      <div class="mt-6">
        <Label class="mb-2">Description</Label>
        <Textarea bind:value={details} placeholder="Detailed description..." rows={3} />
      </div>
    </div>

    <!-- Sticky Footer Actions -->
    <div class="sticky bottom-0 left-0 flex w-full justify-center space-x-4 p-4 bg-white dark:bg-gray-800 border-t z-10">
      <Button type="submit" color="green" class="w-full">add item</Button>
      <Button color="alternative" class="w-full" onclick={toggleCameraVisibility}>open camera</Button>
      <!-- <Button color="light" class="w-full" onclick={onCancel}>cancel</Button> -->
    </div>
  {/if}
</form>