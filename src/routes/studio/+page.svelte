<script>
  import { onMount } from "svelte";
  import { goto } from '$app/navigation';
  import { Camera, CameraOff, SquareArrowDown, SquareArrowUp} from 'lucide-svelte';

  let streamUrl = "http://localhost:5050";

  let showCameraStream = $state(0);

  let item_name = $state("");
  let item_manufacturer = $state("");
  let item_details = $state("");
  let item_type = $state("");
  let item_num =$state(1);
  let image_name= $state("");

  let error_msg = $state("");
  let camera_error = $state("");

  const { user } = $props();

  async function add_inventory_item() {
    const res = await fetch("http://localhost:5000/add_item", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ item_name, item_manufacturer, item_details, item_type, item_num, image_name}),
  });
  if (!res.ok) {
    error_msg = "Adding Item Failed";
  }
  else
  {
    error_msg = "";
  }
}

  async function capture_image() {
    const res = await fetch("http://localhost:5050/capture_image", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ }),
  });

  if (!res.ok) {
    camera_error = "Invalid credentials";
  }
  else
  {
    image_name = await res.json();
  }
}

  function toggleCameraVisibility() {
		if (showCameraStream == 1){showCameraStream = 0;} else {showCameraStream = 1;}
	}

</script>

<style>
  .page-container {
    display: flex;
    justify-content: center;
    align-items: top;
    height: 100vh; /* full viewport height */
  }

  .headline {
    font-size: 3rem;
    font-weight: bold;
    color: #c85203
  }

  .label{
    justify-content: center;
    text-align: center;
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

  .add-button{
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

  .camera-button{
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

  .upload-button{
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

</style>

<svelte:head>
  <title>About</title>
  <meta name="description" content="Page to add new item" />
</svelte:head>

<h1 class="headline">Add New Item</h1>

<div class="page-container">
  <form class="item-box" >
    <input
      type="text"
      placeholder="Name"
      bind:value={item_name}
      required
    />
    <input
      type="text"
      placeholder="Manufacturer"
      bind:value={item_manufacturer}
      required
    />
    <input
      type="text"
      placeholder="Details"
      bind:value={item_details}
      required
    />
    <input
      type="text"
      placeholder="Type"
      bind:value={item_type}
      required
    />
    <label for="avatar">Number of items:</label>
    <input
      type="number"
      placeholder="Details"
      bind:value={item_num}
      required
    />
    <label class="label" for="avatar">Take an item picture in the studio:</label>
    <button class="camera-button" onclick={toggleCameraVisibility}>
      {#if showCameraStream}
      Close Camera
      {:else}
      Open Camera
      {/if}
    </button>
    <!-- Works with MJPEG streaming -->
    {#if showCameraStream}
    <img src={streamUrl} alt="Camera Stream" class="border rounded" />
    <button class="camera-button" onclick={capture_image}>
      <Camera size={20} /> Capture Image
    </button>
    <label class="label" >{camera_error}</label>
    {/if}
    <label class="label" for="avatar">Or load a picture from file:</label>
    <input class="upload-button" type="file" id="avatar" name="avatar" accept="image/png, image/jpeg" />
    <button type="submit" class="add-button" onclick={add_inventory_item}>
      Add New Item
    </button>
    <label class="label" >{error_msg}</label>
  </form>
</div>


