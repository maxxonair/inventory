<script>
  import { onMount } from "svelte";
  import { goto } from '$app/navigation';
  import { Camera, CameraOff, SquareArrowDown, SquareArrowUp, TableProperties} from 'lucide-svelte';

  let showCameraStream = $state(0);
  // URL where media files are hosted 
  let streamUrl = "http://localhost:5050";
  const media_url = "http://127.0.0.1:5000/media/";

  let imageUrl = $state("");

  imageUrl = '${streamUrl}'

  // Library item Properties 
  let name = $state("");
  let manufacturer = $state("");
  let details = $state("");
  let number_items =$state(1);
  let image= $state("");

  let description = $state("");
  let item_type = $state("");
  let location = $state("");
  let check_out_poc = $state("");
  let check_out_date = $state("");
  let is_checked_out = 0;


  let error_msg = $state("");
  let camera_error = $state("");

  const { user } = $props();

  async function add_inventory_item() {
    let date_now = new Date();
    let date_added = date_now.toISOString();
    const res = await fetch("http://localhost:5000/add_item", {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name, manufacturer, details, item_type, number_items, image, description, location, date_added, check_out_poc, check_out_date, is_checked_out}),
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
    camera_error = "Image capture failed!";
  }
  else
  {
    image = await res.json();
    imageUrl = '${media_url}/${image}.png'
    console.log("Image captured successfully, hash -> ",image)

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

<h1 class="headline">Add New Item</h1>

<div class="page-container">
  <form class="item-box" >
    <input
      type="text"
      placeholder="Name"
      bind:value={name}
      required
    />
    <input
      type="text"
      placeholder="Manufacturer"
      bind:value={manufacturer}
      required
    />
    <input
      type="text"
      placeholder="Details"
      bind:value={details}
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
      bind:value={number_items}
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
    <label class="label" >{image}</label>
    <label class="label" >{camera_error}</label>
    {/if}
    <label class="label" for="avatar">Or load a picture from file:</label>
    <input class="upload-button" type="file" id="avatar" name="avatar" accept="image/png, image/jpeg" />
    <button type="submit" class="add-button" title="Add item to the inventory" onclick={add_inventory_item}>
      Add to Library
    </button>
    <label class="label" >{error_msg}</label>
  </form>
</div>


