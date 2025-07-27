<script>
  // @ts-nocheck

  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { CircleX, HandHelping , Undo2, CircleChevronLeft, CircleChevronRight, Printer , Trash2, SquarePen} from 'lucide-svelte';

  const { user } = $props();
  const media_url = "http://127.0.0.1:5000/media/";
  const streamUrl = "http://localhost:5050";

  let showConfirm = $state(false);
  let showCameraStream = $state(true);
  let itemId = $state(0);
  let error_msg = $state("");
  let error = $state("");
  let item = $state("");

  function requestDelete() {
    showConfirm = true;
  }

  function confirmDelete() {
    deleteItem(itemId);
    showConfirm = false;
    itemId = null;
    showCameraStream = true;
  }

  function cancelDelete() {
    showConfirm = false;
  }

  async function printLabel(itemId) {
    const res = await fetch("http://localhost:5000/print_label", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ itemId }),
    });

    if (!res.ok) {
      error = "Printing Label failed";
    }
  }

  async function checkIsQrScanned() {
    const res = await fetch("http://localhost:5000/is_qr", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });

    if (res.ok) {
      const response = await res.json();
      itemId = response.id;

      // Get the inventory item data from the database
      const ret = await fetch("http://localhost:5000/get_item", {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ itemId }),
      });

      if (!ret.ok) {
        error_msg = "Retrieving inventory item failed";
      } else {
        error_msg = "";
        item = await ret.json();
      }
      // Toggle the camera visibilty and show the item card instead
      showCameraStream = false;
    }
  }

  async function updateItem(itemId, item) {
    // Function TODO
  }

  async function deleteItem(itemId) {
    const res = await fetch("http://localhost:5000/delete_item", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ itemId }),
    });

    if (!res.ok) {
      error = "Deleting Item failed";
    }
  }

  async function checkoutItem(itemId) {
    const res = await fetch("http://localhost:5000/checkout_item", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ itemId }),
    });

    if (!res.ok) {
      error = "Item checkout failed";
    }

    // Update item in the list
    item = {
      ...item,
      is_checked_out: true,
      check_out_poc: "You",
      check_out_date: new Date().toLocaleDateString(),
    };
  }

  async function returnItem(itemId) {
    const res = await fetch("http://localhost:5000/return_item", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ itemId }),
    });

    if (!res.ok) {
      error = "Item return failed";
    }

    // Update item in the list
    item = {
      ...item,
      is_checked_out: false,
      check_out_poc: null,
      check_out_date: null,
    };
  }

  onMount(() => {
    checkIsQrScanned();
    // poll for QR scans every 250 ms
    const interval = setInterval(checkIsQrScanned, 250);
    return () => clearInterval(interval);
  });
</script>

