// niimbot.ts
// Functions to generate and print QR codes (with an optional text label) using
// a Niimbot D110 label printer over Bluetooth.
import QRCode from "qrcode";

// -----------------------------
// Constants
// -----------------------------

// Canvas dimensions in pixels. printDirection="left" in ImageEncoder rotates
// the canvas 90° CW, so the printer sees:
//   cols = canvas.height  (must be multiple of 8) → short axis of the label
//   rows = canvas.width                           → long axis of the label
const CANVAS_W = 240;  // long axis  (rows after rotation)
const CANVAS_H = 96;   // short axis (cols after rotation, must be multiple of 8)

export const SERVICE_UUID = "e7810a71-73ae-499d-8c15-faa9aef0c3f2";
export const CHAR_UUID    = "bef8d6c9-9c21-4c9e-b632-bd58c1009f9f";

// -----------------------------
// Printer model profiles
// -----------------------------
// D110 and D110_M share hardware specs (203 DPI, 96px printhead, print
// direction "left") but use different print-task sequences and density
// ranges. See https://printers.niim.blue/interfacing/print-tasks/ and
// https://printers.niim.blue/hardware/niimbot-d110_m/
export type PrinterModel = "D110" | "D110_M";

interface ModelProfile {
  minDensity: number;
  maxDensity: number;
  defaultDensity: number;
}

export const MODEL_PROFILES: Record<PrinterModel, ModelProfile> = {
  D110:   { minDensity: 1, maxDensity: 3, defaultDensity: 2 },
  D110_M: { minDensity: 1, maxDensity: 5, defaultDensity: 3 },
};

// -----------------------------
// Packet helpers (matching reference implementation)
// -----------------------------

function makePacket(cmd: number, data: number[]): Uint8Array {
  let checksum = cmd ^ data.length;
  for (const b of data) checksum ^= b;

  // Connect packet gets a 0x03 prefix per reference packet.ts
  const body = [0x55, 0x55, cmd, data.length, ...data, checksum, 0xaa, 0xaa];
  return new Uint8Array(cmd === 0xc1 ? [0x03, ...body] : body);
}

function u16(n: number): [number, number] {
  return [(n >> 8) & 0xff, n & 0xff];
}

// PrintStart (0x01), 9-byte variant used by the D110M_V4 task.
// Layout: totalPages(u16), always-0(4 bytes), pageColor(u8), speed(u8), flag(u8)
// speed: 0 = higher quality / slower, 1 = lower quality / faster.
function printStart9b(totalPages: number, speed = 0): number[] {
  const [hi, lo] = u16(totalPages);
  return [hi, lo, 0, 0, 0, 0, /* pageColor */ 0, speed, /* flag */ 0];
}

// SetPageSize (0x13), 13-byte variant used by the D110M_V4 task.
// Layout: rows(u16), cols(u16), copies(u16), cutHeight(u16), cutType(u16),
// sendAll(u8), partHeight(u16). Copies replaces the separate PrintQuantity
// (0x15) command, which D110M_V4 does not use.
function setPageSize13b(rows: number, cols: number, copies: number): number[] {
  const [rowsHi, rowsLo] = u16(rows);
  const [colsHi, colsLo] = u16(cols);
  const [copHi, copLo]   = u16(copies);
  return [rowsHi, rowsLo, colsHi, colsLo, copHi, copLo, 0, 0, 0, 0, 0, 0, 0];
}

// Count non-zero bits in a byte array, split across three equal chunks.
// Matches Utils.countPixelsForBitmapPacket with mode="auto".
function countPixels(data: Uint8Array, printheadPixels: number): [number, number, number] {
  const chunkSize = Math.floor(printheadPixels / 8 / 3);
  const canSplit  = data.byteLength <= chunkSize * 3;
  const parts: [number, number, number] = [0, 0, 0];
  let total = 0;

  data.forEach((val, byteN) => {
    for (let bit = 0; bit < 8; bit++) {
      if (val & (1 << bit)) {
        total++;
        if (canSplit) {
          const chunk = Math.floor(byteN / chunkSize);
          if (chunk <= 2) parts[chunk]++;
        }
      }
    }
  });

  if (canSplit) return parts;
  const [h, l] = u16(total);
  return [0, l, h];
}

