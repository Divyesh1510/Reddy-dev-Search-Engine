import React from 'react';
import { ExternalLink, Hash, Award, Clock } from 'lucide-react';

export default function SearchResultItem({ item, onFilterDomain }) {
  return (
    <article className="group bg-slate-900/40 hover:bg-slate-900/80 border border-slate-800/80 hover:border-slate-700/80 rounded-2xl p-5 transition-all duration-200 shadow-sm hover:shadow-lg">
      <div className="flex flex-wrap items-center justify-between gap-2 mb-1.5 text-xs">
        <div className="flex items-center gap-2">
          <button
            onClick={() => onFilterDomain(item.domain)}
            className="text-sky-400 font-medium hover:underline flex items-center gap-1"
          >
            {item.domain}
          </button>
          <span className="text-slate-600">&bull;</span>
          <span className="text-slate-400 truncate max-w-sm">{item.url}</span>
        </div>

        <div className="flex items-center gap-2">
          {item.lexical_rank && (
            <span className="text-[10px] font-mono bg-slate-800 text-amber-300 px-1.5 py-0.5 rounded border border-slate-700">
              BM25 #{item.lexical_rank}
            </span>
          )}
          {item.semantic_rank && (
            <span className="text-[10px] font-mono bg-slate-800 text-indigo-300 px-1.5 py-0.5 rounded border border-slate-700">
              Dense #{item.semantic_rank}
            </span>
          )}
          <span className="text-[11px] font-semibold bg-sky-950/60 text-sky-400 px-2 py-0.5 rounded-full border border-sky-800/40">
            Score: {item.score}
          </span>
        </div>
      </div>

      <h3 className="text-lg font-semibold text-slate-100 group-hover:text-sky-400 transition-colors mb-2">
        <a
          href={item.url}
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-1.5 hover:underline"
        >
          {item.title}
          <ExternalLink className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity text-slate-400" />
        </a>
      </h3>

      <div
        className="text-sm text-slate-300 leading-relaxed font-normal [&>mark]:bg-sky-500/25 [&>mark]:text-sky-200 [&>mark]:px-1 [&>mark]:rounded"
        dangerouslySetInnerHTML={{ __html: item.snippet }}
      />
    </article>
  );
}
