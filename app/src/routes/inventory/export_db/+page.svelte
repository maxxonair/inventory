<script lang="ts">
  import { onMount } from "svelte";
  import { Button, Badge, Card } from "flowbite-svelte";
  import { DownloadOutline, FileCsvOutline, InsertTableAltOutline, CheckCircleOutline, ExclamationCircleOutline } from "flowbite-svelte-icons";
  import { createInventoryStore } from "../services/inventory.svelte";
  import { downloadCSV, downloadExcel } from "../services/export";

  const inventory = createInventoryStore();

  let exportStatus = $state<"idle" | "success" | "error">("idle");
  let statusMessage = $state("");
  let lastExportType = $state<"csv" | "xlsx" | "">("");

  onMount(() => {
    inventory.fetchData();
  });

  function withStatus(fn: () => void, type: "csv" | "xlsx") {
    try {
      fn();
      lastExportType = type;
      exportStatus = "success";
      statusMessage = `Exported ${inventory.items.length} items as .${type}`;
    } catch (err) {
      exportStatus = "error";
      statusMessage = "Export failed. See console for details.";
      console.error(err);
    } finally {
      setTimeout(() => {
        exportStatus = "idle";
        statusMessage = "";
      }, 4000);
    }
  }

  function handleCSV() {
    withStatus(() => downloadCSV(inventory.items), "csv");
  }

  function handleExcel() {
    withStatus(() => downloadExcel(inventory.items), "xlsx");
  }
</script>

<div class="w-full px-4 py-10 flex flex-col gap-6">

  <!-- Header -->
  <div>
    <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Export Inventory</h1>
    <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
      Download a snapshot of all inventory items. Images are excluded from all exports.
    </p>
  </div>

  <!-- Status banner -->
  {#if exportStatus === "success"}
    <div class="flex items-center gap-2 px-4 py-3 rounded-lg text-sm font-medium text-green-800 bg-green-50 border border-green-200 dark:bg-gray-800 dark:text-green-400 dark:border-green-800">
      <CheckCircleOutline class="w-4 h-4 shrink-0" />
      {statusMessage}
    </div>
  {:else if exportStatus === "error"}
    <div class="flex items-center gap-2 px-4 py-3 rounded-lg text-sm font-medium text-red-800 bg-red-50 border border-red-200 dark:bg-gray-800 dark:text-red-400 dark:border-red-800">
      <ExclamationCircleOutline class="w-4 h-4 shrink-0" />
      {statusMessage}
    </div>
  {/if}

  <!-- Item count summary -->
  <div class="flex items-center gap-3 px-4 py-3 rounded-lg bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-sm text-gray-700 dark:text-gray-300">
    {#if inventory.loading}
      <span class="italic text-gray-400 dark:text-gray-500">Loading inventory…</span>
    {:else if inventory.error_msg}
      <ExclamationCircleOutline class="w-4 h-4 text-red-500 shrink-0" />
      <span class="text-red-500">{inventory.error_msg}</span>
    {:else}
      <span>
        <span class="font-semibold text-gray-900 dark:text-white">{inventory.items.length}</span>
        item{inventory.items.length === 1 ? "" : "s"} ready to export
      </span>
      {#if inventory.items.length === 0}
        <Badge color="yellow">Empty</Badge>
      {/if}
    {/if}
  </div>

  <!-- Export cards -->
  <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">

    <!-- CSV -->
    <div class="flex flex-col gap-3 p-5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 shadow-sm">
      <div class="flex items-center gap-3">
        <div class="p-2 rounded-lg bg-blue-50 dark:bg-blue-900/30">
          <FileCsvOutline class="w-6 h-6 text-blue-600 dark:text-blue-400" />
        </div>
        <div>
          <p class="font-semibold text-gray-900 dark:text-white text-sm">CSV</p>
          <p class="text-xs text-gray-400 dark:text-gray-500">Comma-separated values</p>
        </div>
      </div>
      <p class="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
        Compatible with Excel, Google Sheets, and most data tools. Best for flat data import/export.
      </p>
      <Button
        color="blue"
        size="sm"
        class="w-full mt-auto"
        disabled={inventory.loading || inventory.items.length === 0}
        onclick={handleCSV}
      >
        <DownloadOutline class="mr-2 h-4 w-4" /> Download .csv
      </Button>
    </div>

    <!-- Excel -->
    <div class="flex flex-col gap-3 p-5 rounded-xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 shadow-sm">
      <div class="flex items-center gap-3">
        <div class="p-2 rounded-lg bg-green-50 dark:bg-green-900/30">
          <InsertTableAltOutline class="w-6 h-6 text-green-600 dark:text-green-400" />
        </div>
        <div>
          <p class="font-semibold text-gray-900 dark:text-white text-sm">Excel</p>
          <p class="text-xs text-gray-400 dark:text-gray-500">XLSX workbook</p>
        </div>
      </div>
      <p class="text-xs text-gray-500 dark:text-gray-400 leading-relaxed">
        Native Excel format with a dedicated Inventory sheet. Best for reporting and sharing with stakeholders.
      </p>
      <Button
        color="green"
        size="sm"
        class="w-full mt-auto"
        disabled={inventory.loading || inventory.items.length === 0}
        onclick={handleExcel}
      >
        <DownloadOutline class="mr-2 h-4 w-4" /> Download .xlsx
      </Button>
    </div>

  </div>

  <!-- Notes -->
  <div class="text-xs text-gray-400 dark:text-gray-500 leading-relaxed space-y-1">
    <p>· Exports always reflect the current state of the database at the time of the download.</p>
    <p>· Images and avatars are excluded from all export formats.</p>
  </div>

</div>