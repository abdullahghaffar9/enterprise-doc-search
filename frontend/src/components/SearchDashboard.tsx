import { useState } from 'react';
import { Search, Sparkles, FileText, ArrowRight } from 'lucide-react';
import { queryDocuments } from '../lib/api';
import { motion } from 'framer-motion';
import Typewriter from './Typewriter';

// RAG-powered document search interface with query input and results display
const SearchDashboard = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return; // Ignore empty or whitespace-only queries

    setIsLoading(true);
    setHasSearched(true);
    setErrorMsg('');
    try {
      const data = await queryDocuments({ query });
      setResults(data.sources || []);
    } catch (err) {
      setResults([]);
      setErrorMsg('Unable to fetch results. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-8">
      {/* SEARCH INPUT */}
      <form onSubmit={handleSearch} className="relative group">
        <div className="relative flex items-center bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-2xl shadow-xl shadow-blue-900/5 overflow-hidden transition-all focus-within:ring-1 focus-within:ring-blue-500">
          <Search className="ml-6 w-6 h-6 text-slate-400" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a question about your documents..."
            className="w-full p-6 bg-transparent border-none outline-none text-lg font-medium text-slate-900 dark:text-slate-100 placeholder:text-slate-400"
          />
          <button 
            type="submit"
            disabled={isLoading}
            className="mr-2 p-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-colors disabled:opacity-50"
          >
            {isLoading ? <Sparkles className="w-5 h-5 animate-spin" /> : <ArrowRight className="w-5 h-5" />}
          </button>
        </div>
      </form>

      {/* RESULTS GRID */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {results.map((source, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
            className="group relative bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-8 rounded-2xl hover:border-blue-500/50 transition-all shadow-xl shadow-blue-900/5"
          >
            <div className="flex justify-between items-start mb-4">
              <div className="flex items-center space-x-2">
                <div className="p-2 bg-slate-100 dark:bg-slate-800 rounded-lg">
                  <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                </div>
                <span className="text-sm font-semibold text-slate-900 dark:text-slate-100 tracking-wide">
                  Result {index + 1}
                </span>
              </div>
              <span className="px-4 py-1 text-xs font-bold text-blue-700 bg-blue-50 dark:text-blue-400 dark:bg-slate-800 rounded-full shadow">
                {(source.score * 100).toFixed(0)}% Match
              </span>
            </div>
            
            <p className="text-slate-600 dark:text-slate-400 font-normal leading-relaxed line-clamp-4">
              <Typewriter text={source.text?.slice(0, 300) || ''} speed={3} delay={index * 100} />
            </p>
          </motion.div>
        ))}
      </div>

      {errorMsg && (
        <div className="text-center text-red-500 dark:text-red-400 py-4">
          {errorMsg}
        </div>
      )}
      {!isLoading && hasSearched && results.length === 0 && !errorMsg && (
        <div className="text-center text-slate-500 dark:text-slate-400 py-12">
          No relevant documents found.
        </div>
      )}
    </div>
  );
};

export default SearchDashboard;