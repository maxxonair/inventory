<script>
  import { onMount } from "svelte";
  let users = [];
  let newUser = "";
  let items = [];
  let searchQuery = "";

  // Fetch users on load
  async function loadUsers() {
    const res = await fetch("http://127.0.0.1:5000/users");
    users = await res.json();
  }

  // Add a new user
  async function addUser() {
    if (!newUser.trim()) return;
    await fetch("http://127.0.0.1:5000/users", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name: newUser }),
    });
    newUser = "";
    await loadUsers();
  }

  // onMount(loadUsers);

  async function loadItems() {
    const res = await fetch("http://127.0.0.1:5000/items");
    items = await res.json();
  }

  onMount(loadItems);

  // Filter items based on search query
  $: filteredItems = items.filter(item =>
    Object.values(item).some(value =>
      String(value).toLowerCase().includes(searchQuery.toLowerCase())
    )
  );
</script>

<style>
  .search-box {
    margin-bottom: 1rem;
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
    background-color: white;
    transition: box-shadow 0.2s;
  }

  .product-card:hover {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .product-image {
    max-height: 200px;
    object-fit: contain;
    margin-bottom: 1rem;
    border-bottom: 1px solid #eee;
    padding-bottom: 1rem;
  }

  .product-name {
    font-weight: bold;
    font-size: 1.1rem;
    margin-bottom: 0.5rem;
  }

  .manufacturer {
    color: #555;
    margin-bottom: 0.5rem;
  }

  .status {
    margin-top: auto;
    font-weight: 500;
    color: green;
  }

  .status.out {
    color: red;
  }
</style>

<h1 class="text-2xl font-semibold mb-6">Search Results</h1>

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
      <div class:status class:out={item.is_checked_out !== '1'}>
        {item.is_checked_out}
      </div>
    </div>
  {/each}
</div>