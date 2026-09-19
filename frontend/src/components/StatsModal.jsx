import React, { useState, useEffect } from 'react';
import { Activity, Database, HardDrive, Layers, RefreshCw } from 'lucide-react';
import { API_BASE_URL } from '../config';

export default function StatsModal({ isOpen, onClose }) {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/stats`);
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Failed to load stats', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (isOpen) {
      fetchStats();
    }
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-xl shadow-2xl p-6 text-slate-100 relative">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-5">
          <div className="flex items-center gap-2">
            <Activity className="w-5 h-5 text-emerald-400" />
            <h2 className="text-lg font-semibold">Engine & Indexing Dashboard</h2>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={fetchStats}
              className="text-slate-400 hover:text-slate-200 p-1.5 rounded-lg bg-slate-800"
              title="Refresh Stats"
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
            </button>
            <button
              onClick={onClose}
              className="text-slate-400 hover:text-slate-100 text-sm px-2.5 py-1 rounded-lg bg-slate-800"
            >
              &times;
            </button>
          </div>
        </div>

        {loading && !stats ? (
          <div className="py-12 flex items-center justify-center text-slate-400 text-sm">
            <RefreshCw className="w-5 h-5 animate-spin mr-2" /> Loading system metrics...
          </div>
        ) : (
          <div className="space-y-4">
            <div className="grid grid-cols-3 gap-3">
              <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl text-center">
                <div className="flex items-center justify-center gap-1.5 text-xs text-slate-400 mb-1">
                  <Database className="w-3.5 h-3.5 text-sky-400" /> Documents
                </div>
                <div className="text-2xl font-bold text-sky-400">
                  {stats?.index?.total_documents ?? 0}
                </div>
              </div>

              <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl text-center">
                <div className="flex items-center justify-center gap-1.5 text-xs text-slate-400 mb-1">
                  <Layers className="w-3.5 h-3.5 text-indigo-400" /> Total Chunks
                </div>
                <div className="text-2xl font-bold text-indigo-400">
                  {stats?.index?.total_fts_chunks ?? 0}
                </div>
              </div>

              <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl text-center">
                <div className="flex items-center justify-center gap-1.5 text-xs text-slate-400 mb-1">
                  <HardDrive className="w-3.5 h-3.5 text-emerald-400" /> Index Size
                </div>
                <div className="text-2xl font-bold text-emerald-400">
                  {stats?.storage?.total_mb ?? 0} MB
                </div>
              </div>
            </div>

            <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-2 text-xs">
              <div className="font-semibold text-slate-300 pb-1 border-b border-slate-800/80">
                Storage & Volume Details
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400">Persistent DATA_DIR:</span>
                <span className="font-mono text-slate-200">{stats?.storage?.data_dir}</span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400">SQLite FTS5 DB:</span>
                <span className="font-mono text-slate-200">
                  {Math.round((stats?.storage?.sqlite_bytes ?? 0) / 1024)} KB
                </span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400">ChromaDB Vector Store:</span>
                <span className="font-mono text-slate-200">
                  {Math.round((stats?.storage?.chroma_bytes ?? 0) / 1024)} KB
                </span>
              </div>
            </div>

            <div className="bg-slate-950 border border-slate-800 p-4 rounded-xl space-y-2 text-xs">
              <div className="font-semibold text-slate-300 pb-1 border-b border-slate-800/80">
                Crawler Status & Activity
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400">Active Crawl Jobs:</span>
                <span className="font-semibold text-emerald-400">
                  {stats?.crawler?.active_jobs_count ?? 0}
                </span>
              </div>
              <div className="flex justify-between py-1">
                <span className="text-slate-400">Recent Crawls Tracked:</span>
                <span className="text-slate-200">
                  {stats?.crawler?.recent_jobs?.length ?? 0}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
