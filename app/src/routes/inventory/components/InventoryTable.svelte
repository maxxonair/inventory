<!-- InventoryTable.svelte -->
<script lang="ts">
  import { Input, Select, Button, Badge } from "flowbite-svelte";
  import { SearchOutline, FilterOutline, CloseOutline } from "flowbite-svelte-icons";
  import Pagination from "./Pagination.svelte";

  let {
    items,
    totalItems,
    searchTerm = $bindable(),
    currentPosition = $bindable(),
    onSelect,
    allStorageLocations = [],
    allManufacturer = [],
    allTags = [],
  }: {
    items: any[];
    totalItems: number;
    searchTerm: string;
    currentPosition: number;
    onSelect: (id: number) => void;
    allStorageLocations?: { value: number; name: string }[];
    allManufacturer?: string[];
    allTags?: string[];
  } = $props();

  const media_url = `/api/media/`;

  // --- Filter state ---
  let selectedLocation       = $state<number | "">("");
  let selectedTag            = $state("");
  let selectedManufacturer   = $state("");
  let selectedAvailability   = $state<"" | "available" | "checked_out">("");

  // --- Dropdown options ---
  let locationOptions = $derived([
    { value: "", name: "All locations" },
    ...allStorageLocations,
  ]);

  let tagOptions = $derived([
    { value: "", name: "All tags" },
    ...allTags.map(t => ({ value: t, name: t })),
  ]);

  let mfgLocationOptions = $derived([
    { value: "", name: "All manufacturer locations" },
    ...allManufacturer.map(ml => ({ value: ml, name: ml })),
  ]);

  const availabilityOptions = [
    { value: "",            name: "Any availability" },
    { value: "available",   name: "Available" },
    { value: "checked_out", name: "Checked out" },
  ];

  // --- Active filter count ---
  let activeFilterCount = $derived(
    [selectedLocation, selectedTag, selectedManufacturer, selectedAvailability]
      .filter(v => v !== "").length
  );

  // --- Client-side filtering on top of the store's search-filtered items ---
  let displayedItems = $derived((() => {
    let results = items;

    if (selectedLocation !== "") {
      results = results.filter(i => i.location === selectedLocation);
    }
    if (selectedTag) {
      results = results.filter(i =>
        i.tags?.split(",").map((t: string) => t.trim()).includes(selectedTag)
      );
    }
    if (selectedManufacturer) {
      results = results.filter(i => i.manufacturer === selectedManufacturer);
    }
    if (selectedAvailability !== "") {
      const wantCheckedOut = selectedAvailability === "checked_out";
      results = results.filter(i => !!i.is_checked_out === wantCheckedOut);
    }

    return results;
  })());

  function clearFilters() {
    selectedLocation     = "";
    selectedTag          = "";
    selectedManufacturer  = "";
    selectedAvailability = "";
    searchTerm           = "";
  }
</script>

<div class="w-full h-full bg-gray-50 dark:bg-gray-900 p-3 sm:p-5 flex flex-col gap-4">

  <!-- Search + filter row -->
  <div class="flex flex-col gap-3">

    <div class="flex items-center gap-3">
      <div class="relative flex-1">
        <div class="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
          <SearchOutline class="h-5 w-5 text-gray-500 dark:text-gray-400" />
        </div>
        <Input type="search" placeholder="Search items…" bind:value={searchTerm} class="pl-10" />
      </div>

      {#if activeFilterCount > 0}
        <Button color="alternative" size="sm" onclick={clearFilters}>
          <CloseOutline class="mr-1.5 h-4 w-4" />
          Clear
          <span class="ml-1.5 inline-flex items-center justify-center w-4 h-4 text-xs font-bold text-white bg-blue-500 rounded-full">
            {activeFilterCount}
          </span>
        </Button>
      {/if}
    </div>

    <!-- Filter dropdowns -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
      <Select placeholder="Filter by storage location" items={locationOptions}     bind:value={selectedLocation}     size="sm" />
      <Select placeholder="Filter by tags" items={tagOptions}          bind:value={selectedTag}           size="sm" />
      <Select placeholder="Filter by manufacturer" items={mfgLocationOptions}  bind:value={selectedManufacturer}   size="sm" />
      <Select placeholder="Filter by availability" items={availabilityOptions} bind:value={selectedAvailability}  size="sm" />
    </div>

    <!-- Active filter pills -->
    {#if activeFilterCount > 0}
      <div class="flex flex-wrap gap-2 items-center">
        <span class="text-xs text-gray-400 dark:text-gray-500">Filtering by:</span>
        {#if selectedLocation !== ""}
          <Badge color="blue" dismissable onclick={() => selectedLocation = ""}>
            Location: {locationOptions.find(l => l.value === selectedLocation)?.name}
          </Badge>
        {/if}
        {#if selectedTag}
          <Badge color="blue" dismissable onclick={() => selectedTag = ""}>
            Tag: {selectedTag}
          </Badge>
        {/if}
        {#if selectedManufacturer}
          <Badge color="blue" dismissable onclick={() => selectedManufacturer = ""}>
            Made in: {selectedManufacturer}
          </Badge>
        {/if}
        {#if selectedAvailability}
          <Badge color={selectedAvailability === "available" ? "green" : "red"} dismissable onclick={() => selectedAvailability = ""}>
            {selectedAvailability === "available" ? "Available" : "Checked out"}
          </Badge>
        {/if}
      </div>
    {/if}

  </div>

  <!-- Result count -->
  <p class="text-xs text-gray-400 dark:text-gray-500">
    Showing {displayedItems.length} of {totalItems} item{totalItems === 1 ? "" : "s"}
  </p>

  <!-- Tile grid -->
  <div class="grid gap-4 grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5">
    {#each displayedItems as item (item.id)}
      <button
        onclick={() => onSelect(item.id)}
        class="group flex flex-col bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-sm overflow-hidden hover:shadow-md hover:border-blue-400 dark:hover:border-blue-500 transition-all duration-150 text-left"
      >
        <!-- Image -->
        <div class="relative w-full aspect-square bg-gray-100 dark:bg-gray-700 overflow-hidden">
          <img
            src="{media_url}thumbnail_{item.image}.png"
            alt={item.name}
            class="w-full h-full object-contain p-2 group-hover:scale-105 transition-transform duration-150"
          />
          <span class="absolute top-2 right-2 text-xs font-semibold px-2 py-0.5 rounded-full
            {item.is_checked_out
              ? 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'
              : 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'}">
            {item.is_checked_out ? 'Checked out' : 'Available'}
          </span>
        </div>
        <!-- Info -->
        <div class="flex flex-col gap-0.5 px-3 py-2.5 border-t border-gray-100 dark:border-gray-700">
          <p class="text-sm font-semibold text-gray-900 dark:text-white truncate">{item.name}</p>
          <p class="text-xs text-gray-500 dark:text-gray-400 truncate">{item.manufacturer || '—'}</p>
        </div>
      </button>
    {/each}

    {#if displayedItems.length === 0}
      <div class="col-span-full flex flex-col items-center justify-center py-16 text-center gap-2">
        <FilterOutline class="w-8 h-8 text-gray-300 dark:text-gray-600" />
        <p class="text-sm text-gray-500 dark:text-gray-400">No items match the current filters.</p>
        <Button color="alternative" size="xs" onclick={clearFilters}>Clear filters</Button>
      </div>
    {/if}
  </div>

  <div class="mt-auto">
    <Pagination
      totalItems={totalItems}
      itemsPerPage={50}
      bind:currentPosition={currentPosition}
    />
  </div>

</div>