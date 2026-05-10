<script lang="ts">
  import { onMount, onDestroy } from "svelte";
  import jsQR from "jsqr";
  import { goto } from "$app/navigation";

  let videoEl = $state<HTMLVideoElement | null>(null);
  let canvasEl = $state<HTMLCanvasElement | null>(null);
  let stream = $state<MediaStream | null>(null);
  let error = $state("");
  let scanning = true;

  async function startCamera() {
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment" }
      });
      if (videoEl) {
        videoEl.srcObject = stream;
        videoEl.play();
        requestAnimationFrame(tick);
      }
    } catch (err) {
      error = "Camera access denied.";
    }
  }

  // Fixed: not async, returns the value directly
  function parseQrPayload(qr_payload: string): { type: number; id: number } {
    if (!qr_payload || typeof qr_payload !== "string") {
      return { type: 0, id: 0 };
    }

    const parts = qr_payload.split(";").map(p => p.trim());

    // Expect exactly 3 parts: [ "iitem" | "istr", "id", "<number>" ]
    if (parts.length !== 3) {
      return { type: 0, id: 0 };
    }

    const [prefix, key, rawId] = parts;

    if (
      (prefix !== "iitem" && prefix !== "istr") ||
      key !== "id" ||
      isNaN(Number(rawId))
    ) {
      console.warn("Invalid QR structure:", parts);
      return { type: 0, id: 0 };
    }

    if (prefix === "iitem") return { type: 1, id: Number(rawId) };
    if (prefix === "istr")  return { type: 2, id: Number(rawId) };

    return { type: 0, id: 0 };
  }

  function handleScanResult(raw: string) {
    const { type, id } = parseQrPayload(raw);

    if (type === 0) {
      // Unknown/invalid QR — resume scanning
      scanning = true;
      requestAnimationFrame(tick);
      return;
    }

    // Stop the camera before navigating
    stream?.getTracks().forEach(t => t.stop());

    if (type === 1) {
      goto(`/inventory/item/${id}`);
    } else if (type === 2) {
      goto(`/inventory/storage/${id}`);
    }
  }

  function tick() {
    if (!scanning || !videoEl || !canvasEl) return;

    if (videoEl.readyState === videoEl.HAVE_ENOUGH_DATA) {
      canvasEl.height = videoEl.videoHeight;
      canvasEl.width  = videoEl.videoWidth;

      const ctx = canvasEl.getContext("2d");
      if (ctx) {
        ctx.drawImage(videoEl, 0, 0, canvasEl.width, canvasEl.height);
        const imageData = ctx.getImageData(0, 0, canvasEl.width, canvasEl.height);
        const code = jsQR(imageData.data, imageData.width, imageData.height);

        if (code) {
          scanning = false;
          handleScanResult(code.data);
          return;
        }
      }
    }

    requestAnimationFrame(tick);
  }

  onMount(() => {
    canvasEl = document.createElement("canvas");
    startCamera();
  });

  onDestroy(() => {
    scanning = false;
    stream?.getTracks().forEach(t => t.stop());
  });
</script>

<!-- Wrap the scanner in a flex container that grows -->
<div class="flex flex-col h-[calc(100vh-120px)] w-full">
  <div class="relative flex-1 overflow-hidden rounded-lg bg-black">
    {#if error}
      <div class="flex h-full items-center justify-center p-4 text-center text-white">
        <p>{error}</p>
      </div>
    {:else}
      <!-- svelte-ignore a11y_media_has_caption -->
      <video
        bind:this={videoEl}
        class="absolute inset-0 h-full w-full object-cover"
      ></video>

      <!-- Scanning overlay -->
      <div class="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div class="w-64 h-64 border-2 border-dashed border-red-500 opacity-70"></div>
      </div>
      <div class="absolute bottom-4 left-0 right-0 text-center pointer-events-none">
        <span class="bg-black/50 text-white text-xs px-2 py-1 rounded">
          Align QR code within the frame
        </span>
      </div>
    {/if}
  </div>
</div>