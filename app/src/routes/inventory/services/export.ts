import * as XLSX from "xlsx";

/**
 * Generates a timestamped filename
 */
const getFilename = (base: string, extension: string) => {
  const now = new Date();
  const timestamp = now.toISOString().replace(/[:.]/g, "-");
  return `${base}-${timestamp}.${extension}`;
};

/**
 * Triggers a browser download for a given Blob
 */
const downloadFile = (blob: Blob, filename: string) => {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * Resolves the numeric location ID on each item to its human-readable name,
 * then renames the field from 'location' to 'storage_location' for clarity.
 */
const resolveLocations = (
  items: any[],
  storageLocations: { id: number; name: string }[]
): any[] => {
  const locationMap = new Map(storageLocations.map((sl) => [sl.id, sl.name]));
  return items.map(({ location, ...rest }) => ({
    ...rest,
    storage_location: locationMap.get(location) ?? location ?? "",
  }));
};

/**
 * Export inventory items to CSV, excluding images
 */
export const downloadCSV = (
  items: any[],
  storageLocations: { id: number; name: string }[] = []
) => {
  if (!items.length) return;

  const resolvedItems = resolveLocations(items, storageLocations);

  // Extract headers excluding 'image' and 'avatar'
  const headers = Object.keys(resolvedItems[0]).filter(
    (key) => key !== "image" && key !== "avatar"
  );

  const csvRows = [
    headers.join(","), // Header row
    ...resolvedItems.map((item) =>
      headers.map((header) => `"${item[header] ?? ""}"`).join(",")
    ),
  ];

  const csvContent = csvRows.join("\n");
  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });

  downloadFile(blob, getFilename("inventory", "csv"));
};

/**
 * Export inventory items to Excel (XLSX), excluding images
 */
export const downloadExcel = (
  items: any[],
  storageLocations: { id: number; name: string }[] = []
) => {
  if (!items.length) return;

  const resolvedItems = resolveLocations(items, storageLocations);

  // Create a copy of items without the image property
  const filteredData = resolvedItems.map(({ image, avatar, ...rest }) => rest);

  const worksheet = XLSX.utils.json_to_sheet(filteredData);
  const workbook = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(workbook, worksheet, "Inventory");

  const excelBuffer = XLSX.write(workbook, {
    bookType: "xlsx",
    type: "array",
  });

  const blob = new Blob([excelBuffer], { type: "application/octet-stream" });

  downloadFile(blob, getFilename("inventory", "xlsx"));
};