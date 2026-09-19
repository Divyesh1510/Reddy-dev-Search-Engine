import React, { useState, useEffect } from 'react';
import { Send, RefreshCw, CheckCircle, AlertCircle, Clock, Globe } from 'lucide-react';
import { API_BASE_URL } from '../config';

export default function CrawlerModal({ isOpen, onClose, onCrawlComplete }) {
  const [urlsInput, setUrlsInput] = useState('');
  const [maxPages, setMaxPages] = useState(10);
  const [activeJobId, setActiveJobId] = useState(null);
  const [jobStatus, setJobStatus] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Status Polling
  useEffect(() => {
    if (!activeJobId) return;

    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/crawl/status/${activeJobId}`);
        if (res.ok) {
          const data = await res.json();
          setJobStatus(data);
          if (data.status === 'completed' || data.status === 'failed') {
            clearInterval(interval);
            if (data.status === 'completed' && onCrawlComplete) {
              onCrawlComplete();
            }
          }
        }
      } catch (err) {
        console.error('Error polling crawl status', err);
      }
    }, 1200);

    return () => clearInterval(interval);
  }, [activeJobId, onCrawlComplete]);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    const urls = urlsInput
      .split('\n')
      .map((u) => u.trim())
      .filter((u) => u.length > 0);

    if (urls.length === 0) {
      setErrorMessage('Please enter at least one URL.');
      return;
    }

    setIsSubmitting(true);
    try {
      const res = await fetch(`${API_BASE_URL}/crawl`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          urls,
          max_pages: parseInt(maxPages, 10),
          rate_limit_delay: 0.5,
        }),
      });

      if (res.status === 202) {
        const data = await res.json();
        setActiveJobId(data.job_id);
        setJobStatus({
          job_id: data.job_id,
          status: 'queued',
          pages_crawled: 0,
          chunks_indexed: 0,
        });
      } else {
        const errorData = await res.json();
        setErrorMessage(errorData.detail || 'Failed to submit crawl job.');
      }
    } catch (err) {
      setErrorMessage('Network error: unable to reach crawler endpoint.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm animate-fade-in">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg shadow-2xl p-6 text-slate-100 relative">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-4">
          <div className="flex items-center gap-2">
            <Globe className="w-5 h-5 text-sky-400" />
            <h2 className="text-lg font-semibold">Web Crawler & Ingestion</h2>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-100 text-sm px-2 py-1 rounded-lg bg-slate-800"
          >
            &times;
          </button>
        </div>

        {errorMessage && (
          <div className="mb-4 p-3 bg-red-950/50 border border-red-800/60 rounded-xl text-red-300 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        {!activeJobId ? (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-medium text-slate-400 mb-1">
                Seed URLs (one per line)
              </label>
              <textarea
                rows={4}
                value={urlsInput}
                onChange={(e) => setUrlsInput(e.target.value)}
                placeholder="https://example.com/docs&#10;https://python.org"
                className="w-full bg-slate-950 border border-slate-800 rounded-xl p-3 text-sm text-slate-200 focus:outline-none focus:border-sky-500 font-mono"
              />
            </div>

            <div className="flex items-center gap-4">
              <div className="flex-1">
                <label className="block text-xs font-medium text-slate-400 mb-1">
                  Max Pages
                </label>
                <input
                  type="number"
                  min="1"
                  max="50"
                  value={maxPages}
                  onChange={(e) => setMaxPages(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-sky-500"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white font-medium py-2.5 rounded-xl text-sm transition-all shadow-md shadow-sky-500/20 flex items-center justify-center gap-2"
            >
              {isSubmitting ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" /> Submitting...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" /> Start Ingestion Job
                </>
              )}
            </button>
          </form>
        ) : (
          <div className="space-y-4 py-2">
            <div className="p-4 bg-slate-950 border border-slate-800 rounded-xl space-y-3">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">Job ID:</span>
                <span className="font-mono text-slate-300">{jobStatus?.job_id}</span>
              </div>

              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-400">Status:</span>
                <span
                  className={`font-semibold uppercase tracking-wider px-2 py-0.5 rounded-full text-[10px] ${
                    jobStatus?.status === 'completed'
                      ? 'bg-emerald-950/80 text-emerald-400 border border-emerald-800/50'
                      : jobStatus?.status === 'failed'
                      ? 'bg-red-950/80 text-red-400 border border-red-800/50'
                      : 'bg-sky-950/80 text-sky-400 border border-sky-800/50'
                  }`}
                >
                  {jobStatus?.status}
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-2">
                <div className="bg-slate-900/60 p-2.5 rounded-lg border border-slate-800 text-center">
                  <div className="text-xs text-slate-400">Pages Crawled</div>
                  <div className="text-xl font-bold text-sky-400">
                    {jobStatus?.pages_crawled ?? 0}
                  </div>
                </div>
                <div className="bg-slate-900/60 p-2.5 rounded-lg border border-slate-800 text-center">
                  <div className="text-xs text-slate-400">Chunks Indexed</div>
                  <div className="text-xl font-bold text-emerald-400">
                    {jobStatus?.chunks_indexed ?? 0}
                  </div>
                </div>
              </div>

              {jobStatus?.status === 'running' && (
                <div className="flex items-center justify-center gap-2 text-xs text-sky-400 pt-2">
                  <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                  <span>Crawling & indexing in background...</span>
                </div>
              )}

              {jobStatus?.status === 'completed' && (
                <div className="flex items-center justify-center gap-2 text-xs text-emerald-400 pt-2">
                  <CheckCircle className="w-4 h-4" />
                  <span>Ingestion finished successfully!</span>
                </div>
              )}
            </div>

            {jobStatus?.status === 'completed' || jobStatus?.status === 'failed' ? (
              <button
                onClick={() => {
                  setActiveJobId(null);
                  setJobStatus(null);
                  setUrlsInput('');
                }}
                className="w-full bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium py-2 rounded-xl text-sm transition-all"
              >
                Crawl More URLs
              </button>
            ) : null}
          </div>
        )}
      </div>
    </div>
  );
}