// -----------------------------
// Image encoding
// -----------------------------

// Matches ImageEncoder.encodeCanvas with printDirection="left":
// rotates 90° CW so canvas.height becomes cols (short axis).
function encodeCanvas(canvas: HTMLCanvasElement): {
  cols: number; rows: number;
  rowsData: Array<{ rowNumber: number; repeat: number; blackCount: number; data?: Uint8Array }>
} {
  const ctx  = canvas.getContext("2d")!;
  const iData = ctx.getImageData(0, 0, canvas.width, canvas.height);

  // After 90° CW rotation: cols = canvas.height, rows = canvas.width
  const cols = canvas.height;
  const rows = canvas.width;

  if (cols % 8 !== 0) throw new Error(`cols (${cols}) must be a multiple of 8`);

  const rowsData: Array<{ rowNumber: number; repeat: number; blackCount: number; data?: Uint8Array }> = [];

  for (let row = 0; row < rows; row++) {
    let isEmpty    = true;
    let blackCount = 0;
    const rowData  = new Uint8Array(cols / 8);

    for (let colOct = 0; colOct < cols / 8; colOct++) {
      let octet = 0;
      for (let colBit = 0; colBit < 8; colBit++) {
        // printDirection="left": idx = (height - 1 - x) * width + y
        const x   = colOct * 8 + colBit;
        const idx = ((iData.height - 1 - x) * iData.width + row) * 4;
        const isBlack = iData.data[idx] !== 255 || iData.data[idx+1] !== 255 || iData.data[idx+2] !== 255;
        if (isBlack) {
          octet |= 1 << (7 - colBit);
          isEmpty = false;
          blackCount++;
        }
      }
      rowData[colOct] = octet;
    }

    const entry = { rowNumber: row, repeat: 1, blackCount, data: isEmpty ? undefined : rowData };

    if (rowsData.length === 0) {
      rowsData.push(entry);
    } else {
      const last = rowsData[rowsData.length - 1];
      const same = entry.data === undefined
        ? last.data === undefined
        : last.data !== undefined && entry.data.every((b, i) => b === last.data![i]);

      if (same) {
        last.repeat++;
      } else {
        rowsData.push(entry);
      }

      // Check line every 200 rows (matches reference sendRowCheck logic)
      if (row % 200 === 199) {
        rowsData.push({ rowNumber: row, repeat: 0, blackCount: 0, data: undefined });
      }
    }
  }

  return { cols, rows, rowsData };
}

// -----------------------------
// Canvas layout helpers
// -----------------------------

export function sleep(ms: number): Promise<void> {
  return new Promise((res) => setTimeout(res, ms));
}

function createPrintCanvas(): { canvas: HTMLCanvasElement; ctx: CanvasRenderingContext2D } {
  const canvas  = document.createElement("canvas");
  canvas.width  = CANVAS_W;
  canvas.height = CANVAS_H;
  const ctx     = canvas.getContext("2d")!;
  ctx.fillStyle = "white";
  ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);
  return { canvas, ctx };
}

// QR only, centred on the canvas.
function renderQrOnly(qr: HTMLCanvasElement): HTMLCanvasElement {
  const { canvas, ctx } = createPrintCanvas();
  const padding = 2;
  const qrSize  = Math.min(qr.width, CANVAS_H - padding * 2);
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(qr,
    Math.floor((CANVAS_W - qrSize) / 2),
    Math.floor((CANVAS_H - qrSize) / 2),
    qrSize, qrSize);
  return canvas;
}

