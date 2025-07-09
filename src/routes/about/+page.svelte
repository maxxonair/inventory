<script>
  import { onMount } from "svelte";
  let streamUrl = "http://localhost:5050";

  // Detect if run from mobile or desktop
  let isMobile = false;

  onMount(() => {
    const ua = navigator.userAgent;
    isMobile = /Mobi|Android|iPhone|iPad|iPod/i.test(ua);
  });
</script>

<svelte:head>
  <title>About</title>
  <meta name="description" content="Video stream test page" />
</svelte:head>

<!-- Works with MJPEG streaming -->
<img src={streamUrl} alt="Camera Stream" class="border rounded" />
