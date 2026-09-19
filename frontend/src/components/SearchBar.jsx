import React, { useState, useEffect, useRef } from 'react';
import { Search, X, Sparkles, SlidersHorizontal, Globe } from 'lucide-react';
import { API_BASE_URL } from '../config';

export default function SearchBar({
  query,
  setQuery,
  onSearch,
  mode,
  setMode,
  selectedDomain,
  setSelectedDomain
}) {
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const wrapperRef = useRef(null);

  // Fetch auto-suggestions with debounce
  useEffect(() => {
    if (!query.trim() || query.length < 2) {
      setSuggestions([]);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/suggest?q=${encodeURIComponent(query)}`);
        if (res.ok) {
          const data = await res.json();
          setSuggestions(data.suggestions || []);
        }
      } catch (err) {
        // silent fallback for auto-suggest
      }
    }, 200);

    return () => clearTimeout(timer);
  }, [query]);

  // Click outside listener
  useEffect(() => {
    function handleClickOutside(event) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    setShowSuggestions(false);
    onSearch(query);
  };

  const handleSelectSuggestion = (item) => {
    setQuery(item);
    setShowSuggestions(false);
    onSearch(item);
  };

  return (
    <div className="w-full max-w-3xl mx-auto mb-6" ref={wrapperRef}>
      <form onSubmit={handleSubmit} className="relative">
        <div
          className={`flex items-center gap-3 bg-slate-900/90 border backdrop-blur-md rounded-2xl px-4 py-3 shadow-xl transition-all duration-300 ${
            isFocused
              ? 'border-sky-500/80 ring-2 ring-sky-500/20 shadow-sky-500/10'
              : 'border-slate-800 hover:border-slate-700'
          }`}
        >
          <Search className="w-5 h-5 text-slate-400 shrink-0" />
          <input
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setShowSuggestions(true);
            }}
            onFocus={() => {
              setIsFocused(true);
              setShowSuggestions(true);
            }}
            onBlur={() => setIsFocused(false)}
            placeholder="Search indexing architectures, databases, ML embeddings..."
            className="w-full bg-transparent text-slate-100 placeholder-slate-500 text-base focus:outline-none"
          />

          {query && (
            <button
              type="button"
              onClick={() => {
                setQuery('');
                setSuggestions([]);
              }}
              className="text-slate-400 hover:text-slate-200 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
          )}

          <button
            type="submit"
            className="bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white font-medium px-4 py-1.5 rounded-xl text-sm transition-all shadow-md shadow-sky-500/20 shrink-0"
          >
            Search
          </button>
        </div>

        {/* Auto Suggestions Dropdown */}
        {showSuggestions && suggestions.length > 0 && (
          <div className="absolute left-0 right-0 top-full mt-2 bg-slate-900/95 border border-slate-800 rounded-xl shadow-2xl backdrop-blur-lg overflow-hidden z-50 py-1">
            <div className="px-3 py-1.5 text-xs font-semibold text-slate-400 flex items-center gap-1.5 uppercase tracking-wider">
              <Sparkles className="w-3.5 h-3.5 text-sky-400" /> Suggestions
            </div>
            {suggestions.map((item, idx) => (
              <button
                key={idx}
                type="button"
                onMouseDown={() => handleSelectSuggestion(item)}
                className="w-full text-left px-4 py-2.5 text-sm text-slate-200 hover:bg-slate-800/80 hover:text-sky-300 transition-colors flex items-center justify-between"
              >
                <span>{item}</span>
                <span className="text-xs text-slate-500">Jump &rarr;</span>
              </button>
            ))}
          </div>
        )}
      </form>

      {/* Retrieval Mode & Domain Filters */}
      <div className="flex flex-wrap items-center justify-between gap-3 mt-3 px-2 text-xs">
        <div className="flex items-center gap-1.5 bg-slate-900/60 p-1 border border-slate-800/80 rounded-xl">
          <span className="text-slate-400 px-2 py-0.5 flex items-center gap-1">
            <SlidersHorizontal className="w-3 h-3" /> Mode:
          </span>
          {[
            { id: 'hybrid', label: 'Hybrid (RRF)' },
            { id: 'lexical', label: 'Lexical (BM25)' },
            { id: 'semantic', label: 'Semantic (Dense)' },
          ].map((m) => (
            <button
              key={m.id}
              onClick={() => setMode(m.id)}
              className={`px-2.5 py-1 rounded-lg transition-all font-medium ${
                mode === m.id
                  ? 'bg-sky-500/20 text-sky-300 border border-sky-500/40'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>

        {selectedDomain && (
          <div className="flex items-center gap-1.5 bg-slate-800 text-sky-300 px-2.5 py-1 rounded-lg border border-slate-700">
            <Globe className="w-3 h-3" />
            <span>domain: {selectedDomain}</span>
            <button
              onClick={() => setSelectedDomain(null)}
              className="text-slate-400 hover:text-slate-200 ml-1"
            >
              <X className="w-3 h-3" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
