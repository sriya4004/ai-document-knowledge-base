import { useCallback, useEffect, useState } from "react";
import { Download, FileText, RefreshCw, Search as SearchIcon } from "lucide-react";
import { useLocation } from "react-router-dom";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";
import EmptyState from "../components/ui/EmptyState";
import Skeleton from "../components/ui/Skeleton";
import { downloadDocument, getDocuments } from "../services/documentService";
import { getDashboardAnalytics, getSearchHistory } from "../services/searchService";
import { DashboardAnalytics, Document, SearchHistoryItem } from "../types";
import { formatRelativeAgo, parseApiDate } from "../utils/dateTime";

const SEARCH_COMPLETED_EVENT = "searchCompleted";

export default function DashboardPage() {
  const location = useLocation();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [history, setHistory] = useState<SearchHistoryItem[]>([]);
  const [analytics, setAnalytics] = useState<DashboardAnalytics>({
    most_searched_queries: [],
    top_documents: [],
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [lastUpdated, setLastUpdated] = useState<Date>(new Date());
  const [chartEpoch, setChartEpoch] = useState(0);

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [docs, searches, analyticsResponse] = await Promise.all([
        getDocuments(),
        getSearchHistory(),
        getDashboardAnalytics(),
      ]);
      setDocuments(docs);
      setHistory(searches);
      setAnalytics(analyticsResponse);
      setLastUpdated(new Date());
      setChartEpoch((n) => n + 1);
      console.log("📊 Dashboard data loaded", {
        queries: analyticsResponse.most_searched_queries,
        docs: analyticsResponse.top_documents,
      });
    } catch (err) {
      setError("Unable to load dashboard data.");
      console.error("Dashboard load error", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (location.pathname === "/") {
      void loadDashboard();
    }
  }, [location.pathname, loadDashboard]);

  useEffect(() => {
    const handleSearchCompleted = () => {
      setTimeout(() => {
        void loadDashboard();
      }, 600);
    };
    window.addEventListener(SEARCH_COMPLETED_EVENT, handleSearchCompleted);
    return () => window.removeEventListener(SEARCH_COMPLETED_EVENT, handleSearchCompleted);
  }, [loadDashboard]);

  const formatSearchHistoryLine = (dateStr: string) => {
    try {
      const date = parseApiDate(dateStr);
      if (Number.isNaN(date.getTime())) return "Unknown";
      const when = date.toLocaleString(undefined, {
        day: "numeric",
        month: "short",
        year: "numeric",
        hour: "numeric",
        minute: "2-digit",
      });
      return `${when} · ${formatRelativeAgo(date)}`;
    } catch {
      return "Unknown";
    }
  };

  return (
    <section className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-2xl font-semibold text-slate-800">Dashboard</h2>
          <p className="text-sm text-slate-500">Usage trends and most valuable knowledge assets.</p>
        </div>
        <div className="flex shrink-0 items-center gap-3">
          <Button
            type="button"
            variant="secondary"
            className="px-3 py-1.5 text-xs"
            onClick={() => void loadDashboard()}
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} aria-hidden />
            Refresh
          </Button>
          <p className="text-right text-2xs font-medium text-slate-500">
            Updated: <span className="text-slate-700">{lastUpdated.toLocaleTimeString()}</span>
          </p>
        </div>
      </div>

      {loading && (
        <div className="grid gap-4 md:grid-cols-2">
          <Skeleton className="h-72 w-full" />
          <Skeleton className="h-72 w-full" />
          <Skeleton className="h-40 w-full md:col-span-2" />
        </div>
      )}
      {error && <p className="text-sm text-red-600">{error}</p>}
      {!loading && !error && (
        <div className="grid gap-4 md:grid-cols-2">
          <Card title="Most searched queries">
            <div className="h-64">
              {analytics.most_searched_queries.length === 0 ? (
                <div className="flex h-full items-center justify-center">
                  <p className="text-sm text-slate-500">No search data yet</p>
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart key={`q-${chartEpoch}`} data={analytics.most_searched_queries}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="label" hide />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#4f46e5" isAnimationActive={false} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </Card>

          <Card title="Top documents">
            <div className="h-64">
              {analytics.top_documents.length === 0 ? (
                <div className="flex h-full items-center justify-center">
                  <p className="text-sm text-slate-500">No document access data yet</p>
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart key={`d-${chartEpoch}`} data={analytics.top_documents}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="label" hide />
                    <YAxis allowDecimals={false} />
                    <Tooltip />
                    <Bar dataKey="count" fill="#0ea5e9" isAnimationActive={false} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </Card>

          <Card title="Recent searches" className="md:col-span-2">
            <div className="space-y-2 text-sm text-slate-600">
              {history.length === 0 && (
                <EmptyState
                  icon={<SearchIcon size={18} />}
                  title="No recent searches"
                  description="Start searching documents to generate usage insights."
                />
              )}
              <div className="max-h-96 space-y-2 overflow-y-auto">
                {history.map((item) => (
                  <div key={item.id} className="rounded-lg border border-slate-100 bg-slate-50 p-3">
                    <p className="text-sm font-medium text-slate-700">{item.query_text}</p>
                    <p className="mt-1 text-2xs text-slate-500">🕐 {formatSearchHistoryLine(item.created_at)}</p>
                  </div>
                ))}
              </div>
            </div>
          </Card>

          <Card title="Documents in department scope" className="md:col-span-2">
            <div className="grid gap-2 text-sm text-slate-600 md:grid-cols-2">
              {documents.length === 0 && (
                <EmptyState
                  icon={<FileText size={18} />}
                  title="No documents available"
                  description="Upload docs to start building your knowledge base."
                />
              )}
              {documents.map((doc) => (
                <div key={doc.id} className="flex items-start justify-between gap-2 rounded-lg bg-slate-50 p-2">
                  <div className="min-w-0 flex-1">
                    <p className="font-medium text-slate-700">{doc.title}</p>
                    <p className="text-xs text-slate-500">
                      {doc.category} • {doc.source}
                    </p>
                  </div>
                  <button
                    type="button"
                    className="shrink-0 rounded-lg border border-slate-200 bg-white p-1.5 text-slate-600 hover:bg-slate-100"
                    title="Download"
                    onClick={() =>
                      void downloadDocument(doc.id, doc.title, {
                        fileType: doc.file_type,
                        fileName: doc.file_name,
                      })
                    }
                  >
                    <Download size={16} aria-hidden />
                  </button>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}
    </section>
  );
}
