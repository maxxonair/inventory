<script>
  import { page } from "$app/state";
  import { CircleX, HandHelping , Undo2} from 'lucide-svelte';
  // Load item data loaded in +page.ts
  export let data;
  let { user, items } = data;
  let searchQuery = "";
  let error = "";
  
  let selectedItemId = null;

  function toggleItem(itemId) {
    selectedItemId = selectedItemId === itemId ? null : itemId;
  }

  async function checkoutItem(itemId){
    const res = await fetch("http://localhost:5000/checkout_item", {
      method: "POST",
      credentials: "include",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ itemId }),
    });

    if (!res.ok) {
      error = "Item checkout failed";
    }

    // Update item in the list
    const index = items.findIndex((i) => i.id === itemId);
    if (index !== -1) {
      items[index] = {
        ...items[index],
        is_checked_out: true,
        check_out_poc: 'You', // Or extract from response
        check_out_date: new Date().toLocaleDateString(), // Update as needed
      };
    }
  }

  async function returnItem(itemId){
    const res = await fetch("http://localhost:5000/return_item", {
      method: "POST",
      credentials: "include",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ itemId }),
    });

    if (!res.ok) {
      error = "Item return failed";
    }

    // Update item in the list
    const index = items.findIndex((i) => i.id === itemId);
    if (index !== -1) {
      items[index] = {
        ...items[index],
        is_checked_out: false,
        check_out_poc: null,
        check_out_date: null,
      };
    }
  }

  // Filter items based on search query
  $: filteredItems = items.filter(item =>
    Object.values(item).some(value =>
      String(value).toLowerCase().includes(searchQuery.toLowerCase())
    )
  );
</script>

<style>
  .headline {
    font-size: 3rem;
    font-weight: bold;
    color: #c85203
  }

  .search-box {
    display: block;         /* Ensure it's treated as a block */
    margin: 0 auto 1rem;    /* Center horizontally, keep bottom margin */
    padding: 0.5rem;
    width: 100%;
    max-width: 400px;
    font-size: 1rem;
    border: 1px solid #ccc;
    border-radius: 8px;
  }

  .product-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
  }

  .product-card {
    border: 1px solid #ccc;
    border-radius: 10px;
    padding: 1rem;
    display: flex;
    flex-direction: column;
    background-color: rgb(35, 35, 35);
    transition: box-shadow 0.2s;
  }

  .product-card.faded {
    opacity: 0.3;
    pointer-events: none;
    transform: scale(0.98);
  }

  .product-card.expanded {
    grid-column: 1 / -1;
    transform: scale(1.02);
    z-index: 10;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  }

  .product-card:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    background-color: rgb(82, 81, 81);
  }

  .extra-details {
  margin-top: 1rem;
  border-top: 1px solid #eee;
  padding-top: 1rem;
  }
  
  /* Overlay that dims background */
  .overlay {
    position: fixed;
    inset: 0;
    background-color: rgba(0, 0, 0, 0.5);
    z-index: 100;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 1rem;
  }

  /* Centered product card */
  .product-card.centered {
    max-width: 600px;
    width: 100%;
    max-height: 90vh;
    overflow-y: auto;
    background: rgb(114, 113, 113)2, 81, 81);
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25);
    transition: transform 0.3s ease;
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
    color: #fa8d1f
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

  .borrow-button{
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

  .return-button{
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

  .close-button{
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
</style>

<!-- Headline  -->
<h1 class="headline">Inventory</h1>

<!-- Search bar  -->
<input
  class="search-box"
  placeholder="Search items..."
  bind:value={searchQuery}
/>

<svelte:body class:lock-scroll={selectedItemId !== null} />

<div class="product-grid">
  {#each filteredItems as item}
    {#if selectedItemId === item.id}
      <!-- Overlay for expanded card -->
      <div class="overlay" on:click={() => (selectedItemId = null)}>
        <div
          class="product-card expanded centered"
          on:click|stopPropagation
        >
          <img src={item.item_image} alt={item.item_name} class="product-image" />
          <div class="product-name">{item.item_name}</div>
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
            <button class="return-button" on:click={() => returnItem(selectedItemId)}>
              <Undo2 size={20} /> return
            </button>
            {:else}
              <button class="borrow-button" on:click={() => checkoutItem(selectedItemId)}>
                <HandHelping size={20} /> borrow
              </button>
            {/if}
            {#if error}
              <p class="error-message">{error}</p>
            {/if}
            <div class="manufacturer">Manufacturer details: {item.manufacturer_contact}</div>
            <button class="close-button" on:click={() => (selectedItemId = null)}><CircleX size={20} /> close</button>
          </div>
        </div>
      </div>
    {:else if !selectedItemId}
      <!-- Normal card display -->
      <div class="product-card" on:click={() => toggleItem(item.id)}>
        <img src={item.item_image} alt={item.item_name} class="product-image" />
        <div class="product-name">{item.item_name}</div>
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
      </div>
    {/if}
  {/each}
</div>
