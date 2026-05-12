import { printQR } from "$lib/niimbot";

export const media_url = "/api/media/";

// --- Image Utilities ---

export async function uploadImage(formData: FormData): Promise<{ error: string; image: string }> {
  try {
    const response = await fetch(`/api/image_upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      return { error: "Image upload failed. Server returned an error.", image: "" };
    }

    const data = await response.json();
    return { error: "", image: data.image };

  } catch (err) {
    console.error("Upload error:", err);
    return { error: "Network error during image upload.", image: "" };
  }
}

export async function captureImage(videoEl: HTMLVideoElement): Promise<{ error: string; image: string }> {
  if (!videoEl) {
    return { error: "Video element not ready.", image: "" };
  }

  try {
    const canvas = document.createElement("canvas");
    canvas.width = videoEl.videoWidth;
    canvas.height = videoEl.videoHeight;

    const ctx = canvas.getContext("2d");
    if (!ctx) throw new Error("Failed to get canvas context");

    ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height);

    const blob = await new Promise<Blob>((resolve, reject) =>
      canvas.toBlob(
        b => b ? resolve(b) : reject(new Error("toBlob returned null")),
        "image/png"
      )
    );

    const formData = new FormData();
    formData.append("avatar", blob, "capture.png");

    return await uploadImage(formData);

  } catch (err) {
    console.error("Capture error:", err);
    return { error: "Failed to capture image.", image: "" };
  }
}

export interface InventoryItem {
  id: number;
  name?: string | '';
  image?: string | '';
  description?: string | '';
  manufacturer?: string | '';
  details?: string | '';
  is_checked_out?: boolean | null;
  check_out_date?: string | '';
  check_out_poc?: string | '';
  date_added?: string | '';
  tags?: string | '';
  location?: number | 0;
  item_type?: string | '';
  manufacturer_link?: string | '';
  project?: string | '';
  manufacturer_location?: string | '';
  color?: string | '';
  material?: string | '';
  product_use?: string | '';
  number_items?: number | 0;
}

export function createInventoryStore() {
  // --- State ---
  let items = $state<InventoryItem[]>([]);
  let user = $state(null);
  let user_privilege = $state(0);
  let searchTerm = $state("");
  let loading = $state(false);
  let error_msg = $state("");
  let image_updated = $state(false);
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
      // 1. Get User info + privileges in one call — /api/me returns { id, username, user_privileges }
      const userRes = await fetch(`/api/me`, { credentials: "include" });
      if (!userRes.ok) throw new Error("Failed to fetch user");
      const userData = await userRes.json();
      user = userData;
      user_privilege = userData.user_privileges; 

      // 2. Get Items
      const itemsRes = await fetch(`/api/items`, { credentials: "include" });
      if (!itemsRes.ok) throw new Error("Failed to fetch items");
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
          check_out_poc: '',
          check_out_date: '',
        };
      }
    }
  }

  async function updateItem(id: number, updatedData: any): Promise<String> {
    let save_error = "";

    // 1. Validation
    if (!updatedData.name) {
      save_error = "No item name set. Define item name before updating.";
      return save_error;
    }
    else
    {
      // 2. Handle Image Logic
      // If the image was updated in the UI, use the new store-level 'currentImage'
      // Otherwise, stick with what was already on the item
      const finalImage = image_updated ? currentImage : updatedData.image;
  
      try {
        const res = await fetch(`/api/update_item`, {
          method: "POST",
          credentials: "include",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            id,
            ...updatedData,
            image: finalImage,
          }),
        });
  
        if (!res.ok) {
          save_error = "Saving item updates failed";
        } else {
          // 3. Update Local State (Optimistic UI)
          // Find the item in our reactive array and update it so the UI refreshes instantly
          const index = items.findIndex((i) => i.id === id);
          if (index !== -1) {
            items[index] = { ...items[index], ...updatedData, image: finalImage };
          }
          
          // 4. Reset flags
          error_msg = "";
          image_updated = false;
        }
      } catch (err) {
        save_error = "Network error while updating item.";
      }
    }
    return save_error;
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
          location: null,
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
          await printItemQrLabel(newId);
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

  async function printItemQrLabel(id: number): Promise<String> {
    let printError = "";
    const qrPayload = `iitem;id;${id}`;
    try {
      await printQR(String(qrPayload));
    } catch (err) {
      console.error("Printer error:", err);
      printError = "Failed to print QR label!";
    }
    return printError
  }

  // --- Return object ---
  return {
    // State Getters
    get items() { return items },
    get filteredItems() { return filteredItems },
    get searchTerm() { return searchTerm },
    get loading() { return loading },
    get user_privilege() { return user_privilege },
    get image_updated() { return image_updated },
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
    addItem,
    printItemQrLabel,
    captureImage
  };
}