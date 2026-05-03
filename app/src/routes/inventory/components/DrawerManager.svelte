<script lang="ts">
  import { Drawer, CloseButton } from "flowbite-svelte";
  import { sineIn } from "svelte/easing";
  import AddItemPanel from "./AddItemPanel.svelte";
  import ScanQrPanel from "./ScanQrPanel.svelte";

  let { activeDrawer, isOpen = $bindable(), onAdd, onScanSuccess } = $props();

  function handleQrMatch(data: string) {
    // Basic parser for your "bigml2;id;9" format
    const parts = data.split(';');
    if (parts[0] === 'bigml2' && parts[1] === 'id') {
      const id = parseInt(parts[2]);
      isOpen = false;
      onScanSuccess(id);
    }
  }
</script>

<!-- @ts-ignore -->
<Drawer bind:open={isOpen} placement="left" id="sidebar4" class="w-3/4">
  <div class="flex items-center justify-between">
    <h5 class="text-base font-semibold uppercase">
      {#if activeDrawer === 'add_item'}
        Add New Item
      {:else if activeDrawer === 'scan_qr'}
        Scan QR Code
      {:else if activeDrawer === 'add_storage'}
        Add Storage Location
      {/if}
    </h5>
  </div>

  <div class="mt-6">
    {#if activeDrawer === 'add_item'}
      <AddItemPanel 
        {onAdd} 
        onCancel={() => (isOpen = false)} 
      />
    {:else if activeDrawer === 'scan_qr'}
      <ScanQrPanel onScanMatch={handleQrMatch} />
    {:else if activeDrawer === 'add_storage'}
      <div class="p-4 bg-yellow-100 text-yellow-800 rounded">
        Storage location management coming soon!
      </div>
    {/if}
  </div>
</Drawer>