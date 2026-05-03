import { printQR } from "$lib/niimbot";

export interface InventoryItem {
  id: number;
  name: string;
  image: string;
  details: string;
  manufacturer: string;
  item_type: string;
  is_checked_out: boolean;
  check_out_poc?: string | null;
  check_out_date?: string | null;
  tags?: string | null;
  location: number;
  manufacturer_link?: string | null;
  color?: string | null;
  material?: string | null;
  product_use?: string | null;
  number_of_items?: number | null;
}

export function createInventoryStore() {
  // --- State ---
  let items = $state<InventoryItem[]>([]);
  let user = $state(null);
  let user_privilege = $state(0);
  let searchTerm = $state("");
  let loading = $state(false);
  let error_msg = $state("");
  let imageUpdated = $state(false);
  let currentImage = $state("");


  // --- Derived ---
  const filteredItems = $derived(
    items.filter((item: InventoryItem) =>
      Object.values(item).some((v) => 
        String(v).toLowerCase().includes(searchTerm.toLowerCase())
      )
    )
  );

  // --- API Methods ---

  async function fetchData() {
    loading = true;
    try {
      // 1. Get User info
      const userRes = await fetch(`/api/me`, { credentials: "include" });
      const userData = await userRes.json();
      user = userData.user;

      // 2. Get Privileges
      const privRes = await fetch(`/api/user_privilege`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user }),
      });
      const privData = await privRes.json();
      user_privilege = privData.privilege;

      // 3. Get Items
      const itemsRes = await fetch(`/api/items`, { credentials: "include" });
      items = await itemsRes.json();
    } catch (err) {
      console.error("Failed to fetch inventory data:", err);
      error_msg = "Critical error loading data.";
    } finally {
      loading = false;
    }
  }

  async function deleteItem(itemId: number) {
    const res = await fetch(`/api/delete_item`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ itemId }),
    });

    if (res.ok) {
      items = items.filter((i) => i.id !== itemId);
    } else {
      error_msg = "Deleting Item failed";
    }
  }

  async function checkoutItem(itemId: number) {
    const res = await fetch(`/api/checkout_item`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ itemId }),
    });

    if (res.ok) {
      const index = items.findIndex((i) => i.id === itemId);
      if (index !== -1) {
        items[index] = {
          ...items[index],
          is_checked_out: true,
          check_out_poc: "you",
          check_out_date: new Date().toLocaleDateString(),
        };
      }
    }
  }

  async function returnItem(itemId: number) {
    const res = await fetch(`/api/return_item`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ itemId }),
    });

    if (res.ok) {
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
  }

  async function updateItem(id: number, updatedData: any) {
    // 1. Validation
    if (!updatedData.name) {
      error_msg = "No item name set. Define item name before updating.";
      return;
    }

    // 2. Handle Image Logic
    // If the image was updated in the UI, use the new store-level 'currentImage'
    // Otherwise, stick with what was already on the item
    const finalImage = imageUpdated ? currentImage : updatedData.image;

    try {
      const res = await fetch(`/api/update_item`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id,
          ...updatedData,
          image: finalImage,
          date_updated: new Date().toISOString()
        }),
      });

      if (!res.ok) {
        error_msg = "Updating Item Failed";
      } else {
        // 3. Update Local State (Optimistic UI)
        // Find the item in our reactive array and update it so the UI refreshes instantly
        const index = items.findIndex((i) => i.id === id);
        if (index !== -1) {
          items[index] = { ...items[index], ...updatedData, image: finalImage };
        }
        
        // 4. Reset flags
        error_msg = "";
        imageUpdated = false;
      }
    } catch (err) {
      error_msg = "Network error while updating item.";
    }
  }

  async function addItem(newItemData: any) {
    // 1. Validation check
    if (!newItemData.name) {
      error_msg = "No item name set. Define item name before adding.";
      return;
    }

    loading = true;
    try {
      const date_added = new Date().toISOString();
      
      const res = await fetch(`/api/add_item`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...newItemData,
          date_added,
          // Ensure defaults if not provided by the form
          is_checked_out: false,
          check_out_poc: null,
          check_out_date: null
        }),
      });

      if (!res.ok) {
        error_msg = "Adding Item Failed";
      } else {
        error_msg = "";
        const data = await res.json();
        const newId = data.message; // Assuming the API returns the new ID here

        // 2. Handle QR Printing
        try {
          // You can import your existing handleAddItemPrintQr logic here
          await handlePrintQr(newId);
        } catch (err) {
          console.error('Failed to print QR for new item:', err);
        }

        // 3. Update Local State (Avoids window.location.reload)
        // We push the new item to our state array so it appears instantly
        const itemToAppend = { 
          id: newId, 
          ...newItemData, 
          date_added, 
          is_checked_out: false 
        };
        
        items = [...items, itemToAppend];

        // 4. Return success to let the component know it can close the drawer
        return true; 
      }
    } catch (err) {
      error_msg = "Network error while adding item.";
    } finally {
      loading = false;
    }
    return false;
  }

  async function handlePrintQr(item_id: number) {
    try {
      await printQR(String(item_id));
    } catch (err) {
      console.error("Printer error:", err);
      throw err;
    }
  }

  // --- Return object ---
  return {
    // State Getters
    get items() { return items },
    get filteredItems() { return filteredItems },
    get searchTerm() { return searchTerm },
    get loading() { return loading },
    get user_privilege() { return user_privilege },
    get error_msg() { return error_msg },

    // State Setters
    set searchTerm(val) { searchTerm = val },
    set error_msg(val) { error_msg = val },

    // Actions
    fetchData,
    deleteItem,
    checkoutItem,
    returnItem,
    updateItem,
    addItem
  };
}