// Text on the left, QR on the right, both vertically centred.
// The content block (text + gap + QR) is centred along CANVAS_W so both
// elements sit closer to the middle of the label rather than at the edges.
function compositeQrWithLabel(
  qr: HTMLCanvasElement,
  label: string,
  fontSize  = 13,
  gap       = 6,
  padding   = 2,
): HTMLCanvasElement {
  const { canvas, ctx } = createPrintCanvas();

  const qrSize = Math.min(qr.width, CANVAS_H - padding * 2);

  const lineHeight = fontSize + 3;
  const tmp = document.createElement("canvas").getContext("2d")!;
  tmp.font  = `bold ${fontSize}px monospace`;

  // Max text column width: remaining space after QR + gap + side padding.
  const maxTextW = CANVAS_W - qrSize - gap - padding * 2;

  const words = label.split(" ");
  const lines: string[] = [];
  let line = "";
  for (const word of words) {
    const test = line ? `${line} ${word}` : word;
    if (tmp.measureText(test).width > maxTextW && line) {
      lines.push(line);
      line = word;
    } else {
      line = test;
    }
  }
  if (line) lines.push(line);

  const textBlockW = Math.min(
    Math.ceil(Math.max(...lines.map(l => tmp.measureText(l).width))),
    maxTextW,
  );
  const textBlockH = lines.length * lineHeight;

  // Centre the whole content block (text + gap + QR) along CANVAS_W.
  const contentW = textBlockW + gap + qrSize;
  const startX   = Math.floor((CANVAS_W - contentW) / 2);

  // QR on the right side of the content block, vertically centred.
  const qrX = startX + textBlockW + gap;
  const qrY = Math.floor((CANVAS_H - qrSize) / 2);
  ctx.imageSmoothingEnabled = false;
  ctx.drawImage(qr, qrX, qrY, qrSize, qrSize);

  // Text on the left side of the content block, vertically centred.
  const textY = Math.floor((CANVAS_H - textBlockH) / 2);
  ctx.fillStyle    = "black";
  ctx.font         = `bold ${fontSize}px monospace`;
  ctx.textBaseline = "top";
  ctx.textAlign    = "left";
  for (let i = 0; i < lines.length; i++) {
    ctx.fillText(lines[i], startX, textY + i * lineHeight, maxTextW);
  }

  return canvas;
}

// -----------------------------
// QR generation
// -----------------------------

export function generateQrCanvas(text: string, px: number): Promise<HTMLCanvasElement> {
  return new Promise((resolve, reject) => {
    // @ts-ignore
    QRCode.toCanvas(
      text,
      { errorCorrectionLevel: "H", margin: 2, width: px },
      (err: any, canvas: HTMLCanvasElement) => (err ? reject(err) : resolve(canvas)),
    );
  });
}

// -----------------------------
// BLE connection
// -----------------------------

export async function connectD110(): Promise<BluetoothRemoteGATTCharacteristic> {
  const device  = await navigator.bluetooth.requestDevice({
    filters: [{ namePrefix: "D110" }],
    optionalServices: [SERVICE_UUID],
  });
  const server  = await device.gatt!.connect();
  const service = await server.getPrimaryService(SERVICE_UUID);
  const char    = await service.getCharacteristic(CHAR_UUID);
  // Needed so we can listen for responses (e.g. the model-id query below) —
  // the D110 line is NOTIFY + WRITE_NO_RESPONSE, so without this we can send
  // commands but never see what the printer reports back.
  await char.startNotifications();
  return char;
}

// -----------------------------
// BLE write
// -----------------------------

async function send(char: BluetoothRemoteGATTCharacteristic, packet: Uint8Array): Promise<void> {
  const MTU = 160;
  for (let i = 0; i < packet.length; i += MTU) {
    await char.writeValue(packet.slice(i, i + MTU));
    await sleep(10);
  }
}

// -----------------------------
// BLE response parsing / model detection
// -----------------------------

// Parses a single 0x55 0x55 cmd len ...data crc 0xaa 0xaa notification frame.
// Doesn't handle multi-frame reassembly — fine for the small fixed-size
// responses (info queries, acks) used here.
function parsePacket(bytes: Uint8Array): { cmd: number; data: Uint8Array } | null {
  if (bytes.length < 7 || bytes[0] !== 0x55 || bytes[1] !== 0x55) return null;
  const cmd = bytes[2];
  const len = bytes[3];
  if (bytes.length < 4 + len + 3) return null;
  return { cmd, data: bytes.slice(4, 4 + len) };
}

