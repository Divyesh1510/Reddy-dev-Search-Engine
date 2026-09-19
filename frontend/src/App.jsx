import React, { useState, useEffect } from 'react';
import { Search, Sparkles, Activity, PlusCircle, Clock, ChevronLeft, ChevronRight, AlertTriangle } from 'lucide-react';
import SearchBar from './components/SearchBar';
import SearchResultItem from './components/SearchResultItem';
import CrawlerModal from './components/CrawlerModal';
import StatsModal from './components/StatsModal';
import { API_BASE_URL } from './config';

export default function App() {
  const [query, setQuery] = useState('');
  const [mode, setMode] = useState('hybrid');
  const [selectedDomain, setSelectedDomain] = useState(null);
  const [page, setPage] = useState(1);
  const [pageSize] = useState(10);

  const [results, setResults] = useState([]);
  const [totalResults, setTotalResults] = useState(0);
  const [latencyMs, setLatencyMs] = useState(0);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);

  const [isCrawlerOpen, setIsCrawlerOpen] = useState(false);
  const [isStatsOpen, setIsStatsOpen] = useState(false);

  const executeSearch = async (searchQuery, searchPage = 1, currentMode = mode, domain = selectedDomain) => {
    if (!searchQuery.trim()) return;

    setLoading(true);
    setHasSearched(true);
    try {
      let url = `${API_BASE_URL}/search?q=${encodeURIComponent(searchQuery)}&mode=${currentMode}&page=${searchPage}&page_size=${pageSize}`;
      if (domain) {
        url += `&domain=${encodeURIComponent(domain)}`;
      }

      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setResults(data.results || []);
        setTotalResults(data.total_results || 0);
        setLatencyMs(data.latency_ms || 0);
        setPage(data.page || 1);
      } else {
        setResults([]);
        setTotalResults(0);
      }
    } catch (err) {
      console.error('Search request failed', err);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (newQuery) => {
    setPage(1);
    executeSearch(newQuery, 1, mode, selectedDomain);
  };

  const handleModeChange = (newMode) => {
    setMode(newMode);
    if (query.trim()) {
      executeSearch(query, 1, newMode, selectedDomain);
    }
  };

  const handleFilterDomain = (domain) => {
    setSelectedDomain(domain);
    if (query.trim()) {
      executeSearch(query, 1, mode, domain);
    }
  };

  const handleClearDomain = () => {
    setSelectedDomain(null);
    if (query.trim()) {
      executeSearch(query, 1, mode, null);
    }
  };

  const handlePageChange = (newPage) => {
    executeSearch(query, newPage, mode, selectedDomain);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const totalPages = Math.ceil(totalResults / pageSize);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans selection:bg-sky-500/30">
      {/* Top Navigation */}
      <header className="border-b border-slate-900 bg-slate-950/80 backdrop-blur-md sticky top-0 z-40 px-6 py-3.5 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center shadow-md shadow-sky-500/20">
            <Sparkles className="w-4 h-4 text-white" />
          </div>
          <div>
            <h1 className="text-base font-bold bg-gradient-to-r from-sky-400 via-indigo-300 to-white bg-clip-text text-transparent">
              Vortex Engine
            </h1>
            <p className="text-[10px] text-slate-500 font-mono">Hybrid Lexical & Vector Search</p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={() => setIsCrawlerOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-300 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-xl transition-all shadow-sm"
          >
            <PlusCircle className="w-3.5 h-3.5 text-sky-400" />
            <span>Crawl URLs</span>
          </button>

          <button
            onClick={() => setIsStatsOpen(true)}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-300 bg-slate-900 hover:bg-slate-800 border border-slate-800 rounded-xl transition-all shadow-sm"
          >
            <Activity className="w-3.5 h-3.5 text-emerald-400" />
            <span>Dashboard</span>
          </button>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-4xl w-full mx-auto px-4 py-8 flex flex-col">
        {/* Search Hero */}
        <SearchBar
          query={query}
          setQuery={setQuery}
          onSearch={handleSearch}
          mode={mode}
          setMode={handleModeChange}
          selectedDomain={selectedDomain}
          setSelectedDomain={handleClearDomain}
        />

        {/* Results Metadata Bar */}
        {hasSearched && (
          <div className="flex items-center justify-between text-xs text-slate-400 mb-4 px-2">
            <div className="flex items-center gap-2">
              <span className="font-semibold text-slate-200">
                Found {totalResults} result{totalResults === 1 ? '' : 's'}
              </span>
              <span className="text-slate-600">&bull;</span>
              <span className="flex items-center gap-1 text-sky-400">
                <Clock className="w-3 h-3" /> {latencyMs} ms
              </span>
            </div>
            <div className="text-[11px] text-slate-500 font-mono">
              Page {page} of {Math.max(1, totalPages)}
            </div>
          </div>
        )}

        {/* Results List */}
        <div className="space-y-3.5 flex-1">
          {loading ? (
            <div className="py-20 flex flex-col items-center justify-center text-slate-500">
              <div className="w-8 h-8 border-2 border-sky-500/30 border-t-sky-500 rounded-full animate-spin mb-3" />
              <p className="text-sm">Executing retrieval across BM25 & dense index...</p>
            </div>
          ) : results.length > 0 ? (
            results.map((item) => (
              <SearchResultItem
                key={item.chunk_id || item.id}
                item={item}
                onFilterDomain={handleFilterDomain}
              />
            ))
          ) : hasSearched ? (
            <div className="py-16 text-center text-slate-500 bg-slate-900/20 border border-slate-800/60 rounded-2xl p-8">
              <p className="text-base font-semibold text-slate-300 mb-1">No matching documents found</p>
              <p className="text-xs text-slate-500">
                Try searching for technical keywords like "FastAPI", "SQLite FTS5", "Kubernetes", "ChromaDB", or trigger a crawl.
              </p>
            </div>
          ) : (
            <div className="py-16 text-center text-slate-500">
              <p className="text-sm text-slate-400 mb-2">
                Search queries are evaluated with reciprocal rank fusion (BM25 + all-MiniLM-L6-v2)
              </p>
              <div className="flex flex-wrap justify-center gap-2 text-xs">
                {['FastAPI', 'SQLite BM25', 'Reciprocal Rank Fusion', 'ChromaDB', 'Kubernetes', 'Docker'].map((term) => (
                  <button
                    key={term}
                    onClick={() => {
                      setQuery(term);
                      executeSearch(term, 1, mode, selectedDomain);
                    }}
                    className="bg-slate-900 hover:bg-slate-800 text-sky-400/90 border border-slate-800 px-3 py-1 rounded-lg transition-colors"
                  >
                    {term}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Pagination Controls */}
        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-2 mt-8 pt-4 border-t border-slate-900">
            <button
              onClick={() => handlePageChange(page - 1)}
              disabled={page <= 1}
              className="flex items-center gap-1 px-3 py-1.5 text-xs text-slate-300 bg-slate-900 border border-slate-800 rounded-lg hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              <ChevronLeft className="w-3.5 h-3.5" /> Previous
            </button>
            <span className="text-xs text-slate-400 px-3 font-mono">
              {page} / {totalPages}
            </span>
            <button
              onClick={() => handlePageChange(page + 1)}
              disabled={page >= totalPages}
              className="flex items-center gap-1 px-3 py-1.5 text-xs text-slate-300 bg-slate-900 border border-slate-800 rounded-lg hover:bg-slate-800 disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Next <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900/80 py-4 px-6 text-center text-xs text-slate-600">
        Modular Hybrid Search Engine &bull; FastAPI &bull; SQLite FTS5 &bull; ChromaDB &bull; React
      </footer>

      {/* Modals */}
      <CrawlerModal
        isOpen={isCrawlerOpen}
        onClose={() => setIsCrawlerOpen(false)}
        onCrawlComplete={() => {
          if (query.trim()) {
            executeSearch(query, page, mode, selectedDomain);
          }
        }}
      />
      <StatsModal
        isOpen={isStatsOpen}
        onClose={() => setIsStatsOpen(false)}
      />
    </div>
  );
}
