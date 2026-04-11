import { useEffect, useState } from "react";
import axios from "axios";
import { Download, PencilLine } from "lucide-react";
import toast from "react-hot-toast";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";
import EmptyState from "../components/ui/EmptyState";
import Input from "../components/ui/Input";
import {
  deleteDocument,
  downloadDocument,
  getDocuments,
  updateDocument,
  uploadDocumentFile,
} from "../services/documentService";
import { Document } from "../types";

export default function UploadPage() {
  const [title, setTitle] = useState("");
  const [category, setCategory] = useState("general");
  const [source, setSource] = useState("upload");
  const [file, setFile] = useState<File | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);

  const refresh = async () => {
    try {
      const docs = await getDocuments();
      setDocuments(docs);
    } catch {
      toast.error("Could not fetch documents");
    }
  };

  useEffect(() => {
    void refresh();
  }, []);

  const handleUpload = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!file) {
      toast.error("Please select a file");
      return;
    }

    setLoading(true);
    try {
      await uploadDocumentFile({ title: title.trim(), category: category.trim() || "general", source: source.trim() || "upload", file });
      setTitle("");
      setCategory("general");
      setSource("upload");
      setFile(null);
      toast.success("📄 Document uploaded successfully");
      await refresh();
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.status === 409) {
        toast.error("Document with this title already exists in your department");
      } else {
        const msg = err instanceof Error ? err.message : "Upload failed";
        toast.error(msg || "Upload failed");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (documentId: number) => {
    try {
      await deleteDocument(documentId);
      toast.success("Document deleted");
      await refresh();
    } catch {
      toast.error("Delete failed");
    }
  };

  const handleDownload = async (doc: Document) => {
    try {
      await downloadDocument(doc.id, doc.title, {
        fileType: doc.file_type,
        fileName: doc.file_name,
      });
    } catch {
      toast.error("Download failed");
    }
  };

  const handleUpdate = async (document: Document) => {
    setEditingId(document.id);
    try {
      await updateDocument(document.id, {
        title: document.title,
        category: document.category,
        source: document.source,
      });
      toast.success("Document updated");
      setEditingId(null);
      await refresh();
    } catch {
      toast.error("Update failed");
    } finally {
      setEditingId(null);
    }
  };

  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-800">Upload Documents</h2>
        <p className="text-sm text-slate-500">Admin-only document ingestion for PDF/TXT sources.</p>
      </div>

      <Card>
        <form onSubmit={handleUpload} className="grid gap-3 md:grid-cols-2">
          <Input
            placeholder="Title"
            label="Title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />
          <Input
            placeholder="Category"
            label="Category"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          />
          <Input
            placeholder="Source"
            label="Source"
            value={source}
            onChange={(e) => setSource(e.target.value)}
          />
          <Input
            label="File"
            type="file"
            accept=".pdf,.txt"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            required
          />
          <Button className="md:col-span-2" type="submit" isLoading={loading}>
            {loading ? "Uploading..." : "Upload document"}
          </Button>
        </form>
      </Card>

      <Card title="Manage Documents" description="Update or remove uploaded documents.">
        {documents.length === 0 && (
          <EmptyState
            icon={<PencilLine size={18} />}
            title="No documents found"
            description="Upload your first PDF/TXT document to get started."
          />
        )}
        <div className="space-y-3">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="flex flex-col gap-3 rounded-lg border border-slate-200 bg-white p-4 sm:flex-row sm:items-start sm:justify-between"
            >
              <div className="flex-1">
                <h3 className="text-sm font-semibold text-slate-900">{doc.title}</h3>
                <p className="mt-1 text-2xs text-slate-600">
                  📁 {doc.category} · 📌 {doc.source}
                </p>
                {doc.stored_file_path && (
                  <p className="mt-1 text-2xs font-mono text-slate-500" title="Storage path">
                    💾 {doc.stored_file_path}
                  </p>
                )}
                {doc.file_name && (
                  <p className="mt-1 text-2xs text-slate-500">
                    📄 Original: <span className="font-medium">{doc.file_name}</span>
                  </p>
                )}
                <p className="mt-2 text-2xs text-slate-400">
                  ID: {doc.id} · Created: {new Date(doc.created_at).toLocaleDateString()}
                </p>
              </div>
              <div className="flex flex-wrap gap-2 sm:flex-col sm:flex-nowrap">
                <Button
                  type="button"
                  title="Download original file or text export"
                  onClick={() => void handleDownload(doc)}
                >
                  <Download size={16} />
                  Download
                </Button>
                <Button
                  variant="danger"
                  type="button"
                  title="Delete this document"
                  onClick={() => void handleDelete(doc.id)}
                >
                  Delete
                </Button>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </section>
  );
}