{#if showCameraStream}
  <label for="id" class="label"
    >Place QR code in front of the scanner camera!
  </label>
  <label for="id" class="label">{error_msg}</label>
  <img src={streamUrl} alt="Camera Stream" class="border rounded" />
{:else}
  <!-- Overlay for expanded card -->
  <div class="product-card expanded centered">
    <img
      src={`${media_url}${item.image}.png`}
      alt={item.image}
      class="product-image"
    />
    <div class="product-name">{item.name}</div>
    <div class="manufacturer">by {item.manufacturer}</div>
    <!-- This will show the number of items of this category -->
    <div class="manufacturer">Count: {item.item_type}</div>
    <div class="manufacturer">Type: {item.number_items}</div>

    {#if item.is_checked_out}
      <div class="status-out">
        Checked out by {item.check_out_poc} since {item.check_out_date}
      </div>
    {:else}
      <div class="status-available">Available</div>
    {/if}

    <div class="extra-details">
      <div class="manufacturer">Manufacturer details: {item.details}</div>
    </div>

    <div class="extra-details">
      {#if showConfirm}
        <div class="confirm-card">
          <p>Are you sure you want to delete this item?</p>
          <div class="confirm-actions">
            <button class="confirm-button" onclick={confirmDelete}
              >Yes, Delete</button
            >
            <button class="cancel-button" onclick={cancelDelete}>Cancel</button
            >
          </div>
        </div>
      {:else}
        {#if item.is_checked_out}
          <button class="return-button" onclick={() => returnItem(itemId)}>
            <Undo2 size={20} /> return
          </button>
        {:else}
          <button class="borrow-button" onclick={() => checkoutItem(itemId)}>
            <HandHelping size={20} /> borrow
          </button>
        {/if}
        {#if error}
          <p class="error-message">{error}</p>
        {/if}
        <button class="generic-button" onclick={() => printLabel(itemId)}>
          <Printer size={20} />
          <span>print label</span>
        </button>
        <button class="generic-button" onclick={() => requestDelete()}>
          <Trash2 size={20} />
          <span>delete</span>
        </button>
        <button
          class="generic-button"
          onclick={() => updateItem(itemId, item)}
        >
          <SquarePen size={20} />
          <span>update data</span>
        </button>
      {/if}
    </div>
    <div class="extra-details">
      <button
        class="close-button"
        onclick={() => (
          (itemId = null), (showCameraStream = true), (showConfirm = false)
        )}><CircleX size={20} /> close</button
      >
    </div>
  </div>
{/if}

<style>
  .label {
    justify-content: center;
    text-align: center;
    color: white;
  }

  .product-card.expanded {
    grid-column: 1 / -1;
    transform: scale(1.02);
    z-index: 10;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }

  .product-name {
    font-weight: bold;
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
    color: #fa8d1f;
  }

  .manufacturer {
    color: #d5d5d5;
    margin-bottom: 0.5rem;
  }

  .status-available {
    margin-top: auto;
    font-weight: 500;
    color: green;
  }

  .status-out {
    color: red;
  }

  .borrow-button {
    background-color: #fa8d1f;
    color: #252525;
    border: none;
    border-radius: 9999px;
    padding: 0.5rem;
    margin: 0 auto 1rem;
    cursor: pointer;
    transition: background-color 0.2s ease;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  }

  .return-button {
    background-color: #008c13;
    color: #252525;
    border: none;
    border-radius: 9999px;
    padding: 0.5rem;
    margin: 0 auto 1rem;
    cursor: pointer;
    transition: background-color 0.2s ease;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  }

  .close-button {
    display: flex;
    justify-content: center;
    margin-top: 1rem;
    background-color: #c1c1c1;
    color: #252525;
    border: none;
    border-radius: 9999px;
    padding: 0.5rem;
    margin: 0 auto 1rem;
    cursor: pointer;
    transition: background-color 0.2s ease;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  }

  .lock-scroll {
    overflow: hidden;
  }

  .product-image {
    max-height: 200px;
    object-fit: contain;
    margin-bottom: 1rem;
    border-bottom: 1px solid #d37e1d;
    padding-bottom: 1rem;
  }

  .confirm-card {
    background: rgb(241, 167, 167);
    border: 1px solid #af0000;
    padding: 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    margin-top: 0.5rem;
  }

  .generic-button {
    background-color: #252525;
    color: #fa8d1f;
    border: none;
    border-radius: 9999px;
    padding: 0.5rem;
    margin-bottom: 1rem;
    margin-top: 1rem;
    cursor: pointer;
    transition: background-color 0.2s ease;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    /* display: flex; */
    flex-direction: column;
    align-items: center;
    gap: 4px;
  }

  .confirm-actions {
    display: flex;
    gap: 0.5rem;
    margin-top: 1rem;
  }

  .confirm-button {
    background-color: #f21313;
    color: #181818;
    border: none;
    border-radius: 9999px;
    padding: 0.5rem;
    margin: 0 auto 1rem;
    cursor: pointer;
    transition: background-color 0.2s ease;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  }

  .cancel-button {
    background-color: rgb(63, 63, 63) c13;
    color: #404040;
    border: none;
    border-radius: 9999px;
    padding: 0.5rem;
    margin: 0 auto 1rem;
    cursor: pointer;
    transition: background-color 0.2s ease;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  }
</style>
