<script lang="ts">
  let name = $state("");
  let description = $state("");
  let tagInput = $state("");
  let tags = $state<string[]>([]);
  let submitting = $state(false);
  let status = $state<{ type: 'success' | 'error'; message: string } | null>(null);

  let canSubmit = $derived(name.trim().length > 0 && !submitting);

  function addTag() {
    const val = tagInput.trim().replace(/,/g, '');
    if (val && !tags.includes(val) && tags.length < 20) {
      tags = [...tags, val];
    }
    tagInput = "";
  }

  function removeTag(i: number) {
    tags = tags.filter((_, idx) => idx !== i);
  }

  function handleTagKeydown(e: KeyboardEvent) {
    if (e.key === 'Enter' || e.key === ',') {
      e.preventDefault();
      addTag();
    } else if (e.key === 'Backspace' && tagInput === '' && tags.length) {
      tags = tags.slice(0, -1);
    }
  }

  function reset() {
    name = "";
    description = "";
    tagInput = "";
    tags = [];
    status = null;
  }

  async function submit() {
    if (!canSubmit) return;
    submitting = true;
    status = null;

    const payload = {
      name: name.trim(),
      description: description.trim() || null,
      date_added: new Date().toISOString().slice(0, 10),
      tags: tags.length ? tags.join(',') : null,
    };

    try {
      const res = await fetch('/api/add_storage', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
        credentials: 'include',
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.error || 'Server error');
      }
      const data = await res.json();
      status = { type: 'success', message: `Storage location added successfully (ID: ${data.message})` };
      reset();
    } catch (err: any) {
      status = { type: 'error', message: err.message || 'Failed to add storage location. Please try again.' };
    } finally {
      submitting = false;
    }
  }
</script>