// Sends `packet` and resolves with the data payload of the first notification
// whose command matches `expectCmd`, or rejects if none arrives in time.
function sendAndWait(
  char: BluetoothRemoteGATTCharacteristic,
  packet: Uint8Array,
  expectCmd: number,
  timeoutMs = 2000,
): Promise<Uint8Array> {
  return new Promise((resolve, reject) => {
    let timer: ReturnType<typeof setTimeout>;

    const onValue = (ev: Event) => {
      const value = (ev.target as BluetoothRemoteGATTCharacteristic).value;
      if (!value) return;
      const bytes  = new Uint8Array(value.buffer, value.byteOffset, value.byteLength);
      const parsed = parsePacket(bytes);
      if (parsed && parsed.cmd === expectCmd) {
        clearTimeout(timer);
        char.removeEventListener("characteristicvaluechanged", onValue);
        resolve(parsed.data);
      }
    };

    timer = setTimeout(() => {
      char.removeEventListener("characteristicvaluechanged", onValue);
      reject(new Error(`Timed out waiting for response 0x${expectCmd.toString(16)}`));
    }, timeoutMs);

    char.addEventListener("characteristicvaluechanged", onValue);
    send(char, packet).catch((err) => {
      clearTimeout(timer);
      char.removeEventListener("characteristicvaluechanged", onValue);
      reject(err);
    });
  });
}

// Known modelId → PrinterModel.
//   2304 → D110    (confirmed via PrinterInfo/DeviceType on real hardware)
//   2320 → D110_M  (community-confirmed: https://xcr4k.hatenablog.com/entry/label_printer_niimbot_d110_m,
//                   https://github.com/MultiMote/niimbluelib/issues/1)
// Any other id seen on a "D110*"-named device falls back to the D110 task —
// extend this map if you run into a different id that turns out to need the
// D110_M task instead.
const MODEL_ID_MAP: Record<number, PrinterModel> = {
  2304: "D110",
  2320: "D110_M",
};

/**
 * Query the connected printer for its model id (PrinterInfo, DeviceType
 * sub-code 0x08) and map it to "D110" or "D110_M". Falls back to "D110"
 * (logging a warning) if the printer doesn't respond in time or reports an
 * id we don't recognize — "D110" is the simpler/more conservative task of
 * the two, so it's the safer default to guess wrong toward.
 */
export async function detectPrinterModel(
  char: BluetoothRemoteGATTCharacteristic,
): Promise<PrinterModel> {
  try {
    const data = await sendAndWait(char, makePacket(0x40, [0x08]), 0x48);
    // big-endian u16; some firmwares reply with just 1 byte (byte << 8)
    const modelId = data.length >= 2 ? (data[0] << 8) | data[1] : data[0] << 8;
    const model = MODEL_ID_MAP[modelId];
    if (model) {
      console.log(`Detected printer model: ${model} (id ${modelId})`);
      return model;
    }
    console.warn(`Unrecognized printer model id ${modelId}; defaulting to D110 print task.`);
    return "D110";
  } catch (err) {
    console.warn("Could not query printer model, defaulting to D110 print task:", err);
    return "D110";
  }
}

// -----------------------------
// Main print function
// -----------------------------

/**
 * Print a QR code for `qrPayload` on a Niimbot D110 or D110_M.
 * If `label` is provided it is rendered as plain text to the left of the QR.
 * If `model` is omitted, it's auto-detected by querying the printer right
 * after connecting (see detectPrinterModel) — pass it explicitly to skip
 * that round-trip.
 */
