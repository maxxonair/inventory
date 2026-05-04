<script>
  import Header from "./Header.svelte";
  import { onMount } from "svelte";
  import { fetchUser } from "$lib/stores/auth.js";
  import "../app.css";
  
  import { Sidebar, SidebarGroup, SidebarItem, SidebarDropdownWrapper } from 'flowbite-svelte';
  import { HomeSolid, ArchiveSolid, CogSolid } from 'flowbite-svelte-icons';
  import { goto } from "$app/navigation";

  let { children } = $props();
  let isMinimized = $state(false);

  const spanClass = "flex-1 ms-3 whitespace-nowrap";

  function toggleSidebar() {
    isMinimized = !isMinimized;
  }

  onMount(fetchUser);
</script>

<!-- Outer container: Horizontal Flex -->
<div class="flex h-screen w-full bg-gray-50 dark:bg-gray-900 overflow-hidden">
  
  <!-- 1. Sidebar: Use a standard HTML 'aside' only -->
  <aside 
    class="flex flex-col h-full transition-all duration-300 ease-in-out border-r border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 z-40 flex-shrink-0 overflow-hidden"
    style:width={isMinimized ? '64px' : '280px'}
  >
    <!-- Replacing SidebarWrapper with a plain div to avoid forced widths -->
    <div class="flex-1 px-3 py-4 overflow-y-auto overflow-x-hidden">
      <nav class="space-y-2">

        <SidebarDropdownWrapper 
          label={isMinimized ? "" : "Inventory"}
          class="group"
        >
          {#snippet icon()}
            <!-- Force the main icon size -->
            <HomeSolid class="w-4 h-4 flex-shrink-0" />
          {/snippet}

          {#snippet arrowdown()}
            <svg class="w-4 h-4 text-gray-500 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          {/snippet}

          {#snippet arrowup()}
            <svg class="w-4 h-4 text-gray-500 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          {/snippet}

          <!-- Dropdown Items -->
          <div class="group">
            <SidebarItem 
              label={isMinimized ? "" : "Inventory"}
              href="/inventory"
              class="group text-slate-800 hover:bg-sky-100 dark:hover:bg-slate-700 dark:text-slate-300 dark:hover:text-slate-100"
            ></SidebarItem>

            <SidebarItem 
              label={isMinimized ? "" : "Add Item"}
              href="/inventory/add_item"
              class="group text-slate-800 dark:text-slate-300 hover:bg-sky-100 dark:hover:bg-slate-700 dark:hover:text-slate-100"
            ></SidebarItem>
          </div>
        </SidebarDropdownWrapper>

        <SidebarDropdownWrapper 
          label={isMinimized ? "" : "Storage Locations"}
          class="group"
        >
          {#snippet icon()}
            <!-- Force the main icon size -->
            <ArchiveSolid class="w-4 h-4 flex-shrink-0" />
          {/snippet}

          {#snippet arrowdown()}
            <svg class="w-4 h-4 text-gray-500 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          {/snippet}

          {#snippet arrowup()}
            <svg class="w-4 h-4 text-gray-500 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          {/snippet}

          <!-- Dropdown Items -->
          <div class="group">
            <SidebarItem  
              label={isMinimized ? "" : "Storage Overview"}
              href="/storage"
              class="group text-slate-800 hover:bg-sky-100 dark:hover:bg-slate-700 dark:text-slate-300 dark:hover:text-slate-100"
            ></SidebarItem>

            <SidebarItem 
              label={isMinimized ? "" : "Add Storage Location"}
              href="/storage/add_storage"
              class="group text-slate-800 dark:text-slate-300 hover:bg-sky-100 dark:hover:bg-slate-700 dark:hover:text-slate-100"
            ></SidebarItem>
          </div>
        </SidebarDropdownWrapper>

        <SidebarItem 
          href="/settings" 
          label={isMinimized ? "" : "Settings"} class={spanClass}
        >
          <!-- {#snippet icon()}
            <CogSolid class="w-4 h-4 flex-shrink-0" />
          {/snippet} -->
        </SidebarItem>

      </nav>
    </div>
  </aside>

  <!-- 2. Right Side: Vertical Flex (Header + Content) -->
  <div class="flex flex-col flex-1 min-w-0 overflow-hidden">
    <Header {toggleSidebar} />
    <main class="flex-1 overflow-y-auto px-4 py-6 md:px-8">
      {@render children()}
    </main>
  </div>
</div>