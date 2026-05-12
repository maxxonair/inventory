import { printQR } from "$lib/niimbot";

export interface StorageLocation {
  id: number;
  name: string;
  description: string;
  date_added: string;
  tags: string;
}

export function createStorageLocationStore() {
  // --- State ---
  let storage_locations = $state<StorageLocation[]>([]);
  let user = $state(null);
  let user_privilege = $state(0);
  let searchTerm = $state("");
  let loading = $state(false);
  let error_msg = $state("");


  // --- Derived ---
  const filteredStorageLocations = $derived(
    storage_locations.filter((locations: StorageLocation) =>
      Object.values(locations).some((v) => 
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

      // 3. Get storage_locations
      const locationsRes = await fetch(`/api/storage_locations`, { credentials: "include" });
      storage_locations = await locationsRes.json();
    } catch (err) {
      console.error("Failed to fetch storage location data:", err);
      error_msg = "Critical error loading data.";
    } finally {
      loading = false;
    }
  }

  async function deleteStorageLocation(id: number) {
    storage_locations = storage_locations.filter(loc => loc.id !== id);
  }

  async function updateStorageLocation(id: number, updatedData: any) {
    // 1. Validation
    if (!updatedData.name) {
      error_msg = "No storage location name set. Define storage location name before updating.";
      return;
    }


    try {
      const res = await fetch(`/api/update_storage`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          id,
          ...updatedData,
        }),
      });

      if (!res.ok) {
        error_msg = "Updating Storage Location Failed";
      } else {
        // 3. Update Local State (Optimistic UI)
        // Find the item in our reactive array and update it so the UI refreshes instantly
        const index = storage_locations.findIndex((i) => i.id === id);
        if (index !== -1) {
          storage_locations[index] = { ...storage_locations[index], ...updatedData };
        }
        
        // 4. Reset flags
        error_msg = "";
      }
    } catch (err) {
      error_msg = "Network error while updating storage location.";
    }
  }

  async function addStorageLocation(newStorageLocation: StorageLocation) {
    // 1. Validation check
    if (!newStorageLocation.name) {
      error_msg = "No storage location name set. Define storage location name before adding.";
      return;
    }

    loading = true;
    try {
      const date_added = new Date().toISOString();
      
      const res = await fetch(`/api/add_storage`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...newStorageLocation,
        }),
      });

      if (!res.ok) {
        error_msg = "Adding Storage Location Failed";
      } else {
        error_msg = "";
        const data = await res.json();
        const newId = data.message;

        // Update Local State (Avoids window.location.reload)
        // The new item is pushed to our state array so it appears instantly
        const itemToAppend = { 
          ...newStorageLocation, 
          id: newId, 
        };
        
        storage_locations = [...storage_locations, itemToAppend];

        // 4. Return success to let the component know it can close the drawer
        return true; 
      }
    } catch (err) {
      error_msg = "Network error while adding storage location.";
    } finally {
      loading = false;
    }
    return false;
  }

  // --- Return object ---
  return {
    // State Getters
    get storage_locations() { return storage_locations },
    get filteredstorage_locations() { return filteredStorageLocations },
    get searchTerm() { return searchTerm },
    get loading() { return loading },
    get user_privilege() { return user_privilege },
    get error_msg() { return error_msg },

    // State Setters
    set searchTerm(val) { searchTerm = val },
    set error_msg(val) { error_msg = val },

    // Actions
    fetchData,
    deleteStorageLocation,
    updateStorageLocation,
    addStorageLocation
  };
}