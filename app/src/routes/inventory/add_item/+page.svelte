<script lang="ts">
  import { Label, Input, Textarea, Button, Select, ButtonGroup, Badge } from "flowbite-svelte";
  import { MinusOutline, PlusOutline } from "flowbite-svelte-icons";
  import { onDestroy, onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { media_url, captureImage, uploadImage, item_categories } from "../services/inventory.svelte";

  let name = $state("");
  let manufacturer = $state("");
  let manufacturer_link = $state("");
  let manufacturer_location = $state("");
  let number_items = $state(1);
  let item_type = $state("");
  let location = $state<number | "">("");
  let tagList = $state<string[]>([]);
  let tagInput = $state("");
  let material = $state("");
  let color = $state("");
  let project = $state("");
  let product_use = $state("");
  let details = $state("");
  let image = $state("");
  let error_msg = $state("");
  let tmp_image = $state('');

  let showCameraStream = $state(false);
  let videoEl = $state<HTMLVideoElement | null>(null);
  let stream_error = $state("");
  let camera_error = $state("");

  let storageLocations = $state<{ value: number; name: string }[]>([]);
  let storageLocationsError = $state("");

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

  // Tag helpers
  function addTag() {
    const val = tagInput.trim().replace(/,/g, "");
    if (val && !tagList.includes(val) && tagList.length < 20) {
      tagList = [...tagList, val];
    }
    tagInput = "";
  }

  function removeTag(i: number) {
    tagList = tagList.filter((_, idx) => idx !== i);
  }

  function handleTagKeydown(e: KeyboardEvent) {
    if (e.key === "Enter" || e.key === ",") {
      e.preventDefault();
      addTag();
    } else if (e.key === "Backspace" && tagInput === "" && tagList.length) {
      tagList = tagList.slice(0, -1);
    }
  }

  async function toggleCameraVisibility() {
    showCameraStream = !showCameraStream;
    if (showCameraStream) {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoEl) videoEl.srcObject = stream;
      } catch (err) {
        stream_error = "Could not access camera.";
        camera_error = String(err);
        showCameraStream = false;
      }
    } else {
      stopCamera();
    }
  }

  function stopCamera() {
    if (videoEl?.srcObject) {
      (videoEl.srcObject as MediaStream).getTracks().forEach(t => t.stop());
    }
  }

  async function handleImageCapture() {
    const result = await captureImage(videoEl);
    camera_error = result.error;

    if (camera_error === "") {
      image = result.image;
      showCameraStream = false;
      stopCamera();
    }
  }

  async function handleFileUpload(e: Event) {
    const file = (e.target as HTMLInputElement).files?.[0];
    if (file) await processImageFile(file);
  }

  async function onDrop(e: DragEvent) {
    e.preventDefault();
    const file = e.dataTransfer?.files[0];
    if (file) await processImageFile(file);
  }

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
    }
  }

  function onDragOver(e: DragEvent) { e.preventDefault(); }

  async function handleSubmit(e: Event) {
    if (!name) return;
    try {
      const date_added = new Date().toISOString();
      const res = await fetch(`/api/add_item`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name, manufacturer, manufacturer_link, manufacturer_location,
          number_items, item_type,
          location: location === "" ? null : location,
          tags: tagList.join(","),
          material, color, project, product_use, details, image, date_added,
        }),
      });
      if (res.status === 401) {goto('/login');}
      if (!res.ok) {
        error_msg = "Adding Item Failed";
      } else {
        error_msg = "";
        const data = await res.json();
        const newId = data.message;
      }
    } catch (err) {
      error_msg = "Network error while adding item.";
    } finally {
      goto('/inventory');
    }
  }

  onDestroy(stopCamera);
</script>