export async function printQR(
  qrPayload: string,
  label?: string,
  model?: PrinterModel,
): Promise<void> {
  // 1. Build canvas layout.
  //    QR is sized to fit CANVAS_H (the short axis, 96 px) with padding.
  const qr     = await generateQrCanvas(qrPayload, CANVAS_H - 4);
  const canvas = label ? compositeQrWithLabel(qr, label) : renderQrOnly(qr);

  // 2. Encode using the same rotation logic as ImageEncoder.encodeCanvas("left").
  //    After rotation: cols = canvas.height = 96, rows = canvas.width = 240
  const image = encodeCanvas(canvas);
  console.log(`Encoded: ${image.rows} rows × ${image.cols} cols`);

  // 3. Connect, then figure out which print task to use.
  const char = await connectD110();
  console.log("Connected…");

  const resolvedModel = model ?? await detectPrinterModel(char);
  console.log(`Printing with the ${resolvedModel} task`);

  // Printhead resolution for the D110 (96 px wide print head)
  const printheadPixels = image.cols;

  // 4. Print sequence — the two models use different print tasks
  //    (see https://printers.niim.blue/interfacing/print-tasks/):
  //
  //    D110:    setDensity → setLabelType → printStart1b
  //             → printClear → pageStart → setPageSize4b(rows, cols) → setPrintQuantity
  //             → bitmap rows → pageEnd → printEnd
  //
  //    D110_M:  setDensity → setLabelType → printStart9b(totalPages)
  //             → setPageSize13b(rows, cols, copies) → printStatus (fire-and-forget)
  //             → bitmap rows → pageEnd → printEnd → heartbeat (fire-and-forget)
  //             (no printClear, no pageStart, no separate setPrintQuantity —
  //              copies count is folded into setPageSize13b instead)

  const density = MODEL_PROFILES[resolvedModel].defaultDensity;
  await send(char, makePacket(0x21, [density]));                                  // setDensity
  await send(char, makePacket(0x23, [1]));                                        // setLabelType(WithGaps=1)

  if (resolvedModel === "D110") {
    await send(char, makePacket(0x01, [0x01]));                                     // printStart1b
    await send(char, makePacket(0x20, [0x01]));                                     // printClear
    await send(char, makePacket(0x03, [0x01]));                                     // pageStart
    await send(char, makePacket(0x13, [...u16(image.rows), ...u16(image.cols)]));   // setPageSize4b(rows, cols)
    await send(char, makePacket(0x15, [...u16(1)]));                                // setPrintQuantity(1)
  } else {
    await send(char, makePacket(0x01, printStart9b(1)));                            // printStart9b(totalPages=1)
    await send(char, makePacket(0x13, setPageSize13b(image.rows, image.cols, 1)));  // setPageSize13b(rows, cols, copies=1)
    await send(char, makePacket(0xa3, [0x01]));                                     // printStatus (fire-and-forget)
  }

  for (const row of image.rowsData) {
    if (row.data === undefined) {
      // Empty row or check line
      if (row.repeat === 0) {
        // check line packet (0x86)
        await send(char, makePacket(0x86, [...u16(row.rowNumber), 0x01]));
      } else {
        // printEmptySpace (0x84)
        await send(char, makePacket(0x84, [...u16(row.rowNumber), row.repeat]));
      }
    } else if (row.blackCount <= 6) {
      // printBitmapRowIndexed (0x83): encode pixel positions as u16 indexes
      const indexes: number[] = [];
      for (let bytePos = 0; bytePos < row.data.length; bytePos++) {
        for (let bit = 7; bit >= 0; bit--) {
          if (row.data[bytePos] & (1 << bit)) {
            const idx = bytePos * 8 + (7 - bit);
            indexes.push(...u16(idx));
          }
        }
      }
      const counts = countPixels(row.data, printheadPixels);
      await send(char, makePacket(0x83, [...u16(row.rowNumber), ...counts, row.repeat, ...indexes]));
    } else {
      // printBitmapRow (0x85)
      const counts = countPixels(row.data, printheadPixels);
      await send(char, makePacket(0x85, [...u16(row.rowNumber), ...counts, row.repeat, ...row.data]));
    }
  }

  await send(char, makePacket(0xe3, [0x01]));  // pageEnd
  await send(char, makePacket(0xf3, [0x01]));  // printEnd

  if (resolvedModel === "D110_M") {
    // protocolVersion >= 3 printers (D110_M reports protocolVersion 4) expect
    // the "Advanced 2" heartbeat payload (0x04) rather than 0x01.
    await send(char, makePacket(0xdc, [0x04]));  // heartbeat (fire-and-forget)
  }

  console.log("Print done.");
}