<div class="p-4 sm:p-6 lg:p-8">
  <div class="w-full">

    <!-- Back link -->
    <nav class="mb-6">
      <a href="/storage" class="inline-flex items-center text-sm font-medium text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
        <svg class="w-4 h-4 me-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
        </svg>
        Storage locations
      </a>
    </nav>

    <!-- Page heading -->
    <div class="mb-6">
      <h1 class="text-2xl font-semibold text-gray-900 dark:text-white">Add storage location</h1>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        Define a new physical or logical location for inventory items.
      </p>
    </div>

    <!-- Status alert -->
    {#if status}
      {#if status.type === 'success'}
        <div class="flex items-center p-2 mb-6 text-sm text-green-800 rounded-lg bg-green-50 dark:bg-gray-800 dark:text-green-400 border border-green-300 dark:border-green-800" role="alert">
          <svg class="shrink-0 inline w-4 h-4 me-3" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5Zm3.707 8.207-4 4a1 1 0 0 1-1.414 0l-2-2a1 1 0 0 1 1.414-1.414L9 10.586l3.293-3.293a1 1 0 0 1 1.414 1.414Z"/>
          </svg>
          <span>{status.message}</span>
          <button onclick={() => status = null} aria-label="Close" class="ms-auto text-green-800 dark:text-green-400 hover:opacity-70">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      {:else}
        <div class="flex items-center p-4 mb-6 text-sm text-red-800 rounded-lg bg-red-50 dark:bg-gray-800 dark:text-red-400 border border-red-300 dark:border-red-800" role="alert">
          <svg class="shrink-0 inline w-4 h-4 me-3" fill="currentColor" viewBox="0 0 20 20">
            <path d="M10 .5a9.5 9.5 0 1 0 9.5 9.5A9.51 9.51 0 0 0 10 .5Zm1 13a1 1 0 1 1-2 0 1 1 0 0 1 2 0Zm-1-8a1 1 0 0 1 1 1v3a1 1 0 1 1-2 0V6.5a1 1 0 0 1 1-1Z"/>
          </svg>
          <span>{status.message}</span>
          <button onclick={() => status = null} aria-label="Close" class="ms-auto text-red-800 dark:text-red-400 hover:opacity-70">
            <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>
      {/if}
    {/if}

    <!-- Card -->
    <div class="bg-white border border-gray-200 rounded-lg shadow-sm dark:bg-gray-800 dark:border-gray-700">
      <div class="p-6 space-y-6">

        <!-- Name -->
        <div>
          <label for="name" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
            Location name <span class="text-red-500">*</span>
          </label>
          <input
            id="name"
            type="text"
            bind:value={name}
            maxlength="255"
            placeholder="e.g. Warehouse A — Shelf 3"
            autocomplete="off"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
          />
          <p class="mt-1.5 text-xs text-gray-400 dark:text-gray-500 text-right">{name.length} / 255</p>
        </div>

        <!-- Description -->
        <div>
          <label for="description" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
            Description
          </label>
          <textarea
            id="description"
            bind:value={description}
            maxlength="1055"
            rows="4"
            placeholder="Optional notes about this location — capacity, access requirements, temperature range…"
            class="block w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 p-2.5 resize-y"
          ></textarea>
          <p class="mt-1.5 text-xs text-right {description.length > 950 ? 'text-yellow-500' : 'text-gray-400 dark:text-gray-500'}">{description.length} / 1055</p>
        </div>

        <!-- Tags -->
        <div>
          <label class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Tags</label>
          <!-- Tag pill container -->
          <div
            class="flex flex-wrap gap-2 items-center min-h-[42px] w-full text-sm text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus-within:ring-1 focus-within:ring-blue-500 focus-within:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white p-2 cursor-text"
            onclick={() => document.getElementById('tagInput')?.focus()}
          >
            {#each tags as tag, i}
              <span class="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300">
                {tag}
                <button
                  type="button"
                  onclick={() => removeTag(i)}
                  class="inline-flex items-center p-0.5 ms-1 text-xs text-blue-400 bg-transparent rounded-full hover:bg-blue-200 hover:text-blue-900 dark:hover:bg-blue-800 dark:hover:text-blue-300"
                  aria-label="Remove tag {tag}"
                >
                  <svg class="w-2 h-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M6 18L18 6M6 6l12 12"/>
                  </svg>
                </button>
              </span>
            {/each}
            <input
              id="tagInput"
              type="text"
              bind:value={tagInput}
              onkeydown={handleTagKeydown}
              placeholder={tags.length === 0 ? 'Type and press Enter to add a tag…' : ''}
              class="flex-1 min-w-[140px] bg-transparent border-none outline-none text-sm text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 p-0"
            />
          </div>
          <p class="mt-1.5 text-xs text-gray-400 dark:text-gray-500">
            Press <kbd class="px-1 py-0.5 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-200 rounded dark:bg-gray-600 dark:text-gray-100 dark:border-gray-500">Enter</kbd>
            or <kbd class="px-1 py-0.5 text-xs font-semibold text-gray-800 bg-gray-100 border border-gray-200 rounded dark:bg-gray-600 dark:text-gray-100 dark:border-gray-500">,</kbd>
            to add a tag. Backspace removes the last one.
          </p>
        </div>

      </div>

      <!-- Card footer / actions -->
      <div class="flex items-center justify-end gap-3 px-6 py-4 border-t border-gray-200 dark:border-gray-700 rounded-b-lg bg-gray-50 dark:bg-gray-800">
        <button
          type="button"
          onclick={reset}
          class="py-2.5 px-5 text-sm font-medium text-gray-900 focus:outline-none bg-white rounded-lg border border-gray-200 hover:bg-gray-100 hover:text-blue-700 focus:z-10 focus:ring-4 focus:ring-gray-100 dark:focus:ring-gray-700 dark:bg-gray-800 dark:text-gray-400 dark:border-gray-600 dark:hover:text-white dark:hover:bg-gray-700"
        >
          Clear
        </button>
        <button
          type="button"
          onclick={submit}
          disabled={!canSubmit}
          class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 dark:bg-blue-600 dark:hover:bg-blue-700 focus:outline-none dark:focus:ring-blue-800 disabled:opacity-50 disabled:cursor-not-allowed inline-flex items-center gap-2"
        >
          {#if submitting}
            <svg class="animate-spin w-4 h-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"/>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
            </svg>
            Saving…
          {:else}
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            Add location
          {/if}
        </button>
      </div>
    </div>

  </div>
</div>