<div class="w-full bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-200 dark:border-gray-700 overflow-hidden">

  <!-- Top bar -->
  <div class="flex items-center justify-between px-6 py-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
    <div>
      <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Add inventory item</h2>
      <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">Fill in the details below to register a new item.</p>
    </div>
    <div class="flex items-center gap-2">
      {#if !showCameraStream}
        <Button color="alternative" size="sm" onclick={toggleCameraVisibility}>Open camera</Button>
        <Button color="green" size="sm" onclick={handleSubmit}>Add item</Button>
      {/if}
    </div>
  </div>

  {#if error_msg}
    <div class="flex items-center gap-2 px-6 py-3 text-sm text-red-800 bg-red-50 dark:bg-gray-800 dark:text-red-400 border-b border-red-200 dark:border-red-800">
      <svg class="w-4 h-4 shrink-0" fill="currentColor" viewBox="0 0 20 20">
        <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5Zm1 13a1 1 0 1 1-2 0 1 1 0 0 1 2 0Zm-1-8a1 1 0 0 1 1 1v3a1 1 0 1 1-2 0V6.5a1 1 0 0 1 1-1Z"/>
      </svg>
      {error_msg}
    </div>
  {/if}

  {#if showCameraStream}
    <div class="flex flex-col items-center gap-4 p-8">
      <p class="text-sm font-medium text-gray-700 dark:text-gray-300">Capture product image</p>
      {#if stream_error}
        <p class="text-sm text-red-500">{stream_error}</p>
      {:else}
        <!-- svelte-ignore a11y_media_has_caption -->
        <video bind:this={videoEl} autoplay playsinline
          class="w-full max-w-lg rounded-xl border border-gray-200 dark:border-gray-700"></video>
      {/if}
      {#if camera_error}
        <p class="text-xs text-gray-400">{camera_error}</p>
      {/if}
      <div class="flex gap-3">
        <Button size="sm" onclick={handleImageCapture}>Capture image</Button>
        <Button color="alternative" size="sm" onclick={toggleCameraVisibility}>Cancel</Button>
      </div>
    </div>

  {:else}
    <form onsubmit={handleSubmit}>
      <div class="flex flex-col md:flex-row">

        <!-- Left: image panel -->
        <div class="md:w-64 lg:w-80 shrink-0 bg-gray-100 dark:bg-gray-800 flex flex-col items-center justify-start p-6 gap-4 border-b md:border-b-0 md:border-r border-gray-200 dark:border-gray-700">
          <div class="w-full aspect-square rounded-xl overflow-hidden bg-gray-200 dark:bg-gray-700 flex items-center justify-center">
            {#if image}
              <img src="{media_url}{image}.png" alt="Preview" class="w-full h-full object-contain" />
            {:else}
              <svg class="w-16 h-16 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5"
                  d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
            {/if}
          </div>

          <label for="dropzone-file"
            class="flex flex-col items-center justify-center w-full h-24 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-lg cursor-pointer bg-gray-50 dark:bg-gray-700 hover:bg-gray-100 dark:hover:bg-gray-600 transition-colors"
            ondrop={onDrop} ondragover={onDragOver}
          >
            <p class="text-xs text-gray-500 dark:text-gray-400 text-center px-2">
              <span class="font-semibold">Click to upload</span> or drag & drop<br/>
              <span class="text-gray-400">SVG, PNG, JPG</span>
            </p>
            <input id="dropzone-file" type="file" class="hidden" onchange={handleFileUpload} />
          </label>
        </div>

        <!-- Right: fields -->
        <div class="flex-1 p-6 lg:p-8">
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-6 gap-y-5">

            <div>
              <p class="text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-1.5">Name <span class="text-red-500">*</span></p>
              <Input bind:value={name} placeholder="Item name" required />
            </div>

            <div>
              <p class="text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-1.5">Manufacturer</p>
              <Input bind:value={manufacturer} placeholder="Brand or maker" />
            </div>

            <div>
              <p class="text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-1.5">Manufacturer Link</p>
              <Input bind:value={manufacturer_link} placeholder="https://…" />
            </div>

            <div>
              <p class="text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-1.5">Manufacturer Location</p>
              <Input bind:value={manufacturer_location} placeholder="City, Country" />
            </div>

            <div>
              <p class="text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-1.5">Count</p>
              <ButtonGroup>
                <Button type="button" onclick={() => number_items = Math.max(0, number_items - 1)}>
                  <MinusOutline class="h-4 w-4" />
                </Button>
                <Input type="number" bind:value={number_items} class="w-20 text-center" />
                <Button type="button" onclick={() => number_items++}>
                  <PlusOutline class="h-4 w-4" />
                </Button>
              </ButtonGroup>
            </div>

            <div>
              <p class="text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-1.5">Item Type</p>
              <Select items={item_categories} bind:value={item_type} />
            </div>

            <!-- Storage Location -->
            <div>
              <p class="text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-1.5">Storage Location</p>
              {#if storageLocationsError}
                <p class="text-xs text-red-500">{storageLocationsError}</p>
              {:else if storageLocations.length === 0}
                <p class="text-xs text-gray-400 dark:text-gray-500 italic">Loading locations…</p>
              {:else}
                <Select items={[ ...storageLocations]} bind:value={location} />
              {/if}
            </div>

            <!-- Tags pill input -->
            <div>
              <p class="text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-1.5">Tags</p>
              <!-- svelte-ignore a11y_click_events_have_key_events a11y_no_static_element_interactions -->
              <div
                class="flex flex-wrap gap-1.5 items-center min-h-[42px] w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus-within:ring-1 focus-within:ring-blue-500 focus-within:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white p-2 cursor-text"
                onclick={() => document.getElementById('tag-input')?.focus()}
              >
                {#each tagList as tag, i}
                  <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300">
                    {tag}
                    <button
                      type="button"
                      onclick={() => removeTag(i)}
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
                  id="tag-input"
                  type="text"
                  bind:value={tagInput}
                  onkeydown={handleTagKeydown}
                  placeholder={tagList.length === 0 ? "Type and press Enter…" : ""}
                  class="flex-1 min-w-[120px] bg-transparent border-none outline-none text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 p-0"
                />
              </div>
              <p class="mt-1 text-xs text-gray-400 dark:text-gray-500">
                Press <kbd class="px-1 py-0.5 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-200 rounded dark:bg-gray-600 dark:text-gray-100 dark:border-gray-500">Enter</kbd>
                or <kbd class="px-1 py-0.5 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-200 rounded dark:bg-gray-600 dark:text-gray-100 dark:border-gray-500">,</kbd>
                to add · Backspace to remove
              </p>
            </div>

            <div>
              <p class="text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-1.5">Material</p>
              <Input bind:value={material} placeholder="e.g. Steel, Oak" />
            </div>

            <div>
              <p class="text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-1.5">Color</p>
              <Input bind:value={color} placeholder="e.g. Charcoal grey" />
            </div>

            <div>
              <p class="text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-1.5">Project</p>
              <Input bind:value={project} placeholder="Associated project" />
            </div>

            <div>
              <p class="text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-1.5">Product Use</p>
              <Input bind:value={product_use} placeholder="Intended use" />
            </div>

            <div class="sm:col-span-2">
              <p class="text-xs font-medium uppercase tracking-wide text-gray-400 dark:text-gray-500 mb-1.5">Details</p>
              <Textarea bind:value={details} placeholder="Additional notes, specifications…" rows={3} class="w-full" />
            </div>

          </div>
        </div>
      </div>
    </form>
  {/if}
</div>