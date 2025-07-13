<script>
  import { page } from "$app/state";
  // Load item data loaded in +page.ts
  export let data;
  let { user, items } = data;
  let searchQuery = "";
  
  // Redirect if user is null (in case of hot navigation after logout)
  import { goto } from '$app/navigation';
  if (!user) {
    goto('/login');
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

  .product-card:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    background-color: rgb(82, 81, 81);
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
</style>

<!-- Headline  -->
<h1 class="headline">Inventory</h1>

<!-- Search bar  -->
<input
  class="search-box"
  placeholder="Search items..."
  bind:value={searchQuery}
/>

<div class="product-grid">
  {#each filteredItems as item}
    <div class="product-card">
     <img src={item.item_image} alt={item.item_name} class="product-image" />
      <div class="product-name">{item.item_name}</div>
      <div class="manufacturer">by {item.manufacturer}</div>
      <div class="manufacturer">{item.manufacturer_contact}</div>
      {#if item.is_checked_out}
      <div class="status-out">
        Checked out by {item.check_out_poc} since {item.check_out_date}
      </div>
      {:else}
      <div class="status-available">
        Available
      </div>
      {/if}
  </div>
  {/each}
</div>
