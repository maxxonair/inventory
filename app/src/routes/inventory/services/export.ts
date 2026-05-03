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
 * Export inventory items to CSV, excluding images
 */
export const downloadCSV = (items: any[]) => {
  if (!items.length) return;

  // Extract headers excluding 'image' and 'avatar'
  const headers = Object.keys(items[0]).filter(
    (key) => key !== "image" && key !== "avatar"
  );

  const csvRows = [
    headers.join(","), // Header row
    ...items.map((item) =>
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
export const downloadExcel = (items: any[]) => {
  if (!items.length) return;

  // Create a copy of items without the image property
  const filteredData = items.map(({ image, avatar, ...rest }) => rest);

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