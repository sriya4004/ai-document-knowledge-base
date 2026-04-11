import { Download, FileText, Sparkles } from "lucide-react";
import { downloadDocument } from "../services/documentService";
import { SourceChunk } from "../types";
import EmptyState from "./ui/EmptyState";
import Skeleton from "./ui/Skeleton";

type Props = {
  results: SourceChunk[];
  answer?: string;
  isLoading?: boolean;
  /** True after the user has run at least one search (distinguishes idle vs zero-hit). */
  hasSearched?: boolean;
};

function metadataText(value: unknown): string {
  if (value === null || value === undefined) return "-";
  return String(value);
}

function displayTitle(result: SourceChunk): string {
  const t = result.title?.trim();
  if (t) return t;
  return metadataText(result.metadata.title);
}

function displayCategory(result: SourceChunk): string {
  const c = result.category?.trim();
  if (c) return c;
  return metadataText(result.metadata.category);
}

function displaySnippet(result: SourceChunk): string {
  const s = result.snippet?.trim();
  if (s) return s;
  const legacy = result.content?.trim();
  if (legacy) return legacy;
  return "No preview content returned.";
}

/** Chroma / API metadata: skip placeholders used when a field is absent. */
function downloadMetaHint(
  metadata: Record<string, string | number | boolean | null>,
  key: string
): string | undefined {
  const raw = metadata[key];
  if (raw === null || raw === undefined) return undefined;
  const s = String(raw).trim();
  if (!s || s === "-" || s.toLowerCase() === "unknown") return undefined;
  return s;
}

export default function SearchResults({ results, answer, isLoading = false, hasSearched = false }: Props) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="rounded-2xl border border-slate-200/80 bg-white p-6 shadow-card">
          <Skeleton className="mb-4 h-5 w-2/5 max-w-[200px]" />
          <Skeleton className="h-24 w-full rounded-xl" />
        </div>
        <div className="space-y-3">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className="animate-fade-in-up rounded-2xl border border-slate-200/60 bg-white p-5 opacity-0 shadow-card"
              style={{ animationDelay: `${120 + i * 70}ms` }}
            >
              <Skeleton className="mb-3 h-4 w-3/5 max-w-xs" />
              <Skeleton className="mb-2 h-3 w-full" />
              <Skeleton className="h-3 w-11/12 max-w-full" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!results.length) {
    return (
      <EmptyState
        title={hasSearched ? "No results found" : "No results yet"}
        description={
          hasSearched
            ? "Try different keywords, or ask an admin to upload documents for your department."
            : "Try a natural-language question, or confirm documents are uploaded and indexed."
        }
        icon={<FileText className="h-5 w-5" strokeWidth={1.75} />}
      />
    );
  }

  const seenIds = new Set<number>();
  const uniqueResults = results.filter((result) => {
    const id = result.document_id;
    if (typeof id !== "number" || !Number.isFinite(id) || id <= 0 || seenIds.has(id)) {
      return false;
    }
    seenIds.add(id);
    return true;
  });

  if (uniqueResults.length === 0) {
    return (
      <EmptyState
        title="No results found"
        description="The server returned matches we could not display. Try again or contact an administrator."
        icon={<FileText className="h-5 w-5" strokeWidth={1.75} />}
      />
    );
  }

  // Show warning if backend didn't deduplicate properly
  if (uniqueResults.length < results.length) {
    console.warn(
      `Deduplication: removed ${results.length - uniqueResults.length} duplicate(s)`,
      { original: results.length, unique: uniqueResults.length }
    );
  }

  return (
    <section className="space-y-8">
      {answer ? (
        <div
          className="animate-fade-in-up relative overflow-hidden rounded-2xl border border-slate-200/80 bg-white opacity-0 shadow-card"
          style={{ animationDelay: "40ms" }}
        >
          <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-brand-400/50 to-transparent" />
          <div className="p-6 sm:p-7">
            <div className="mb-4 flex items-center gap-2.5">
              <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand-500 to-violet-600 text-white shadow-sm">
                <Sparkles className="h-4 w-4" strokeWidth={2} aria-hidden />
              </span>
              <div>
                <h2 className="text-sm font-semibold tracking-tight text-slate-900">Summary</h2>
                <p className="text-2xs font-medium uppercase tracking-wider text-slate-500">AI-generated from top sources</p>
              </div>
            </div>
            <p className="text-[0.9375rem] font-normal leading-relaxed tracking-tight text-slate-700">{answer}</p>
          </div>
        </div>
      ) : null}

      <div>
        <div className="animate-fade-in-up mb-4 flex items-baseline justify-between gap-4 opacity-0" style={{ animationDelay: "100ms" }}>
          <h2 className="text-lg font-bold tracking-tight text-slate-900">Sources</h2>
          <span className="rounded-full bg-slate-100 px-2.5 py-0.5 text-2xs font-semibold tabular-nums text-slate-600">
            {uniqueResults.length} {uniqueResults.length === 1 ? "match" : "matches"}
          </span>
        </div>

        <ul className="space-y-3">
          {uniqueResults.map((result, index) => (
            <li
              key={`${result.document_id}-${index}`}
              className="animate-fade-in-up opacity-0"
              style={{ animationDelay: `${140 + Math.min(index, 6) * 55}ms` }}
            >
              <article className="group rounded-2xl border border-slate-200/70 bg-white p-5 shadow-card transition-all duration-300 ease-out hover:border-slate-300/90 hover:shadow-card-hover sm:p-6">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="text-base font-semibold leading-snug tracking-tight text-slate-900">
                        {displayTitle(result)}
                      </h3>
                      <span className="inline-flex items-center rounded-full bg-brand-50 px-2 py-0.5 text-2xs font-semibold text-brand-700 ring-1 ring-brand-100/80">
                        {displayCategory(result)}
                      </span>
                    </div>
                    <p className="mt-2 text-2xs font-medium text-slate-500">
                      Document <span className="tabular-nums text-slate-600">#{result.document_id}</span>
                      <span className="mx-1.5 text-slate-300">·</span>
                      {metadataText(result.metadata.source)}
                      <span className="mx-1.5 text-slate-300">·</span>
                      <span className="tabular-nums">Score {(result.score * 100).toFixed(1)}%</span>
                    </p>
                  </div>
                  <button
                    type="button"
                    className="inline-flex shrink-0 items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-2 text-2xs font-semibold text-slate-700 shadow-sm transition-all duration-200 hover:border-brand-200 hover:bg-brand-50/50 hover:text-brand-700 active:scale-[0.98]"
                    onClick={() =>
                      void downloadDocument(result.document_id, displayTitle(result), {
                        fileType: downloadMetaHint(result.metadata, "file_type"),
                        fileName: downloadMetaHint(result.metadata, "file_name"),
                      })
                    }
                  >
                    <Download className="h-3.5 w-3.5" strokeWidth={2} aria-hidden />
                    Download
                  </button>
                </div>
                <p className="mt-4 border-t border-slate-100 pt-4 text-sm leading-relaxed tracking-tight text-slate-600">
                  {displaySnippet(result)}
                </p>
              </article>
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
