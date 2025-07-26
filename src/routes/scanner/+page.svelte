<script>
  // @ts-nocheck

  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { CircleX, HandHelping, Undo2 } from "lucide-svelte";

  const { user } = $props();
  let streamUrl = "http://localhost:5050";

  // let showCameraStream = $state(1);
  let showCameraStream = $state(true);
  let itemId = $state(0);
  let error_msg = $state("");
  let error = $state("");
  let item = $state("");

  const media_url = "http://127.0.0.1:5000/media/";

  async function checkIsQrScanned() {
    const res = await fetch("http://localhost:5000/is_qr", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({}),
    });
    console.log(res);
    if (res.ok) {
      const response = await res.json();
      itemId = response.id;

      // Get the inventory item data from the database
      get_inventory_item();
      // Toggle the camera visibilty and show the item card instead
      showCameraStream = false;

      console.log(itemId);
    }
  }

  async function get_inventory_item() {
    const res = await fetch("http://localhost:5000/get_item", {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ itemId }),
    });
    if (!res.ok) {
      error_msg = "Adding Item Failed";
    } else {
      error_msg = "";
      item = await res.json();
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
      check_out_poc: "You", // Or extract from response
      check_out_date: new Date().toLocaleDateString(), // Update as needed
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

<p>showCameraStream: {showCameraStream}</p>
<p>itemId: {itemId}</p>

{#if showCameraStream}
  <label for="id" class="label"
    >Place QR code in front of the scanner camera!
  </label>
  <img src={streamUrl} alt="Camera Stream" class="border rounded" />
{:else}
  <!-- Overlay for expanded card -->
  <div class="product-card expanded centered" on:click|stopPropagation>
    <img
      src={`${media_url}${item.image}.png`}
      alt={item.image}
      className="product-image"
    />
    <div class="product-name">{item.name}</div>
    <div class="manufacturer">by {item.manufacturer}</div>
    <!-- This will show the number of items of this category -->
    <div class="manufacturer">Count: N/A</div>

    {#if item.is_checked_out}
      <div class="status-out">
        Checked out by {item.check_out_poc} since {item.check_out_date}
      </div>
    {:else}
      <div class="status-available">Available</div>
    {/if}

    <div class="extra-details">
      {#if item.is_checked_out}
        <button
          class="return-button"
          on:click={() => returnItem(itemId)}
        >
          <Undo2 size={20} /> return
        </button>
      {:else}
        <button
          class="borrow-button"
          on:click={() => checkoutItem(itemId)}
        >
          <HandHelping size={20} /> borrow
        </button>
      {/if}
      {#if error}
        <p class="error-message">{error}</p>
      {/if}
      <div class="manufacturer">Manufacturer details: {item.details}</div>
      <button class="close-button" on:click={() => (showCameraStream = 1)}
        ><CircleX size={20} /> close</button
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

  .product-image {
    max-height: 200px;
    object-fit: contain;
    margin-bottom: 1rem;
    border-bottom: 1px solid #d37e1d;
    padding-bottom: 1rem;
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
</style>
