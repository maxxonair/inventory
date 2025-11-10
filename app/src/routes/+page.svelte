<script lang="ts">
	// import { createReadStream } from 'node:fs';
  // @ts-nocheck

  import { page } from "$app/state";
  import { onMount, onDestroy } from "svelte";
  import * as XLSX from "xlsx";
  import {
    CircleX,
    HandHelping,
    Undo2,
    CircleChevronLeft,
    CircleChevronRight,
    Printer,
    Trash2,
    SquarePen,
  } from "lucide-svelte";
  import {
    TableBody,
    P,
    TableBodyCell,
    TableBodyRow,
    TableHead,
    TableHeadCell,
  } from "flowbite-svelte";
  import {
    TableSearch,
    Dropdown,
    DropdownItem,
    Checkbox,
    ButtonGroup,
    List,
    Li,
    FloatingLabelInput,
  } from "flowbite-svelte";
  import { Drawer, Button, GradientButton } from "flowbite-svelte";
  import { CloseButton, Label, Input, Textarea, Select } from "flowbite-svelte";
  import {
    CloseOutline,
    ExclamationCircleOutline,
    CheckCircleOutline,
    PrinterOutline,
  } from "flowbite-svelte-icons";
  import {
    PenOutline,
    ChevronDownOutline,
    FilterSolid,
    ChevronRightOutline,
  } from "flowbite-svelte-icons";
  import {
    ChevronLeftOutline,
    QrCodeOutline,
    FolderArrowRightOutline,
  } from "flowbite-svelte-icons";
  import { Section } from "flowbite-svelte-blocks";
  import {
    CartPlusAltOutline,
    MinusOutline,
    PlusOutline,
  } from "flowbite-svelte-icons";
  import jsQR from "jsqr";

  let { user } = $props();

  /* ------------------  Main Table function ----------------------- */

  // Define user privilege level
  const PRIVILEGE_GUEST = 0;
  const PRIVILEGE_REPORTER = 1;
  const PRIVILEGE_DEVELOPPER = 2;
  const PRIVILEGE_MAINTAINER = 3;
  const PRIVILEGE_OWNER = 4;

  let user_privilege = $state(null);

  let divClass =
    "bg-white dark:bg-gray-800 relative shadow-md sm:rounded-lg overflow-hidden";
  let innerDivClass =
    "flex flex-col md:flex-row items-center justify-between space-y-3 md:space-y-0 md:space-x-4 p-4";
  let searchClass = "w-full md:w-1/2 relative";

  let searchTerm = $state("");
  let currentPosition = $state(0);
  const itemsPerPage = 50;
  const showPage = 5;
  let totalPages = $state(0);
  let pagesToShow = $state([]);
  let totalItems = $state(0);
  let startPage;
  let endPage = $state(10);

  let items = $state([]);
  let loading = $state(true);

  let cameraServerUrl = $state("");

  // Fetch data from backend
  const fetchData = async () => {
    // Get user
    try {
      const res = await fetch(`/api/me`, { credentials: "include" });
      const data = await res.json();
      user = data.user;
    } catch (err) {
      console.error("Failed to get user:", err);
    }

    // Get user privilege level
    try {
      const res = await fetch(`/api/user_privilege`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user }),
      });

      const data = await res.json();
      user_privilege = data.privilege;
    } catch (err) {
      console.error("Failed to load user privilege level:", err);
    }

    // Load all inventory items
    loading = true;
    try {
      const res = await fetch(`/api/items`, {
        credentials: "include",
      });
      const data = await res.json();
      items = data;
      totalItems = items.length;
      renderPagination(items.length);
    } catch (err) {
      console.error("Failed to fetch items:", err);
    } finally {
      loading = false;
    }
  };

  let filteredItems = $derived(
    items.filter((item) =>
      Object.values(item).some((value) =>
        String(value).toLowerCase().includes(searchTerm.toLowerCase())
      )
    )
  );

  const updateDataAndPagination = () => {
    let currentPageItems = filteredItems.slice(
      currentPosition,
      currentPosition + itemsPerPage
    );
    renderPagination(currentPageItems.length);
  };

  const loadNextPage = () => {
    if (currentPosition + itemsPerPage < filteredItems.length) {
      currentPosition += itemsPerPage;
      updateDataAndPagination();
    }
  };

  const loadPreviousPage = () => {
    if (currentPosition - itemsPerPage >= 0) {
      currentPosition -= itemsPerPage;
      updateDataAndPagination();
    }
  };

  const renderPagination = (totalItems) => {
    totalPages = Math.ceil(filteredItems.length / itemsPerPage);
    const currentPage = Math.ceil((currentPosition + 1) / itemsPerPage);

    startPage = currentPage - Math.floor(showPage / 2);
    startPage = Math.max(1, startPage);
    endPage = Math.min(startPage + showPage - 1, totalPages);

    pagesToShow = Array.from(
      { length: endPage - startPage + 1 },
      (_, i) => startPage + i
    );
  };

  const goToPage = (pageNumber) => {
    currentPosition = (pageNumber - 1) * itemsPerPage;
    updateDataAndPagination();
  };

  let startRange = $derived(currentPosition + 1);
  let endRange = $derived(Math.min(currentPosition + itemsPerPage, totalItems));

  let currentPageItems = $derived(
    filteredItems.slice(currentPosition, currentPosition + itemsPerPage)
  );

  $effect(() => {
    // Fetch inventory data on mount
    fetchData();
  });

  /* ------------------  Add Item Side panel function ----------------------- */

  let showLeftDrawer = $state(false);
  let showAddItemPanel = $state(false);
  let showScannerPanel = $state(false);
  let showErrorAlert = $state(false);
  let imageUpdated = $state(false);

  let selected = $state();
  let categories = [
    { value: "", name: "Select Type" },
    { value: "Fabric", name: "Fabric" },
    { value: "Flooring", name: "Flooring" },
    { value: "Furniture", name: "Furniture" },
    { value: "Curtains", name: "Curtains" },
    { value: "Tiles", name: "Tiles" },
  ];

  const toggleAddItemPanel = () => {
    showLeftDrawer = !showLeftDrawer;
    showAddItemPanel = true;
    showScannerPanel = false;
  };

  const toggleScannerPanel = () => {
    showLeftDrawer = !showLeftDrawer;
    showAddItemPanel = false;
    showScannerPanel = true;

    if (showScannerPanel) {
      startQrCamera();
    } else {
      stopQrScanner();
    }

    console.log("Camera address:", cameraServerUrl);
  };

  let name = $state("");
  let manufacturer = $state("");
  let details = $state("");
  let number_items = $state(1);
  let image = $state("");
  let tags = $state("");

  let err = "";

  const media_url = `/api/media/`;

  let imageUrl = $state("/api/media/");

  let description = $state("");
  let item_type = $state("");
  let location = $state("");
  let check_out_poc = $state("");
  let check_out_date = $state("");
  let is_checked_out = 0;

  let manufacturer_link = $state("");
  let manufacturer_location = $state("");
  let project = $state("");
  let color = $state("");
  let material = $state("");
  let product_use = $state("");
  

  let selectedFile = $state(null);
  
  // Variables for dynamic client side video stream
  let videoEl = $state(null);
  let stream = null;
  let stream_error = $state(null);
  let canvasEl = $state(null);
  let scanning = $state(false);
  let scanAnimationFrame = $state(null);

  function onDrop(event) {
    event.preventDefault();
    handleDragAndDropFileUpload(event);
  }

  function onDragOver(event) {
    event.preventDefault();
  }

  async function handleDragAndDropFileUpload(Event) {
    const files = event.target.files || event.dataTransfer.files;

    if (files && files.length > 0) {
      selectedFile = files[0];

      const formData = new FormData();
      formData.append("avatar", selectedFile);

      try {
        const response = await fetch(`/api/image_upload`, {
          method: "POST",
          body: formData,
        });

        if (response.ok) {
          const result = await response.json();
          image = result.image;
          imageUrl = `/api/media/${image}.png`;
          showStaticImg = true;
          console.log("Upload successful:", result);
        } else {
          console.error("Upload failed:", await response.text());
        }
      } catch (error) {
        console.error("Error uploading file:", error);
      }
    }
  }

  async function handleFileUpload(Event) {
    const input = event.target;
    if (input.files && input.files.length > 0) {
      selectedFile = input.files[0];

      const formData = new FormData();
      formData.append("avatar", selectedFile);

      try {
        const response = await fetch(`/api/image_upload`, {
          method: "POST",
          body: formData,
        });

        if (response.ok) {
          const result = await response.json();
          image = result.image;
          imageUrl = `${media_url}/${image}.png`;
          showStaticImg = true;
          console.log("Upload successful:", result);
        } else {
          console.error("Upload failed:", await response.text());
        }
      } catch (error) {
        console.error("Error uploading file:", error);
      }
    }
  }

  /* ------------------  Additional functions ----------------------- */
  let error_msg = $state("");
  let camera_error = $state("");
  let showConfirm = $state(false);
  let selectedItemId = $state(null);
  let enableEdit = $state(false);
  let showCameraStream = $state(false);
  let showStaticImg = $state(false);

  // Define possible options to filter the item type
  const item_type_filter_options = ["Flooring", "Curtain"];
  let selectedTypes = $state([]);

  function toggleType(type) {
    if (selectedTypes.includes(type)) {
      selectedTypes = selectedTypes.filter((t) => t !== type);
    } else {
      selectedTypes = [...selectedTypes, type];
    }
  }

  function toggleEdit() {
    imageUrl = "";
    if (!enableEdit) {
      imageUpdated = false;
    }
    enableEdit = !enableEdit;
    showCameraStream = false;
  }

  const closeErrorAlertAlert = () => {
    alert("Clicked closeAlert.");
    showErrorAlert = !showErrorAlert;
  };

  function showErrorAlertFnct() {
    showErrorAlert = true;
    //  Auto-dismiss Alerts after 10 seconds
    setTimeout(() => {
      showErrorAlert = false;
    }, 120000);
  }

  async function addItem() {
    if (!name) {
      error_msg = "No item name set. Define item name before adding.";
      showErrorAlertFnct();
    } else {
      let date_now = new Date();
      let date_added = date_now.toISOString();
      const res = await fetch(`/api/add_item`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name,
          manufacturer,
          details,
          item_type,
          number_items,
          image,
          description,
          location,
          date_added,
          check_out_poc,
          check_out_date,
          is_checked_out,
          tags,
          manufacturer_link,
          manufacturer_location,
          project,
          color,
          material,
          product_use,
        }),
      });

      if (!res.ok) {
        error_msg = "Adding Item Failed";
        showErrorAlertFnct();
      } else {
        error_msg = "";
        showErrorAlert = false;
        toggleAddItemPanel();
        window.location.reload();
      }
    }
  }

  async function captureImage() {
    if (!videoEl) {
      camera_error = "Video element not ready!";
      return;
    }

    try {
      // 1. Create a canvas to draw the video frame
      const canvas = document.createElement("canvas");
      canvas.width = videoEl.videoWidth;
      canvas.height = videoEl.videoHeight;

      console.log("Canvas created with size:", canvas.width, canvas.height);
      const ctx = canvas.getContext("2d");
      if (!ctx) throw new Error("Failed to get canvas context");

      // 2. Draw current video frame onto the canvas
      ctx.drawImage(videoEl, 0, 0, canvas.width, canvas.height);

      // 3. Convert canvas to blob
      const blob: Blob = await new Promise((resolve) =>
        canvas.toBlob(resolve, "image/png")
      );

      // 4. Send blob to backend
      const formData = new FormData();
      formData.append("file", blob, "capture.png"); 

      const res = await fetch("/api/store_media_image", {
        method: "POST",
        body: formData,
        credentials: "include",
      });

      if (!res.ok) {
        camera_error = "Image capture failed!";
      } else {
        const data = await res.json();
        imageUrl = `${media_url}/${data.hash}.png`; 
        imageUpdated = true;
        showCameraStream = false;
        showStaticImg = true;
      }
    } catch (err) {
      console.error(err);
      camera_error = "Failed to capture image!";
    }
  }

  function toggleCameraVisibility() {
    if (showCameraStream == true) {
      showCameraStream = false;
      showStaticImg = false;
      stopCamera();
    } else {
      showCameraStream = true;
      showStaticImg = false;
      startCamera();
    }
  }

  async function downloadCSV() {
    const itemRes = await fetch(`/api/items`, {
      credentials: "include",
    });

    const items = await itemRes.json();

    // Exit if list is empty
    if (!items.length) return;

    // Extract CSV headers, excluding 'image'
    const headers = Object.keys(items[0]).filter((key) => key !== "image");

    // Format rows
    const csvRows = [
      headers.join(","), // header row
      ...items.map((item) =>
        headers.map((header) => `"${item[header] ?? ""}"`).join(",")
      ),
    ];

    const csvContent = csvRows.join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);

    // Generate timestamped filename
    const now = new Date();
    const timestamp = now.toISOString().replace(/[:.]/g, "-");
    const filename = `inventory-${timestamp}.csv`;

    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  async function downloadExcel() {
    const itemRes = await fetch(`/api/items`, {
      credentials: "include",
    });

    const items = await itemRes.json();
    if (!items.length) return;

    // Exclude 'image' from each item
    const filteredItems = items.map(({ image, ...rest }) => rest);

    // Convert filtered JSON to worksheet
    const worksheet = XLSX.utils.json_to_sheet(filteredItems);

    // Create a new workbook and append the worksheet
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Inventory");

    // Generate timestamped filename
    const now = new Date();
    const timestamp = now.toISOString().replace(/[:.]/g, "-");
    const filename = `inventory-${timestamp}.xlsx`;

    // Write the workbook to a blob and trigger download
    const excelBuffer = XLSX.write(workbook, {
      bookType: "xlsx",
      type: "array",
    });
    const blob = new Blob([excelBuffer], { type: "application/octet-stream" });

    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  async function deleteItem(itemId) {
    const res = await fetch(`/api/delete_item`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ itemId }),
    });

    if (!res.ok) {
      error_msg = "Deleting Item failed";
    } else {
      // Remove this item from the item list
      const index = items.findIndex((i) => i.id === itemId);
      if (index !== -1) {
        items.splice(index, 1);
      }
    }
  }

  async function checkoutItem(itemId) {
    const res = await fetch(`/api/checkout_item`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ itemId }),
    });

    if (!res.ok) {
      error_msg = "Item checkout failed";
    }

    // Update item in the list
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

  async function returnItem(itemId) {
    const res = await fetch(`/api/return_item`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ itemId }),
    });

    if (!res.ok) {
      error_msg = "Item return failed";
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

  async function updateItem(id, item) {
    name = item.name;
    manufacturer = item.manufacturer;
    details = item.details;
    item_type = item.item_type;
    location = item.location;
    number_items = item.number_items;
    tags = item.tags;
    description = item.description;
    manufacturer_link = item.manufacturer_link;
    manufacturer_location = item.manufacturer_location; 
    project = item.project;
    color = item.color;
    material = item.material;
    product_use = item.product_use;

    // If image not updated -> keep item.image
    if (!imageUpdated) {
      image = item.image;
    }

    if (!name) {
      error_msg = "No item name set. Define item name before updating.";
      showErrorAlertFnct();
    } else {
      let date_now = new Date();
      let date_added = date_now.toISOString();
      const res = await fetch(`/api/update_item`, {
        method: "POST",
        credentials: "include",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          id,
          name,
          manufacturer,
          details,
          item_type,
          number_items,
          description,
          location,
          tags,
          image,
          manufacturer_link,
          manufacturer_location,
          project,
          color,
          material,
          product_use,
        }),
      });

      if (!res.ok) {
        error_msg = "Adding Item Failed";
        showErrorAlertFnct();
      } else {
        error_msg = "";
        showErrorAlert = false;
        toggleEdit();
      }
    }
  }

  async function printLabel(itemId) {
    const res = await fetch(`/api/print_label`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ itemId }),
    });

    if (!res.ok) {
      error = "Printing Label failed";
    }
  }

  function requestDelete() {
    enableEdit = false;
    showConfirm = true;
  }

  function confirmDelete() {
    deleteItem(selectedItemId);
    showConfirm = false;
    selectedItemId = null;
  }

  function cancelDelete() {
    enableEdit = false;
    showConfirm = false;
  }

  function toggleItem(itemId) {
    selectedItemId = selectedItemId === itemId ? null : itemId;
  }

  function parseQRCodeData(qrString) {
    if (!qrString || typeof qrString !== "string") return null;

    const parts = qrString.split(";").map(p => p.trim());

    // Expect exactly 3 parts: [ "bigml2", "id", "9" ]
    if (parts.length !== 3) return null;

    const [prefix, key, id] = parts;

    // Validate structure
    if (prefix !== "bigml2" || key !== "id" || isNaN(Number(id))) {
      console.warn("Invalid QR structure:", parts);
      return null;
    }

    return Number(id); // return numeric ID
  }

  async function startQrScanner() {
    if (!videoEl) return;

    // Prepare canvas for frame capture
    if (!canvasEl) {
      canvasEl = document.createElement("canvas");
    }
    console.log('Enable QR scanning')
    const ctx = canvasEl.getContext("2d");

    scanning = true;
    stream_error = null;

    const scan = () => {
      if (!scanning || !showScannerPanel) return; // stop if drawer is closed

      // Match canvas size to video
      canvasEl.width = videoEl.videoWidth;
      canvasEl.height = videoEl.videoHeight;

      // Draw current frame
      ctx.drawImage(videoEl, 0, 0, canvasEl.width, canvasEl.height);
      const imageData = ctx.getImageData(0, 0, canvasEl.width, canvasEl.height);

      const qrCode = jsQR(imageData.data, imageData.width, imageData.height);
      if (qrCode) {
        const itemId = parseQRCodeData(qrCode.data);
        if (!itemId) {
          console.warn("QR code format invalid — ignoring.");
          requestAnimationFrame(scan);
          return;
        }
        console.log("✅ Valid QR Code found, item with ID ", itemId);
        
        // Stop scanning
        scanning = false;

        // Automatically close drawer
        showScannerPanel = false;

        // Find matching item
        const matchedItem = items.find(item => item.id === itemId);
        if (matchedItem) {
          selectedItemId = matchedItem.id;
          console.log("📦 Opening item card:", matchedItem.id);

          // Hide drawer
          showLeftDrawer = false;
          // Show extended item card
          const index = items.findIndex((i) => i.id === itemId);
          item = items[index];
        } else {
          console.warn("QR code valid but no matching item found.");
          stream_error = "Item not found in inventory. ID: " + itemId;
        }

        return;
      }

      scanAnimationFrame = requestAnimationFrame(scan);
    };

    scanAnimationFrame = requestAnimationFrame(scan);
  }


  async function startCamera() {
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
      });
      videoEl.srcObject = stream;
      await videoEl.play();
    } catch (err) {
      console.error("Failed to access camera:", err);
      stream_error = "Unable to access camera — check camera connection and permissions.";
    }
  }

  async function startQrCamera() {
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" },
      });
      videoEl.srcObject = stream;
      await videoEl.play();
      startQrScanner();
    } catch (err) {
      console.error("Failed to access camera:", err);
      stream_error = "Unable to access camera — check camera connection and permissions.";
    }
  }

  function stopQrScanner() {
    scanning = false;
    cancelAnimationFrame(scanAnimationFrame);
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      stream = null;
    }
    console.log('Disable QR scanning')
  }

  function stopCamera() {
    cancelAnimationFrame(scanAnimationFrame);
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      stream = null;
    }
  }

  onDestroy(() => {
    stopQrScanner();
  });

  onMount(async () => {
    // Do nothing
  });
