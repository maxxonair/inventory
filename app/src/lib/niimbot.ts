// niimbot.ts
// This file contains functions to generate and print QR codes using a Niimbot 
// D110 label printer over Bluetooth.
import QRCode from "qrcode";
  
// -----------------------------
// Constants
// -----------------------------
const NIIMBOT_D110_MAX_WIDTH_PX = 120;
const NIIMBOT_D110_MAX_HEIGHT_PX = 100; 

export const SERVICE_UUID = "e7810a71-73ae-499d-8c15-faa9aef0c3f2";
export const CHAR_UUID = "bef8d6c9-9c21-4c9e-b632-bd58c1009f9f";

// -----------------------------
// NiimbotPacket class
// -----------------------------
  class NiimbotPacket {
    type: number;
    data: Uint8Array;

    constructor(type: number, data: Uint8Array) {
      this.type = type;
      this.data = data;
    }

    toBytes(): Uint8Array {
      let checksum = this.type ^ this.data.length;
      for (const b of this.data) checksum ^= b;

      const out = new Uint8Array(2 + 1 + 1 + this.data.length + 1 + 2); // 0x55 0x55 + type + len + data + checksum + 0xAA 0xAA
      out[0] = 0x55;
      out[1] = 0x55;
      out[2] = this.type;
      out[3] = this.data.length;
      out.set(this.data, 4);
      out[4 + this.data.length] = checksum;
      out[5 + this.data.length] = 0xAA;
      out[6 + this.data.length] = 0xAA;
      return out;
    }
  }

  // -----------------------------
  // Helper functions
  // -----------------------------

  export function resizeCanvasToFit(src: HTMLCanvasElement, maxWidth: number, maxHeight: number) {
    const scale = Math.min(maxWidth / src.width, maxHeight / src.height, 1);
    if (scale === 1) return src; // already fits

    const dst = document.createElement("canvas");
    dst.width = Math.floor(src.width * scale);
    dst.height = Math.floor(src.height * scale);

    const ctx = dst.getContext("2d")!;
    ctx.drawImage(src, 0, 0, dst.width, dst.height);
    return dst;
  }


  export function sleep(ms: number) {
    return new Promise((res) => setTimeout(res, ms));
  }

  // Helper: add top padding (which becomes LEFT after Niimbot rotates)
  function addTopPadding(src: HTMLCanvasElement, padding = 30, bg = "white") {
    const dst = document.createElement("canvas");
    dst.width = src.width;
    dst.height = src.height + padding;
    const ctx = dst.getContext("2d")!;
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, dst.width, dst.height);
    ctx.drawImage(src, 0, padding);
    return dst;
  }

  // Fit for Niimbot: user supplies the printer's printed max width/height in PX (printed units)
  // Niimbot rotates 90° clockwise at print time, so:
  // printedWidthPx  <-- preRotationHeight
  // printedHeightPx <-- preRotationWidth
  export function fitCanvasForNiimbot(
    src: HTMLCanvasElement,
    printedMaxWidthPx: number,   // how many px the printer can print across (final printed width)
    printedMaxHeightPx: number,  // how many px the printer can print down (final printed height)
    drawDebugBox = true
  ) {
    // compute pre-rotation constraints
    const preRotMaxWidth = printedMaxHeightPx; // pre-rotation width must be <= printedHeight
    const preRotMaxHeight = printedMaxWidthPx; // pre-rotation height must be <= printedWidth

    // compute scale that keeps aspect and doesn't enlarge
    const scale = Math.min(preRotMaxWidth / src.width, preRotMaxHeight / src.height, 1);

    const w = Math.floor(src.width * scale);
    const h = Math.floor(src.height * scale);

    const dst = document.createElement("canvas");
    dst.width = w;
    dst.height = h;

    const ctx = dst.getContext("2d")!;
    // White background - matches most label printers; change if you need transparent
    ctx.fillStyle = "white";
    ctx.fillRect(0, 0, w, h);

    // draw the scaled image crisply (use imageSmoothing for safety)
    ctx.imageSmoothingEnabled = false;
    ctx.drawImage(src, 0, 0, w, h);

    // optional debug overlay: draw the printable area in red (pre-rotation bounds)
    if (drawDebugBox) {
      ctx.strokeStyle = "red";
      ctx.lineWidth = 2;
      // printable area (should be the full dst area if scale < 1)
      ctx.strokeRect(0, 0, w - 1, h - 1);
      // also print helpful info to console
      console.info("fitCanvasForNiimbot debug:",
        { srcWidth: src.width, srcHeight: src.height, scale, preRotMaxWidth, preRotMaxHeight, outW: w, outH: h });
    }

    return dst;
  }

  function padCanvasWidthToByteBoundary(src: HTMLCanvasElement) {
    const remainder = src.width % 8;
    if (remainder === 0) return src;

    const newWidth = src.width + (8 - remainder);

    const dst = document.createElement("canvas");
    dst.width = newWidth;
    dst.height = src.height;

    const ctx = dst.getContext("2d")!;
    ctx.fillStyle = "white"; // fill padding
    ctx.fillRect(0, 0, newWidth, src.height);

    ctx.drawImage(src, 0, 0);

    return dst;
  }

  export function canvasToMono(canvas: HTMLCanvasElement): { width: number; height: number; pixels: number[][] } {
    const ctx = canvas.getContext("2d")!;
    const w = canvas.width;
    const h = canvas.height;
    const img = ctx.getImageData(0, 0, w, h).data;

    const pixels: number[][] = [];
    for (let y = 0; y < h; y++) {
      const row: number[] = [];
      for (let x = 0; x < w; x++) {
        const i = (y * w + x) * 4;
        const r = img[i];
        const g = img[i + 1];
        const b = img[i + 2];
        const lum = 0.299 * r + 0.587 * g + 0.114 * b;
        // Invert: white=0, black=1
        row.push(lum < 128 ? 1 : 0);
      }
      pixels.push(row);
    }
    return { width: w, height: h, pixels };
  }

  export function generateRowPacket(y: number, row: number[]): NiimbotPacket {
    const width = row.length;
    let bits = "";
    for (let b of row) bits += b.toString();
    const rowBytes = new Uint8Array(Math.ceil(width / 8));
    for (let i = 0; i < rowBytes.length; i++) {
      const byteStr = bits.slice(i * 8, i * 8 + 8).padEnd(8, "0");
      rowBytes[i] = parseInt(byteStr, 2);
    }
    // header: y (2B big-endian), counts 0,0,0 (3B), 1 (height 1 row)
    const header = new Uint8Array(6);
    header[0] = (y >> 8) & 0xff;
    header[1] = y & 0xff;
    header[2] = 0;
    header[3] = 0;
    header[4] = 0;
    header[5] = 1;
    return new NiimbotPacket(0x85, new Uint8Array([...header, ...rowBytes]));
  }

  // -----------------------------
  // Connect to D110
  // -----------------------------
  export async function connectD110() {
    const device = await navigator.bluetooth.requestDevice({
      filters: [{ namePrefix: "D110" }],
      optionalServices: [SERVICE_UUID],
    });

    const server = await device.gatt!.connect();
    const service = await server.getPrimaryService(SERVICE_UUID);
    const char = await service.getCharacteristic(CHAR_UUID);
    return { server, char };
  }

  // -----------------------------
  // Generate QR canvas
  // -----------------------------
  export function generateQrCanvas(text: string, px = 384): Promise<HTMLCanvasElement> {
    const canvas = document.createElement("canvas");
    canvas.width = px;
    canvas.height = px;
    return new Promise((resolve, reject) => {
      // @ts-ignore
      QRCode.toCanvas(
        canvas,
        text,
        { errorCorrectionLevel: "H", margin: 1.2, width: px },
        (err: any) => {
          if (err) reject(err);
          else resolve(canvas);
        }
      );
    });
  }

  // -----------------------------
  // Write NiimbotPacket over BLE
  // -----------------------------
  export async function writePacket(char: BluetoothRemoteGATTCharacteristic, pkt: NiimbotPacket) {
    const bytes = pkt.toBytes();
    const MTU = 160;
    for (let i = 0; i < bytes.length; i += MTU) {
      const chunk = bytes.slice(i, i + MTU);
      await char.writeValue(chunk);
      await sleep(10);
    }
  }

  // -----------------------------
  // Main print function
  // -----------------------------
  export async function printQR(itemId: string) {
    const qrString = `bigml2;id;${itemId}`;

    // 1) Generate QR
    let canvas = await generateQrCanvas(qrString, NIIMBOT_D110_MAX_HEIGHT_PX);
    
    // 2) add top padding (becomes left when printed)
    canvas = addTopPadding(canvas, 2);

    // 3) fit for Niimbot using the printer's printed limits (in px).
    canvas = fitCanvasForNiimbot(canvas, NIIMBOT_D110_MAX_WIDTH_PX, NIIMBOT_D110_MAX_HEIGHT_PX, true);
    canvas = padCanvasWidthToByteBoundary(canvas);

    // canvas = rotateForNiimbot(canvas);

    // 3) Convert to monochrome pixels
    const { width, height, pixels } = canvasToMono(canvas);

    // 4) Connect
    const { server, char } = await connectD110();
    console.log("Connected…");

    // 5) START_PRINT
    await writePacket(char, new NiimbotPacket(0x01, new Uint8Array([0x01])));

    // 6) START_PAGE_PRINT
    await writePacket(char, new NiimbotPacket(0x03, new Uint8Array([0x01])));

    // 7) SET_DIMENSION (width, height) big-endian
    const dim = new Uint8Array([ (width >> 8) & 0xff, width & 0xff, (height >> 8) & 0xff, height & 0xff ]);
    await writePacket(char, new NiimbotPacket(0x13, dim));

    // 8) Send each row
    for (let y = 0; y < height; y++) {
      const rowPkt = generateRowPacket(y, pixels[y]);
      await writePacket(char, rowPkt);
    }

    // 9) END_PAGE_PRINT
    await writePacket(char, new NiimbotPacket(0xE3, new Uint8Array([0x01])));

    // 10) END_PRINT
    await writePacket(char, new NiimbotPacket(0xF3, new Uint8Array([0x01])));

    console.log("PRINT DONE")
  }