import { Document } from "../types";
import apiClient from "./apiClient";

export async function getDocuments(): Promise<Document[]> {
  const { data } = await apiClient.get<Document[]>("/documents/");
  return data;
}

export async function uploadDocumentFile(payload: {
  title: string;
  category: string;
  source: string;
  file: File;
}): Promise<Document> {
  const formData = new FormData();
  formData.append("title", payload.title);
  formData.append("category", payload.category);
  formData.append("source", payload.source);
  formData.append("file", payload.file);
  const { data } = await apiClient.post<Document>("/documents/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function deleteDocument(documentId: number): Promise<void> {
  await apiClient.delete(`/documents/${documentId}`);
}

export async function updateDocument(
  documentId: number,
  payload: Partial<Pick<Document, "title" | "category" | "source" | "content">>
): Promise<Document> {
  const { data } = await apiClient.put<Document>(`/documents/${documentId}`, payload);
  return data;
}

function parseFilenameFromContentDisposition(header: string | undefined): string | null {
  if (!header) return null;
  const utf8 = /filename\*=UTF-8''([^;\s]+)/i.exec(header);
  if (utf8) {
    try {
      return decodeURIComponent(utf8[1].trim());
    } catch {
      return null;
    }
  }
  const quoted = /filename="([^"]+)"/i.exec(header);
  if (quoted) return quoted[1];
  const plain = /filename=([^;\s]+)/i.exec(header);
  if (plain) return plain[1].replace(/"/g, "");
  return null;
}

export type DownloadHints = {
  fileType?: string | null;
  fileName?: string | null;
};

function fallbackDownloadFilename(title: string, hints?: DownloadHints): string {
  const safe = title.replace(/[^\w\s.\-]+/g, "").trim().replace(/\s+/g, "_") || "document";
  const fromApi = hints?.fileName?.trim();
  if (fromApi && fromApi !== "-") {
    const base = fromApi.replace(/[/\\?*:|"<>]/g, "_").replace(/^\.+/, "") || safe;
    return base;
  }
  const ft = (hints?.fileType || "").toLowerCase();
  if (ft === "pdf") return `${safe}.pdf`;
  if (ft === "txt") return `${safe}.txt`;
  return `${safe}.txt`;
}

/** Download original file (PDF/TXT upload) or a .txt export of stored text-only documents. */
export async function downloadDocument(
  documentId: number,
  fallbackTitle: string,
  hints?: DownloadHints
): Promise<void> {
  const response = await apiClient.get<Blob>(`/documents/${documentId}/download`, {
    responseType: "blob",
  });
  const header =
    (response.headers["content-disposition"] as string | undefined) ??
    (response.headers["Content-Disposition"] as string | undefined);
  const parsed = parseFilenameFromContentDisposition(header);
  const filename = parsed ?? fallbackDownloadFilename(fallbackTitle, hints);
  const url = URL.createObjectURL(response.data);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}
