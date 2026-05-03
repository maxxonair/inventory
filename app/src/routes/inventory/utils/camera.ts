// src/routes/inventory/utils/camera.ts
export async function getCameraStream() {
  return await navigator.mediaDevices.getUserMedia({
    video: { facingMode: "environment" },
  });
}

export function stopStream(stream: MediaStream | null) {
  stream?.getTracks().forEach(track => track.stop());
}