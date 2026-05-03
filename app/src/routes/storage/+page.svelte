<script lang="ts">
  import { onMount } from "svelte";
  import { Card, Badge, Button, Input } from "flowbite-svelte";
  import { SearchOutline, MapPinAltSolid, CubeSolid } from "flowbite-svelte-icons";
  import { createStorageLocationStore } from "./services/storage.svelte";

  const storage_registry = createStorageLocationStore();
  let searchTerm = $state("");

  onMount(() => {
    storage_registry.fetchData();
  });

  // Extract unique locations and count items in each
  let storageLocations = $derived.by(() => {
    const locationsMap = new Map();
    
    storage_registry.storage_locations.forEach(item => {
      const loc = item.name || "Unassigned";
      if (!locationsMap.has(loc)) {
        locationsMap.set(loc, { name: loc, count: 0, items: [] });
      }
      locationsMap.get(loc).count++;
      locationsMap.get(loc).items.push(item);
    });

    const list = Array.from(locationsMap.values());
    
    if (!searchTerm) return list;
    return list.filter(l => l.name.toLowerCase().includes(searchTerm.toLowerCase()));
  });
</script>

<div class="p-4 space-y-6">
  <div class="flex flex-col md:flex-row justify-between items-center gap-4">
    <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Storage Locations</h1>
    
    <div class="w-full md:w-96">
      <Input placeholder="Search locations..." bind:value={searchTerm}>
        <!-- <SearchOutline slot="left" class="w-5 h-5" /> -->
      </Input>
    </div>
  </div>

  <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
    {#each storageLocations as location}
      <Card class="hover:shadow-lg transition-shadow">
        <div class="flex items-start justify-between">
          <div class="p-3 bg-primary-100 dark:bg-primary-900 rounded-lg">
            <MapPinAltSolid class="w-6 h-6 text-primary-600 dark:text-primary-400" />
          </div>
          <Badge color="indigo" rounded>{location.count} Items</Badge>
        </div>

        <h5 class="mt-4 text-xl font-bold tracking-tight text-gray-900 dark:text-white">
          {location.name}
        </h5>
        
        <p class="mb-5 font-normal text-gray-700 dark:text-gray-400 leading-tight">
          Manage storage_registry stored in this specific zone.
        </p>

        <div class="flex gap-2">
          <Button size="sm" color="alternative" class="w-full">
            <CubeSolid class="w-4 h-4 mr-2" />
            View Items
          </Button>
        </div>
      </Card>
    {/each}
  </div>

  {#if storageLocations.length === 0}
    <div class="text-center py-20">
      <p class="text-gray-500">No storage locations found matching your search.</p>
    </div>
  {/if}
</div>