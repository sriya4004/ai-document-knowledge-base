import { useEffect, useState } from "react";
import { History, RefreshCw } from "lucide-react";
import toast from "react-hot-toast";
import Button from "../components/ui/Button";
import Card from "../components/ui/Card";
import EmptyState from "../components/ui/EmptyState";
import Skeleton from "../components/ui/Skeleton";
import { getSearchHistory } from "../services/searchService";
import { SearchHistoryItem } from "../types";
import { formatRelativeAgo, parseApiDate } from "../utils/dateTime";

const SEARCH_COMPLETED_EVENT = "searchCompleted";

export default function HistoryPage() {
  const [history, setHistory] = useState<SearchHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadHistory = async () => {
    setLoading(true);
    setError("");
    try {
      const items = await getSearchHistory();
      setHistory(items);
    } catch {
      setError("Could not load search history.");
      toast.error("Failed to load history");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadHistory();
  }, []);

  // Listen for new searches and refresh history
  useEffect(() => {
    const handleSearchCompleted = () => {
      console.log("🔄 Search completed, refreshing history");
      setTimeout(() => {
        void loadHistory();
      }, 300);
    };

    window.addEventListener(SEARCH_COMPLETED_EVENT, handleSearchCompleted);
    return () => {
      window.removeEventListener(SEARCH_COMPLETED_EVENT, handleSearchCompleted);
    };
  }, []);

  const formatTimestamp = (dateStr: string) => {
    try {
      const date = parseApiDate(dateStr);
      if (Number.isNaN(date.getTime())) {
        return { relative: "Unknown", dateTime: "", full: "Unknown" };
      }
      const now = new Date();
      const relative = formatRelativeAgo(date, now);
      const dateTime = date.toLocaleString(undefined, {
        day: "numeric",
        month: "short",
        year: "numeric",
        hour: "numeric",
        minute: "2-digit",
      });
      return { relative, dateTime, full: date.toLocaleString() };
    } catch {
      return { relative: "Unknown", dateTime: "", full: "Unknown" };
    }
  };

  return (
    <section className="space-y-6">
      <div className="flex items-start justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-slate-800">Search History</h2>
          <p className="text-sm text-slate-500">Your latest 10 semantic queries with timestamps.</p>
        </div>
        <Button
          variant="secondary"
          className="shrink-0 px-3 py-1.5 text-xs"
          onClick={() => void loadHistory()}
          disabled={loading}
        >
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      <Card>
        {loading && (
          <div className="space-y-3">
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
            <Skeleton className="h-16 w-full" />
          </div>
        )}

        {!loading && error && <p className="text-sm text-red-600">{error}</p>}

        {!loading && !error && history.length === 0 && (
          <EmptyState
            icon={<History size={20} />}
            title="No recent searches"
            description="Run a few searches and they will appear here."
          />
        )}

        {!loading && !error && history.length > 0 && (
          <div className="space-y-3">
            {history.map((item) => {
              const timestamps = formatTimestamp(item.created_at);
              return (
                <article
                  key={item.id}
                  className="rounded-xl border border-slate-200 bg-white p-4 transition-colors hover:bg-slate-50"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-slate-900">{item.query_text}</p>
                      <p className="mt-1 text-2xs text-slate-500" title={timestamps.full}>
                        {timestamps.dateTime ? (
                          <>
                            <span className="font-medium text-slate-600">{timestamps.dateTime}</span>
                            <span className="mx-1.5 text-slate-300">·</span>
                          </>
                        ) : null}
                        <span>🕐 {timestamps.relative}</span>
                      </p>
                    </div>
                    <div className="shrink-0 text-right">
                      <p className="text-2xs font-medium text-slate-400"># {item.id}</p>
                    </div>
                  </div>
                </article>
              );
            })}
          </div>
        )}
      </Card>
    </section>
  );
}
