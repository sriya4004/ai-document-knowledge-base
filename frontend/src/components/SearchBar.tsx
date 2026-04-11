import { FormEvent } from "react";
import { Search } from "lucide-react";
import Button from "./ui/Button";

type Props = {
  query: string;
  onQueryChange: (value: string) => void;
  onSearch: () => void;
  isLoading?: boolean;
};

export default function SearchBar({ query, onQueryChange, onSearch, isLoading = false }: Props) {
  const submit = (event: FormEvent) => {
    event.preventDefault();
    onSearch();
  };

  return (
    <form onSubmit={submit} className="relative">
      <div className="rounded-2xl bg-gradient-to-br from-brand-500/15 via-violet-500/10 to-slate-200/40 p-[1px] shadow-glow transition-shadow duration-300 hover:shadow-card-hover">
        <div className="rounded-[15px] bg-white/95 p-2 shadow-card backdrop-blur-sm sm:p-2.5">
          <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:gap-3">
            <div className="group relative min-w-0 flex-1">
              <Search
                className="pointer-events-none absolute left-4 top-1/2 h-[1.125rem] w-[1.125rem] -translate-y-1/2 text-slate-400 transition-colors duration-200 group-focus-within:text-brand-600"
                strokeWidth={2}
                aria-hidden
              />
              <input
                type="search"
                enterKeyHint="search"
                autoComplete="off"
                placeholder="Ask anything about your documents…"
                value={query}
                onChange={(e) => onQueryChange(e.target.value)}
                className="group w-full rounded-xl border border-slate-200/80 bg-slate-50/50 py-3.5 pl-11 pr-4 text-[0.9375rem] font-medium leading-snug text-slate-900 shadow-inner outline-none ring-0 transition-all duration-200 placeholder:font-normal placeholder:text-slate-400 focus:border-brand-200 focus:bg-white focus:shadow-sm focus:ring-2 focus:ring-brand-100"
              />
            </div>
            <Button
              type="submit"
              className="h-12 shrink-0 rounded-xl px-6 font-semibold shadow-sm transition-transform duration-200 active:scale-[0.98] sm:h-[3.25rem] sm:px-8"
              disabled={!query.trim()}
              isLoading={isLoading}
            >
              {isLoading ? "Searching…" : "Search"}
            </Button>
          </div>
          <p className="mt-2.5 px-1 text-center text-2xs font-medium text-slate-500 sm:px-3 sm:text-left">
            Returns up to <span className="text-slate-700">5</span> best-matching passages · Powered by embeddings
          </p>
        </div>
      </div>
    </form>
  );
}
