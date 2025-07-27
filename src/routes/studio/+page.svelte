<script>
  import { onMount } from "svelte";
  import { goto } from "$app/navigation";
  import { Textarea } from "flowbite-svelte";
  import {
    Camera,
    CameraOff,
    SquareArrowDown,
    SquareArrowUp,
    TableProperties,
    Check,
    ShieldAlert
  } from "lucide-svelte";

  // URL where media files are hosted
  let streamUrl = "http://localhost:5050";
  const media_url = "http://127.0.0.1:5000/media/";
  const { user } = $props();
  let showSuccessAlert = $state(false);
  let showErrorAlert = $state(false);

  let imageUrl = $state("");
  imageUrl = "${streamUrl}";

  let showCameraStream = $state(false);
  let showStaticImg = $state(false);

  // Library item Properties
  let name = $state("");
  let manufacturer = $state("");
  let details = $state("");
  let number_items = $state(1);
  let image = $state("");
  let tags = $state("");

  let description = $state("");
  let item_type = $state("");
  let location = $state("");
  let check_out_poc = $state("");
  let check_out_date = $state("");
  let is_checked_out = 0;

  let error_msg = $state("");
  let camera_error = $state("");

  let selectedFile = $state(null);

  async function handleFileUpload(Event) {
    const input = event.target;
    if (input.files && input.files.length > 0) {
      selectedFile = input.files[0];

      const formData = new FormData();
      formData.append("avatar", selectedFile);

      try {
        const response = await fetch("http://127.0.0.1:5000/image_upload", {
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

  const closeSuccessAlertAlert = () => {
    alert("Clicked closeAlert.");
    showSuccessAlert = !showSuccessAlert;
  };
  function showSuccessAlertFnct() {
    showSuccessAlert = true;
    // Auto-dismiss Alerts after 5 seconds
    setTimeout(() => {
      showSuccessAlert = false;
    }, 5000);
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

  async function add_inventory_item() {
    if (!name){
      error_msg = "No item name set. Define item name before adding.";
      showErrorAlertFnct();
    }
    else
    {
      let date_now = new Date();
      let date_added = date_now.toISOString();
      const res = await fetch("http://localhost:5000/add_item", {
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
        }),
      });

      if (!res.ok) {
        error_msg = "Adding Item Failed";
        showErrorAlertFnct();
      } else {
        error_msg = "";
        closeErrorAlertAlert();
        showSuccessAlertFnct();
      }
    }
  }

  async function capture_image() {
    const res = await fetch("http://localhost:5050/capture_image", {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({}),
    });

    if (!res.ok) {
      camera_error = "Image capture failed!";
    } else {
      image = await res.json();
      imageUrl = `${media_url}/${image}.png`;
      showCameraStream = false;
      showStaticImg = true;
    }
  }

  function toggleCameraVisibility() {
    if (showCameraStream == true) {
      showCameraStream = false;
      showStaticImg = false;
    } else {
      showCameraStream = true;
      showStaticImg = false;
    }
  }
</script>

<!-- ------------------------------------------------------------------------------- -->

<h1 class="headline">Add New Item</h1>

<div class="page-container">
  <form class="item-box">
    {#if showSuccessAlert}
      <label class="success-alert">
        <Check size={20} />
        Item successfully added to Inventory
      </label>
    {/if}
    {#if showErrorAlert}
      <label class="error-alert">
        <ShieldAlert size={20} />
        {error_msg}
      </label>
    {/if}
    <input
      type="text"
      class="input-field"
      placeholder="Name"
      bind:value={name}
      required
    />
    <input
      type="text"
      class="input-field"
      placeholder="Manufacturer"
      bind:value={manufacturer}
    />
    <div class="input-text-field">
      <Textarea
        id="textarea-id"
        class="my-4 w-full"
        bind:value={details}
        placeholder="Details"
        rows={4}
        name="message"
      />
    </div>
    <input
      type="text"
      placeholder="Type"
      class="input-field"
      bind:value={item_type}
    />
    <input
      type="text"
      placeholder="Tags"
      class="input-field"
      bind:value={tags}
    />
    <label class="label" for="avatar">Number of items:</label>
    <input
      type="number"
      class="input-field"
      placeholder="Details"
      bind:value={number_items}
      required
    />
    <!-- Works with MJPEG streaming -->
    {#if showCameraStream}
      <label class="label" for="avatar"
        >Take an item picture in the studio:</label
      >
      <button class="camera-button" onclick={capture_image}>
        Capture Image
      </button>
      <img src={streamUrl} alt="Camera Stream" class="border rounded" />
      <label class="label">{camera_error}</label>
      <button class="close-button" onclick={toggleCameraVisibility}>
        Close Camera
      </button>
    {:else}
      {#if showStaticImg}
        <label class="label" for="avatar">Item Image</label>
        <img src={`${imageUrl}`} alt={image} class="product-image" />
        <button class="camera-button" onclick={toggleCameraVisibility}
          >Re-take Image
        </button>
      {:else}
        <button class="toggle-camera-button" onclick={toggleCameraVisibility}>
          {#if showCameraStream}
            Close Camera
          {:else}
            Open Camera
          {/if}
        </button>
      {/if}
      <label class="label" for="avatar">Or load a picture from file:</label>
      <input
        class="upload-button"
        type="file"
        id="avatar"
        name="avatar"
        accept="image/png, image/jpeg"
        onchange={handleFileUpload}
      />
      <button
        type="submit"
        class="add-button"
        title="Add item to the inventory"
        onclick={add_inventory_item}
      >
        Add to Library
      </button>
    {/if}
  </form>
</div>

<!-- ------------------------------------------------------------------------------- -->

<style>
  .page-container {
    display: flex;
    justify-content: center;
    align-items: top;
    height: 135vh; /* full viewport height */
  }

  .headline {
    font-size: 3rem;
    font-weight: bold;
    color: #c85203;
  }

  .label {
    justify-content: center;
    text-align: center;
  }

  .success-alert {
    justify-content: left;
    text-align: center;
    background-color: rgb(130, 251, 130);
    border-color: rgb(91, 179, 91);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    border-radius: 1rem;
    padding: 1.5rem;
  }

  .error-alert {
    justify-content: left;
    text-align: center;
    background-color: rgb(213, 94, 94);
    border-color: rgb(166, 38, 38);
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    border-radius: 1rem;
    padding: 1.5rem;
  }

  .item-box {
    background-color: white;
    padding: 2rem;
    border-radius: 1rem;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.1);
    width: 100%;
    max-width: 400px;
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .product-image {
    max-height: 200px;
    object-fit: contain;
    margin-bottom: 1rem;
    border-bottom: 1px solid #d37e1d;
    padding-bottom: 1rem;
  }

  .input-text-field {
    background-color: #494949;
    color: #fa8d1f;
    padding: 0.5rem;
    margin: 0 auto 1rem;
    transition: background-color 0.2s ease;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    border-radius: 6px;
  }

  .input-field {
    background-color: #494949;
    color: #fa8d1f;
    border-radius: 9999px;
    border-color: #fa8d1f;
    padding: 0.5rem;
    margin: 0 auto 0.5rem;
    cursor: pointer;
    transition: background-color 0.2s ease;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    text-align: center;
  }

  .add-button {
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

  .upload-button {
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

  .toggle-camera-button {
    background-color: #252525;
    color: #fa8d1f;
    border: none;
    border-radius: 9999px;
    padding: 0.8rem;
    margin: 0 auto 1rem;
    cursor: pointer;
    transition: background-color 0.2s ease;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  }

  .camera-button {
    background-color: #252525;
    color: #fa8d1f;
    border: none;
    border-radius: 9999px;
    padding: 0.3rem;
    cursor: pointer;
    transition: background-color 0.2s ease;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  }

  .close-button {
    justify-content: center;
    margin-top: 0.05rem;
    background-color: #c1c1c1;
    color: #252525;
    border: none;
    border-radius: 9999px;
    padding: 0.1rem;
    cursor: pointer;
    transition: background-color 0.2s ease;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  }

  .extra-details {
    margin-top: 1rem;
    border-top: 1px solid #eee;
    padding-top: 1rem;
  }
</style>
