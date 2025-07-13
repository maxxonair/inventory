<script>
  import { onMount } from "svelte";
  import { goto } from '$app/navigation';
  import { Camera, CameraOff, SquareArrowDown} from 'lucide-svelte';

  let streamUrl = "http://localhost:5050";

  let showCameraStream = $state(0);

  const { user } = $props();

  function toggleCameraVisibility() {
		if (showCameraStream == 1){showCameraStream = 0;} else {showCameraStream = 1;}
	}

</script>

<svelte:head>
  <title>About</title>
  <meta name="description" content="Video stream test page" />
</svelte:head>

<button onclick={toggleCameraVisibility}>
  {#if showCameraStream}
  <CameraOff size={20} /> Hide Camera Stream <SquareArrowDown size={20} />
  {:else}
  <Camera size={20} /> Show Camera Stream <SquareArrowDown size={20} />
  {/if}
</button>

<!-- Works with MJPEG streaming -->
{#if showCameraStream}
 <img src={streamUrl} alt="Camera Stream" class="border rounded" />
{/if}
