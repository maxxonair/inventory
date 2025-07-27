<script>
  import { page } from "$app/state";
  import IconButton from '@smui/icon-button';
  import { CircleX, HandHelping , Undo2, CircleChevronLeft, CircleChevronRight, Printer , Trash2, SquarePen} from 'lucide-svelte';
  // Load item data loaded in +page.ts
  export let data;
  let { user, items } = data;
  
  let searchQuery = "";
  let error = "";
  let showConfirm = false;
  let selectedItemId = null;
  let currentPage = 1;
  // Number of items to display per page. Store as string to support option "All"
  let selectedItemsPerPage = "50"; 

  function requestDelete() {
    showConfirm = true;
  }

  function confirmDelete() {
    deleteItem(selectedItemId);
    showConfirm = false;
    selectedItemId = null;
  }

  function cancelDelete() {
    showConfirm = false;
  }

  function toggleItem(itemId) {
    selectedItemId = selectedItemId === itemId ? null : itemId;
  }

  $: itemsPerPage = selectedItemsPerPage === "All" ? filteredItems.length : parseInt(selectedItemsPerPage);

  $: totalPages = Math.ceil(filteredItems.length / itemsPerPage);
  $: paginatedItems = filteredItems.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  function goToPage(page) {
    if (page >= 1 && page <= totalPages) {
      currentPage = page;
    }
  }

  function handleItemsPerPageChange(event) {
    selectedItemsPerPage = event.target.value;
    currentPage = 1; // reset to first page
  }

  async function updateItem(itemId, item){
    // Function TODO 
  }

  async function printLabel(itemId){
    const res = await fetch("http://localhost:5000/print_label", {
      method: "POST",
      credentials: "include",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ itemId }),
    });

    if (!res.ok) {
      error = "Printing Label failed";
    }
  }

  async function deleteItem(itemId){
    const res = await fetch("http://localhost:5000/delete_item", {
      method: "POST",
      credentials: "include",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ itemId }),
    });

    if (!res.ok) {
      error = "Deleting Item failed";
    }
    else
    { 
      // Remove this item from the item list 
      const index = items.findIndex((i) => i.id === itemId);
      if (index !== -1) {
        items.splice(index, 1);
      }
    }
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

<svelte:head>
  <title>Inventory</title>
  <meta name="description" content="Page to add new item" />
</svelte:head>

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
  {#each paginatedItems as item}
    {#if selectedItemId === item.id}
      <!-- Overlay for expanded card -->
      <div class="overlay" on:click={() => (selectedItemId = null)}>
        <div
          class="product-card expanded centered"
          on:click|stopPropagation
        >
          <img src={`${media_url}${item.image}.png`} alt={item.image} className="product-image" />
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
                  <button class="confirm-button" on:click={confirmDelete}>Yes, Delete</button>
                  <button class="cancel-button" on:click={cancelDelete}>Cancel</button>
                </div>
              </div>
            {:else}
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
              <button class="generic-button" on:click={() => printLabel(selectedItemId)}> 
                <Printer size={20} /> 
                <span>print label</span>
              </button>
              <button class="generic-button" on:click={() => requestDelete()}> 
                <Trash2 size={20} /> 
                <span>delete</span>
              </button>
              <button class="generic-button" on:click={() => updateItem(selectedItemId, item)}> 
                <SquarePen size={20} /> 
                <span>update data</span>
              </button>
            {/if}
          </div>
          <div class="extra-details">
            <button class="close-button" on:click={() => (selectedItemId = null)}><CircleX size={20} /> close</button>
          </div>
        </div>
      </div>
    {:else if !selectedItemId}
      <!-- Normal card display -->
      <div class="product-card" on:click={() => toggleItem(item.id)}>
        <img src={`${media_url}${item.image}.png`} alt={item.name} class="product-image" />
        <div class="product-name">{item.name}</div>
        <div class="manufacturer">by {item.manufacturer}</div>
        <div class="manufacturer">Type: {item.number_items}</div>
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

<footer class="footer">

  <div class="pagination">
    <button class="generic-button" on:click={() => goToPage(currentPage - 1)} disabled={currentPage === 1}>
      <CircleChevronLeft size={20} />
    </button>

    {#each Array(totalPages) as _, index}
      <button
      class="generic-button"
        class:active-page={currentPage === index + 1}
        on:click={() => goToPage(index + 1)}
      >
        {index + 1}
      </button>
    {/each}

    <button class="generic-button" on:click={() => goToPage(currentPage + 1)} disabled={currentPage === totalPages}>
      <CircleChevronRight size={20} />
    </button>

    <div class="pagination-controls">
    <label class="label" for="itemsPerPage">Items per page:</label>
    <select class="generic-dropdown" 
            id="itemsPerPage" 
            on:change={handleItemsPerPageChange} 
            bind:value={selectedItemsPerPage}>
      <option value="5">5</option>
      <option value="10">10</option>
      <option value="50">50</option>
      <option value="All">All</option>
    </select>
  </div>
  </div>
</footer>

<style>

  .pagination {
    margin-top: 1rem;
    display: flex;
    justify-content: center;
    gap: 0.5rem;
  }

  .pagination button {
    padding: 0.4rem 0.7rem;
  }

  .active-page {
    font-weight: bold;
    background-color: #ddd;
  }

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

  .label{
    justify-content: center;
    text-align: center;
    color: #fa8d1f;
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

  .button-row {
    display: flex;
    gap: 1rem; 
    justify-content: center;
    flex-wrap: wrap;
  }

  .generic-button{
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

  .generic-button span {
    margin-top: 4px;
    font-size: 0.85rem;
  }

  .generic-dropdown{
    background-color: #252525;
    color: #fa8d1f;
    border: none;
    border-radius: 9999px;
    padding: 0.5rem;
    margin: 0 auto 1rem; 
    cursor: pointer;
    transition: background-color 0.2s ease;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
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

  .confirm-card {
    background: rgb(241, 167, 167);
    border: 1px solid #af0000;
    padding: 1rem;
    border-radius: 0.5rem;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    margin-top: 0.5rem;
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
    background-color: rgb(63, 63, 63)c13;
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