</script>

<!-- --------------------------- PAGE CONTENT ------------------------------- -->
<svelte:head>
  <title>Inventory</title>
  <meta name="description" content="Page to add new item" />
</svelte:head>

<Section
  name="advancedTable"
  sectionClass="w-full h-full bg-gray-50 dark:bg-gray-900 p-3 sm:p-5"
>
  <TableSearch
    placeholder="Search"
    hoverable={true}
    bind:inputValue={searchTerm}
    {divClass}
    {innerDivClass}
    {searchClass}
  >
    {#snippet header()}
      <div
        class="flex w-full flex-shrink-0 flex-col items-stretch justify-end space-y-2 md:w-auto md:flex-row md:items-center md:space-y-0 md:space-x-3"
      >
        {#if user_privilege > PRIVILEGE_REPORTER}
          <Button onclick={toggleAddItemPanel}>
            <PlusOutline class="mr-2 h-3.5 w-3.5" />Add item
          </Button>
        {/if}
        <Button onclick={toggleScannerPanel}>
          <QrCodeOutline class="mr-2 h-3.5 w-3.5" /> Scan QR
        </Button>
        <Button color="alternative"
          >More<ChevronDownOutline class="ml-2 h-3 w-3 " /></Button
        >
        <Dropdown simple class="w-44 divide-y divide-gray-100">
          {#if user_privilege > PRIVILEGE_GUEST}
            <DropdownItem onclick={downloadExcel} class="text-xs"
              >Export inventory excel</DropdownItem
            >
            <DropdownItem onclick={downloadCSV} class="text-xs"
              >Export inventory csv</DropdownItem
            >
          {/if}
        </Dropdown>
        <Button color="alternative" disabled
          >Filter<FilterSolid class="ml-2 h-3 w-3 " /></Button
        >
        <Dropdown class="w-48 space-y-2 p-3 text-sm">
          <h6 class="mb-3 text-sm font-medium text-gray-900 dark:text-white">
            Choose item type
          </h6>
          <List tag="dl">
            {#each item_type_filter_options as type_option}
              <Li>
                <Checkbox
                  checked={selectedTypes.includes(type_option)}
                  onchange={() => toggleType(type_option)}
                >
                  {type_option}
                </Checkbox>
              </Li>
            {/each}
          </List>
        </Dropdown>
      </div>
    {/snippet}
    <!-- ------------------------------------------------------------------------- -->

    <div class="product-grid p-2">
      {#each currentPageItems as item}
        {#if selectedItemId === item.id}
          <!-- --------------------------- EXTENDED CARD END --------------------- -->

          <!-- svelte-ignore a11y_click_events_have_key_events -->
          <!-- svelte-ignore a11y_no_static_element_interactions -->
          <div type="overlay" class="w-full">
            <div
              class="rounded-lg expanded w-full centered mb-6 p-4 dark:bg-slate-800 bg-slate-200 border dark:border-slate-400 border-slate-800"
            >
              <div class="relative flex items-center justify-between w-full">
                <div class="flex justify-center">
                  <h2
                    class="mb-4 text-xl inline-flex font-bold items-center px-8 text-gray-800 dark:text-slate-300 border border-cyan-950 dark:border-cyan-400 rounded-lg"
                  >
                    {item.name}
                  </h2>
                </div>

                <div class="flex justify-center mt-auto">
                  {#if item.is_checked_out}
                    <label
                      for="borrowed"
                      class="mb-2 p-2 bg-red-500 text-slate-900 font-semibold border border-red-900 rounded-lg"
                      >Checked out by {item.check_out_poc} since {item.check_out_date}</label
                    >
                  {:else}
                    <label
                      for="available"
                      class="mb-2 p-2 bg-green-500 text-slate-800 font-semibold border border-slate-900 rounded-lg"
                      >Available</label
                    >
                  {/if}
                </div>

                <CloseButton
                  onclick={() => (selectedItemId = null)}
                  class="mb-4 dark:text-white"
                />
              </div>

              <div class="mb-6 grid gap-6 md:grid-cols-2">
                <div class="mb-6 flex flex-col items-center p-2 col-span-1">
                  <div class="flex items-center justify-center">
                    {#if !imageUpdated}
                      <img
                        src={`${media_url}${item.image}.png`}
                        alt={item.image}
                        class="w-full border rounded-lg border-slate-900"
                      />
                    {:else}
                      <img
                        src={`${media_url}${image}.png`}
                        alt={image}
                        class="w-full border rounded-lg border-slate-900"
                      />
                    {/if}
                  </div>
                </div>

                <form class="p-2">
                  {#if showCameraStream}
                    <div class="mb-6 flex flex-col items-center p-2 col-span-1">
                      <Label for="name" class="mb-2 block p-2"
                        >Record item image</Label
                      >
                      <Button class="w-full border mb-2 " onclick={captureImage}
                        >capture image</Button
                      >
                      <img
                        src={`${cameraServerUrl}`}
                        alt="Opening camera stream ..."
                        class="text-slate-800 dark:text-slate-400 border rounded-lg mb-2"
                      />
                      <Button
                        color="light"
                        class="w-full mb-2"
                        onclick={toggleCameraVisibility}>close camera</Button
                      >
                      <Label class="b-2 block">{camera_error}</Label>
                    </div>
                  {:else}
                    <div class="mb-2 grid gap-2 md:grid-cols-2">
                      <div>
                        <!-- svelte-ignore attribute_quoted -->
                        {#if enableEdit}
                          <FloatingLabelInput
                            clearable
                            variant="outlined"
                            bind:value={item.name}
                            class="bg-white dark:bg-slate-900 rounded-lg"
                            >name</FloatingLabelInput
                          >
                        {:else}
                          <Label
                            for="name"
                            class="mb-2 p-2 bg-slate-50 dark:bg-slate-700 rounded-lg"
                          >
                            <span class="text-red-500">Name: </span>
                            {item.name}</Label
                          >
                        {/if}
                      </div>

                      <div>
                        <!-- svelte-ignore attribute_quoted -->
                        {#if enableEdit}
                          <FloatingLabelInput
                            clearable
                            variant="outlined"
                            bind:value={item.manufacturer}
                            class="bg-white dark:bg-slate-900 rounded-lg"
                            >Manufacturer</FloatingLabelInput
                          >
                        {:else}
                          <Label
                            for="name"
                            class="mb-2 p-2 text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg"
                          >
                            <span class="text-red-500">Manufacturer: </span>
                            {item.manufacturer}
                          </Label>
                        {/if}
                      </div>

                      <div>
                        <!-- svelte-ignore attribute_quoted -->
                        {#if enableEdit}
                          <FloatingLabelInput
                            clearable
                            variant="outlined"
                            bind:value={item.manufacturer_link}
                            class="bg-white dark:bg-slate-900 rounded-lg"
                            >Manufacturer Link</FloatingLabelInput
                          >
                        {:else}
                          {#if item.manufacturer_link}
                            <a class="font-medium hover:underline justify-center" href={item.manufacturer_link} target="_blank" rel="noopener noreferrer">
                              <Label
                                for="name"
                                class="mb-2 p-2 flex justify-center text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg"
                              >
                                <span class="text-orange-300">{item.name} Product Page </span>
                              </Label>
                            </a>
                          {:else}
                            <Label
                              for="name"
                              class="mb-2 p-2 flex justify-center text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg"
                            >
                              <span class="text-gray-500">Product Page N/A</span>
                            </Label>
                          {/if}
                        {/if}
                      </div>

                      <div>
                        <!-- svelte-ignore attribute_quoted -->
                        {#if enableEdit}
                          <FloatingLabelInput
                            clearable
                            variant="outlined"
                            bind:value={item.manufacturer_location}
                            class="bg-white dark:bg-slate-900 rounded-lg"
                            >Manufacturer Location</FloatingLabelInput
                          >
                        {:else}
                          <Label
                            for="name"
                            class="mb-2 p-2 text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg"
                          >
                            <span class="text-red-500">Manufacturer Location: </span>
                            {item.manufacturer_location}
                          </Label>
                        {/if}
                      </div>

                      <div class="mb-4">
                        {#if enableEdit}
                          <Label for="number_items" class="mb-2 block"
                            >Number of Items</Label
                          >
                          <div
                            class="relative flex max-w-[8rem] items-center mb-6"
                          >
                            <ButtonGroup>
                              <Button
                                type="button"
                                id="decrement-button"
                                onclick={() => (item.number_items -= 1)}
                              >
                                <MinusOutline />
                              </Button>
                              <Input
                                bind:value={item.number_items}
                                type="number"
                                id="quantity-input"
                                aria-describedby="helper-text-explanation"
                                placeholder="{item.number_items} "
                                required
                                class="w-20"
                              />
                              <Button
                                type="button"
                                id="increment-button"
                                onclick={() => (item.number_items += 1)}
                              >
                                <PlusOutline />
                              </Button>
                            </ButtonGroup>
                          </div>
                        {:else}
                          <Label
                            class="mb-2 p-2 text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg"
                          >
                            <span class="text-red-500">Count: </span>
                            {item.number_items}</Label
                          >
                        {/if}
                      </div>

                      <div>
                        {#if enableEdit}
                          <Label
                            >Product Type
                            <Select
                              class="mt-2"
                              items={categories}
                              bind:value={item.item_type}
                            />
                          </Label>
                        {:else}
                          <Label
                            class="mb-2 p-2 bg-slate-50 dark:bg-slate-700 rounded-lg"
                          >
                            <span class="text-red-500">Product Type: </span>
                            {item.item_type}</Label
                          >
                        {/if}
                      </div>

                      <div>
                        <!-- svelte-ignore attribute_quoted -->
                        {#if enableEdit}
                          <FloatingLabelInput
                            clearable
                            variant="outlined"
                            bind:value={item.product_use}
                            class="bg-white dark:bg-slate-900 rounded-lg"
                            >Product Use</FloatingLabelInput
                          >
                        {:else}
                          <Label
                            for="name"
                            class="mb-2 p-2 text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg"
                          >
                            <span class="text-red-500">Product Use: </span>
                            {item.product_use}
                          </Label>
                        {/if}
                      </div>

                      <div>
                        <!-- svelte-ignore attribute_quoted -->
                        {#if enableEdit}
                          <FloatingLabelInput
                            clearable
                            variant="outlined"
                            bind:value={item.material}
                            class="bg-white dark:bg-slate-900 rounded-lg"
                            >Material</FloatingLabelInput
                          >
                        {:else}
                          <Label
                            for="name"
                            class="mb-2 p-2 text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg"
                          >
                            <span class="text-red-500">Material: </span>
                            {item.material}
                          </Label>
                        {/if}
                      </div>

                      <div>
                        <!-- svelte-ignore attribute_quoted -->
                        {#if enableEdit}
                          <FloatingLabelInput
                            clearable
                            variant="outlined"
                            bind:value={item.color}
                            class="bg-white dark:bg-slate-900 rounded-lg"
                            >Product Color</FloatingLabelInput
                          >
                        {:else}
                          <Label
                            for="name"
                            class="mb-2 p-2 text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg"
                          >
                            <span class="text-red-500">Product Color: </span>
                            {item.color}
                          </Label>
                        {/if}
                      </div>

                      <div>
                        <!-- svelte-ignore attribute_quoted -->
                        {#if enableEdit}
                          <FloatingLabelInput
                            clearable
                            variant="outlined"
                            bind:value={item.project}
                            class="bg-white dark:bg-slate-900 rounded-lg"
                            >Project</FloatingLabelInput
                          >
                        {:else}
                          <Label
                            for="name"
                            class="mb-2 p-2 text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg"
                          >
                            <span class="text-red-500">Project: </span>
                            {item.project}
                          </Label>
                        {/if}
                      </div>

                      <!-- svelte-ignore attribute_quoted -->
                      {#if enableEdit}
                        <div>
                          <FloatingLabelInput
                            clearable
                            variant="outlined"
                            bind:value={item.location}
                            class="bg-white dark:bg-slate-900 rounded-lg"
                            >Storage Location</FloatingLabelInput
                          >
                        </div>
                      {:else}
                        <div>
                          <Label
                            for="storage"
                            class="mb-2 p-2 text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg"
                          >
                            <span class="text-red-500">Storage Location: </span>
                            {item.location}</Label
                          >
                        </div>
                      {/if}

                      <div>
                        <!-- svelte-ignore attribute_quoted -->
                        {#if enableEdit}
                          <FloatingLabelInput
                            clearable
                            variant="outlined"
                            bind:value={item.tags}
                            class="bg-white dark:bg-slate-900 rounded-lg"
                            >Tags</FloatingLabelInput
                          >
                        {:else}
                          <Label
                            for="storage"
                            class="mb-2 p-2 text-inherit bg-slate-50 dark:bg-slate-700 rounded-lg"
                          >
                            <span class="text-red-500">Tags: </span>
                            {item.tags}</Label
                          >
                        {/if}
                      </div>

                      <div>
                        {#if !enableEdit}
                          {#if item.details}
                            <Label
                              class="mb-2 p-2 bg-slate-50 dark:bg-slate-700 rounded-lg"
                            >
                              <span class="text-red-500">Details: </span>
                              {item.details}</Label
                            >
                          {:else}
                            <Label
                              class="mb-2 p-2 bg-slate-50 dark:bg-slate-700 rounded-lg"
                            >
                              <span class="text-red-500">Details: </span> N/A</Label
                            >
                          {/if}
                        {/if}
                      </div>
                    </div>

                    <div>
                      {#if enableEdit}
                        <div class="mb-2 justify-center w-full">
                          <Label for="description" class="mb-2">Details</Label>
                          <Textarea
                            id="message"
                            class="w-full"
                            placeholder={item.detials}
                            rows={1}
                            name="message"
                            bind:value={item.details}
                          />
                        </div>

                        <div
                          class="items-center justify-center w-full mb-4"
                          role="region"
                          ondrop={onDrop}
                          ondragover={onDragOver}
                        >
                          <label
                            for="dropzone-file"
                            class="flex flex-col items-center justify-center w-full h-16 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:hover:bg-gray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500 dark:hover:bg-gray-600"
                          >
                            <div
                              class="flex flex-col items-center justify-center pt-5 pb-6"
                            >
                              <p
                                class="mb-2 text-xs text-gray-500 dark:text-gray-400"
                              >
                                <span class="font-semibold"
                                  >Click to upload</span
                                > or drag and drop
                              </p>
                              <p
                                class="text-xs text-gray-500 dark:text-gray-400"
                              >
                                SVG, PNG, JPG
                              </p>
                            </div>
                            <input
                              id="dropzone-file"
                              type="file"
                              class="hidden"
                              onchange={handleFileUpload}
                            />
                          </label>
                        </div>
                      {/if}
                    </div>

                    <div
                      class="bottom-0 left-0 flex w-full justify-start space-x-4 pb-4 md:px-4"
                    >
                      {#if enableEdit}
                        <Button
                          onclick={() => updateItem(selectedItemId, item)}
                          color="green"
                        >
                          <CheckCircleOutline
                            type="print-button"
                            color="green"
                            class="me-2 h-5 w-5"
                          /> confirm edit
                        </Button>
                        <!-- Delete Items only for users of maintainer privilege and above -->
                        {#if user_privilege >= PRIVILEGE_MAINTAINER}
                          <Button color="red" onclick={() => requestDelete()}>
                            <FolderArrowRightOutline
                              type="return-button"
                              class="me-2 h-5 w-5"
                            /> delete item
                          </Button>
                        {/if}
                        <Button type="camera" onclick={toggleCameraVisibility}>
                          open camera
                        </Button>
                        <Button color="light" onclick={() => toggleEdit()}>
                          <CloseOutline
                            type="print-button"
                            class="me-2 h-5 w-5"
                          /> cancel edit
                        </Button>
                      {:else if showConfirm}
                        <div
                          class="mb-2 p-2 border border-red-900 bg-red-500 rounded-lg"
                        >
                          <Label class="mb-2 p-2 text-slate-950"
                            >Are you sure you want to delete this item?</Label
                          >
                          <div class="row-span-3 md:row-span-4">
                            <Button
                              color="red"
                              onclick={confirmDelete}
                              class="mb-4 border border-slate-900"
                            >
                              <ExclamationCircleOutline
                                type="delete-button"
                                class="me-2 h-5 w-5"
                              /> yes, delete
                            </Button>
                            <Button
                              color="light"
                              onclick={cancelDelete}
                              class="mb-4 dark:text-white"
                            >
                              <CloseOutline
                                type="confirm-button"
                                class="me-2 h-5 w-5"
                              /> cancel
                            </Button>
                          </div>
                        </div>
                      {:else}
                        {#if item.is_checked_out}
                          <Button
                            color="green"
                            onclick={() => returnItem(selectedItemId)}
                            class="mb-4"
                          >
                            <FolderArrowRightOutline
                              type="return-button"
                              class="me-2 h-5 w-5"
                            /> return item
                          </Button>
                        {:else}
                          <Button
                            onclick={() => checkoutItem(selectedItemId)}
                            class="mb-4"
                          >
                            <CartPlusAltOutline
                              type="return-button"
                              class="me-2 h-5 w-5"
                            /> borrow
                          </Button>
                        {/if}
                        <Button
                          onclick={() => printLabel(selectedItemId)}
                          class="mb-4"
                        >
                          <PrinterOutline
                            type="print-button"
                            class="me-2 h-5 w-5"
                          /> print label
                        </Button>
                        {#if user_privilege > PRIVILEGE_REPORTER}
                          <Button onclick={() => toggleEdit()} class="mb-4">
                            <PenOutline
                              type="print-button"
                              class="me-2 h-5 w-5"
                            /> edit
                          </Button>
                        {/if}
                        <Button
                          color="light"
                          onclick={() => (selectedItemId = null)}
                          class="mb-4 dark:text-white"
                        >
                          <CloseOutline
                            type="print-button"
                            class="me-2 h-5 w-5"
                          /> close
                        </Button>
                      {/if}
                    </div>
                  {/if}
                </form>
              </div>
            </div>
          </div>

          <!-- --------------------------- EXTENDED CARD END --------------------- -->
        {:else if !selectedItemId}
          <!-- Normal grid card display -->
          <!-- svelte-ignore a11y_click_events_have_key_events -->
          <!-- svelte-ignore a11y_no_static_element_interactions -->
          <div
            class="mb-6 h-full flex-col items-center justify-start border rounded-lg border-inherit bg-slate-100 dark:bg-slate-700 p-2"
            onclick={() => toggleItem(item.id)}
          >
            <div class="flex justify-center mt-auto">
              {#if item.is_checked_out}
                <label
                  for="red"
                  class="mb-2 p-2 bg-red-500 text-slate-900 font-semibold border border-red-500 rounded-lg"
                  >Checked out by {item.check_out_poc} since {item.check_out_date}</label
                >
              {:else}
                <label
                  for="green"
                  class="mb-2 p-2 bg-green-500 text-slate-800 font-semibold border border-green-500 rounded-lg"
                  >Available</label
                >
              {/if}
            </div>
            <img
              src={`${media_url}${item.image}.png`}
              alt={item.name}
              class="mb-6 w-full max-w-96 border rounded-lg border-slate-900"
            />
            <div class="p-2 text-orange-500 font-bold">{item.name}</div>
            {#if item.manufacturer}
              <div class="p-2 text-slate-900 dark:text-slate-200">
                by {item.manufacturer}
              </div>
            {:else}
              <div class="p-2 text-slate-900 dark:text-slate-200">
                Manufactuer N/A
              </div>
            {/if}
            {#if item.item_type}
              <div class="p-2 text-slate-900 dark:text-slate-200">
                Type: {item.item_type}
              </div>
            {/if}
          </div>
        {/if}
      {/each}
    </div>

    <!-- ------------------------------------------------------------------------- -->
    {#snippet footer()}
      <div
        class="flex flex-col items-start justify-between space-y-3 p-4 md:flex-row md:items-center md:space-y-0"
        aria-label="Table navigation"
      >
        <span class="text-sm font-normal text-gray-500 dark:text-gray-400">
          Showing
          <span class="font-semibold text-gray-900 dark:text-white"
            >{startRange}-{endRange}</span
          >
          of
          <span class="font-semibold text-gray-900 dark:text-white"
            >{totalItems}</span
          >
        </span>
        <ButtonGroup>
          <Button onclick={loadPreviousPage} disabled={currentPosition === 0}
            ><ChevronLeftOutline size="xs" class="m-1.5" /></Button
          >
          {#each pagesToShow as pageNumber}
            <Button onclick={() => goToPage(pageNumber)}>{pageNumber}</Button>
          {/each}
          <Button onclick={loadNextPage} disabled={totalPages === endPage}
            ><ChevronRightOutline size="xs" class="m-1.5" /></Button
          >
        </ButtonGroup>
      </div>
    {/snippet}
  </TableSearch>
</Section>

<!-- ---------------------   ADD ITEM SIDE PANEL --------------------------- -->

<!-- <Section name="crudcreatedrawer"> -->
<Drawer bind:open={showLeftDrawer} id="sidebar4" class="w-3/4">
  {#if showAddItemPanel}
    <div class="flex items-center justify-between">
      <h5
        id="drawer-label"
        class="mb-6 inline-flex items-center text-base font-semibold text-gray-500 uppercase dark:text-gray-400"
      >
        New Item
      </h5>
    </div>

    <form action="#" class="mb-2">
      {#if showCameraStream}
        <div class="mb-6 flex flex-col items-center p-2 col-span-1">
          <Label for="name" class="mb-2 block p-2">Capture Product Image</Label>
          <!-- TODO : bug fix image capture routine and enable button -->
          <Button class="w-full border mb-2 " onclick={captureImage} disabled
            >capture image</Button
          >
          <div class="mb-6 flex flex-col items-center p-2 col-span-1 w-full h-full">
            <p class="text-red-600">{stream_error}</p>
            {#if !stream_error}
              <div class="flex items-center justify-center w-full h-full">
                <video
                  bind:this={videoEl}
                  autoplay
                  playsinline
                  class="rounded-lg w-full h-full max-h-[80vh] object-contain"
                >
                  <track kind="captions" />
                </video>
              </div>
            {/if}
          </div>
          <Button
            color="light"
            class="w-full mb-2"
            onclick={toggleCameraVisibility}>close camera</Button
          >
          <Label class="b-2 block">{camera_error}</Label>
        </div>
      {:else}
        <div class="mb-4 p-2 gap-1">
          <div class="mb-4 grid gap-2 md:grid-cols-2">
            {#if image}
              <div class="w-full flex justify-center">
                <img
                  src={`${media_url}${image}.png`}
                  alt={image}
                  class="max-w-[220px] max-h-[220px]"
                />
              </div>
            {:else}
              <div
                class="bg-slate-900 flex justify-center max-w-[220px] max-h-[220px] min-w-[220px] min-h-[220px]"
              ></div>
            {/if}

            <div class="mb-6">
              <div class="mb-6">
                <Label for="name" class="mb-2 block">Name</Label>
                <Input
                  id="name"
                  name="name"
                  required
                  placeholder="Item name"
                  bind:value={name}
                />
              </div>

              <div class="mb-6">
                <Label for="manufacturer" class="mb-2 block">Manufacturer</Label
                >
                <Input
                  id="manufacturer"
                  name="manufacturer"
                  placeholder="Item manufacturer"
                  bind:value={manufacturer}
                />
              </div>

              <div class="mb-6">
                <Label for="manufacturer_link" class="mb-2 block">Manufacturer Link</Label
                >
                <Input
                  id="manufacturer_link"
                  name="manufacturer_link"
                  placeholder="Manufacturer link"
                  bind:value={manufacturer_link}
                />
              </div>

              <div class="mb-6">
                <Label for="manufacturer_location" class="mb-2 block">Manufacturer Location</Label
                >
                <Input
                  id="manufacturer_location"
                  name="manufacturer_location"
                  placeholder="Manufacturer location"
                  bind:value={manufacturer_location}
                />
              </div>
            </div>

          <div
            class="items-center justify-center w-full"
            role="region"
            ondrop={onDrop}
            ondragover={onDragOver}
          >
            <label
              for="dropzone-file"
              class="flex flex-col items-center justify-center w-full h-16 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:hover:bg-gray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500 dark:hover:bg-gray-600"
            >
              <div class="flex flex-col items-center justify-center pt-5 pb-6">
                <p class="mb-2 text-xs text-gray-500 dark:text-gray-400">
                  <span class="font-semibold">Click to upload</span> or drag and
                  drop
                </p>
                <p class="text-xs text-gray-500 dark:text-gray-400">
                  SVG, PNG, JPG
                </p>
              </div>
              <input
                id="dropzone-file"
                type="file"
                class="hidden"
                onchange={handleFileUpload}
              />
            </label>
          </div>

            <div class="mb-6 w-full">
              <Label for="number_items" class="mb-2 block"
                >Number of Items</Label
              >
              <div class="relative items-center mb-6">
                <ButtonGroup>
                  <Button
                    type="button"
                    id="decrement-button"
                    onclick={() => (number_items -= 1)}
                  >
                    <MinusOutline />
                  </Button>
                  <Input
                    bind:value={number_items}
                    type="number"
                    id="quantity-input"
                    aria-describedby="helper-text-explanation"
                    placeholder="1"
                    required
                    class="w-20"
                  />
                  <Button
                    type="button"
                    id="increment-button"
                    onclick={() => (number_items += 1)}
                  >
                    <PlusOutline />
                  </Button>
                </ButtonGroup>
              </div>
            </div>

            <div class="mb-6">
              <Label
                >Item Type
                <Select
                  class="mt-2"
                  items={categories}
                  bind:value={item_type}
                />
              </Label>
            </div>

            <div class="mb-6">
              <Label for="location" class="mb-2 block">Storage Location</Label>
              <Input
                id="location"
                name="location"
                placeholder="Storage location"
                bind:value={location}
              />
            </div>

            <div class="mb-6">
              <Label for="tags" class="mb-2 block">Tags</Label>
              <Input
                id="tags"
                name="tags"
                placeholder="Tags"
                bind:value={tags}
              />
            </div>

            <div class="mb-6">
              <Label for="tags" class="mb-2 block">Material</Label>
              <Input
                id="material"
                name="material"
                placeholder="Material"
                bind:value={material}
              />
            </div>

            <div class="mb-6">
              <Label for="color" class="mb-2 block">Color</Label>
              <Input
                id="color"
                name="color"
                placeholder="Color"
                bind:value={color}
              />
            </div>

            <div class="mb-6">
              <Label for="project" class="mb-2 block">Project</Label>
              <Input
                id="project"
                name="project"
                placeholder="Project"
                bind:value={project}
              />
            </div>

            <div class="mb-6">
              <Label for="product_use" class="mb-2 block">Product Use</Label>
              <Input
                id="product_use"
                name="product_use"
                placeholder="Product Use"
                bind:value={product_use}
              />
            </div>
          </div>

          <div class="mb-2 justify-center w-full">
            <Label for="description" class="mb-2">Description</Label>
            <Textarea
              id="message"
              class="w-full"
              placeholder="Enter a detailed item description here"
              rows={1}
              name="message"
              bind:value={details}
            />
          </div>

        </div>

        <div class="sticky bottom-0 left-0 flex w-full justify-center space-x-4 p-4 bg-white dark:bg-gray-800 border-t">
          <Button type="submit" color="green" class="w-full" onclick={addItem}
            >add item</Button
          >
          <Button type="camera" class="w-full" onclick={toggleCameraVisibility}
            >open camera</Button
          >
          <Button
            class="w-full"
            color="light"
            onclick={() => (showLeftDrawer = false)}
          >
            <svg
              aria-hidden="true"
              class="-ml-1 h-5 w-5 sm:mr-1"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
            cancel
          </Button>
        </div>
      {/if}
    </form>
  {:else if showScannerPanel}

    <div class="mb-6 flex flex-col items-center p-2 col-span-1 w-full h-full">
      <Label for="name" class="mb-2 block p-2">Hold the QR label in front of the camera!</Label>
      <p class="text-red-600">{stream_error}</p>
      {#if !stream_error}
        <div class="flex items-center justify-center w-full h-full">
          <video
            bind:this={videoEl}
            autoplay
            playsinline
            class="rounded-lg w-full h-full max-h-[80vh] object-contain"
          >
            <track kind="captions" />
          </video>
        </div>
      {/if}
    </div>
  {/if}
</Drawer>

<!-- </Section> -->

<style>
  .product-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
  }
</style>
