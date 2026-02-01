import React, { useState, useRef, useEffect, useCallback } from 'react';
import { ArrowLeft, Send, BadgeCheck } from 'lucide-react';
import { queryDocuments } from '../lib/api';
import type { SourceDoc } from '../types/api';
import { getErrorMessage, isTimeoutError } from '../types/api';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';

interface ChatInterfaceProps {
  filename: string;
  onBack: () => void;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ filename, onBack }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SourceDoc[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const inputRef = useRef<HTMLInputElement | null>(null);

  const handleSearch = useCallback(async () => {
    const q = query.trim();
    if (!q) return;
    setIsLoading(true);
    setError('');
    setResults([]);
    try {
      const res = await queryDocuments({ query: q }, { timeout: 60000 });
      setResults(res.sources || []);
    } catch (err: unknown) {
      setError(isTimeoutError(err)
        ? 'The server is taking too long. Please check your backend terminal.'
        : getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }, [query]);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !isLoading) handleSearch();
  };

  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  return (
    <div className="flex flex-col w-full max-w-2xl mx-auto min-h-[500px]">
      {/* Top Bar */}
      <div className="flex items-center border-b border-slate-200 px-4 py-3 bg-white rounded-t-xl">
        <button
          type="button"
          onClick={onBack}
          className="mr-3 p-1 rounded hover:bg-slate-100"
          aria-label="Back to upload"
        >
          <ArrowLeft size={22} />
        </button>
        <h2 className="font-semibold text-lg text-slate-700">Search: <span className="text-blue-600">{filename}</span></h2>
      </div>
      {/* Search Bar */}
      <div className="flex items-center gap-2 bg-white px-4 py-6 border-b border-slate-200">
        <input
          ref={inputRef}
          className="flex-1 text-lg px-4 py-3 rounded-lg border border-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-600 bg-slate-50"
          placeholder="Ask a question about this document..."
          value={query}
          onChange={e => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isLoading}
        />
        <button
          className={clsx(
            'ml-2 px-4 py-3 rounded-lg font-semibold text-white bg-blue-600 hover:bg-blue-700 transition',
            isLoading && 'opacity-60 cursor-not-allowed'
          )}
          onClick={handleSearch}
          disabled={isLoading}
        >
          <Send size={20} />
        </button>
      </div>
      {/* Results */}
      <div className="flex-1 overflow-y-auto p-6 bg-slate-50 space-y-6 rounded-b-xl">
        {error && (
          <div className="text-red-600 font-medium text-center">{error}</div>
        )}
        <AnimatePresence>
          {results.map((src, idx) => (
            <motion.div
              key={src.id || idx}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
              transition={{ duration: 0.25, delay: idx * 0.07 }}
              className="bg-white border border-slate-200 rounded-xl shadow-sm p-6 flex flex-col gap-2"
            >
              <div className="flex items-center gap-2 mb-1">
                <span className="text-xs font-semibold text-slate-500">Result #{idx + 1}</span>
                {src.score !== undefined && (
                  <span className="ml-2 inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold bg-green-100 text-green-700">
                    <BadgeCheck size={14} className="text-green-500" />
                    {Math.round(src.score * 100)}% Match
                  </span>
                )}
              </div>
              <div className="text-base text-slate-800 leading-relaxed whitespace-pre-line">
                {src.text}
              </div>
              <div className="flex gap-4 text-xs text-slate-500 mt-2">
                {src.metadata?.page_number && (
                  <span>Page {src.metadata.page_number}</span>
                )}
                {src.metadata?.filename && (
                  <span>{src.metadata.filename}</span>
                )}
                {src.metadata?.chunk_index !== undefined && (
                  <span>Chunk {src.metadata.chunk_index}</span>
                )}
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
        {!isLoading && results.length === 0 && !error && (
          <div className="text-slate-400 text-center mt-12">No results yet. Try searching for something!</div>
        )}
        {isLoading && (
          <div className="text-blue-600 text-center font-medium mt-12 animate-pulse">Searching...</div>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;
