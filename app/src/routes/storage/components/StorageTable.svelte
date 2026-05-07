<script lang="ts">
  import { Input } from "flowbite-svelte";
  import { Section } from "flowbite-svelte-blocks";
  import Pagination from "./Pagination.svelte";

  let {
    filteredStorageLocations,
    totalStorageLocations,
    searchTerm = $bindable(),
    currentPosition = $bindable(),
    onSelect,
  } = $props();
</script>

<Section
  name="advancedTable"
  sectionClass="w-full h-full bg-gray-50 dark:bg-gray-900 p-3 sm:p-5"
>
  <div class="mb-4">
    <Input
      placeholder="Search"
      bind:value={searchTerm}
    />
  </div>

  <div class="grid gap-4 p-2 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5">
    {#each filteredStorageLocations as item (item.id)}
      <button
        class="flex flex-col items-center rounded-lg bg-slate-100 dark:bg-slate-700 p-2 hover:bg-sky-300 dark:hover:bg-sky-700"
        onclick={() => onSelect(item.id)}
      >
        <div class="mt-2 font-bold text-orange-500">
          {item.name}
        </div>
      </button>
    {/each}
  </div>

  <div class="mt-4">
    <Pagination
      totalItems={totalStorageLocations}
      itemsPerPage={50}
      bind:currentPosition={currentPosition}
    />
  </div>
</Section>