import { useState } from "react";
import toast from "react-hot-toast";
import SearchBar from "../components/SearchBar";
import SearchResults from "../components/SearchResults";
import { askQuestion } from "../services/searchService";
import { SourceChunk } from "../types";

// Custom event to notify dashboard of new search
export const SEARCH_COMPLETED_EVENT = "searchCompleted";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [answer, setAnswer] = useState("");
  const [results, setResults] = useState<SourceChunk[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) {
      toast.error("Please enter a search query");
      return;
    }

    // Clear previous search state before new search
    setError("");
    setResults([]);
    setAnswer("");
    setIsLoading(true);

    try {
      const response = await askQuestion(query.trim(), 5);

      if (!response || typeof response !== "object") {
        throw new Error("Invalid response format");
      }

      const uniqueSources = response.sources || [];
      setResults(uniqueSources);
      setAnswer(response.answer || "");
      setHasSearched(true);

      window.dispatchEvent(
        new CustomEvent(SEARCH_COMPLETED_EVENT, {
          detail: { query: query.trim(), resultCount: uniqueSources.length },
        })
      );

      if (uniqueSources.length === 0) {
        toast("No results found for your search. Try different keywords.");
      }
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : "Search failed. Please try again.";
      setError(errorMsg);
      setResults([]);
      setAnswer("");
      toast.error(errorMsg);
      console.error("Search error:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section className="mx-auto max-w-3xl px-1 pb-12 pt-2 sm:px-0">
      <header className="animate-fade-in mb-10 text-center sm:mb-12">
        <p className="mb-2 text-2xs font-semibold uppercase tracking-[0.2em] text-brand-600">Knowledge base</p>
        <h1 className="text-balance text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
          Find answers across your documents
        </h1>
        <p className="mx-auto mt-3 max-w-lg text-pretty text-sm leading-relaxed text-slate-600 sm:text-base">
          Semantic search returns the five most relevant passages with context-aware ranking.
        </p>
      </header>

      <div className="animate-fade-in-up opacity-0" style={{ animationDelay: "80ms" }}>
        <SearchBar query={query} onQueryChange={setQuery} onSearch={handleSearch} isLoading={isLoading} />
      </div>

      {error && (
        <div
          className="animate-fade-in mt-6 rounded-2xl border border-red-200/90 bg-red-50/95 px-4 py-3 text-center text-sm font-medium text-red-800 shadow-sm backdrop-blur-sm"
          role="alert"
        >
          {error}
        </div>
      )}

      <div className="mt-10">
        <SearchResults results={results} answer={answer} isLoading={isLoading} hasSearched={hasSearched} />
      </div>
    </section>
  );
}
