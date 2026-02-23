import React from 'react';
import { Sun, Moon, Github, User } from 'lucide-react';
import ThemeToggle from './ThemeToggle';

// Fixed header with theme toggle, GitHub link, and user menu
export default function Header() {
  return (
    <header className="sticky top-0 h-16 w-full backdrop-blur-md bg-white/80 dark:bg-slate-950/80 border-b border-slate-200 dark:border-slate-800 z-40 flex items-center px-8 justify-between">
      <div className="flex items-center gap-3">
        <span className="font-extrabold text-xl tracking-tight text-slate-900 dark:text-white">DocSearch AI</span>
      </div>
      <div className="flex items-center gap-6">
        <ThemeToggle />
        <a href="https://github.com/" target="_blank" rel="noopener noreferrer" aria-label="GitHub" className="text-slate-400 hover:text-slate-900 dark:hover:text-white">
          <Github size={22} />
        </a>
        <div className="w-9 h-9 rounded-full bg-slate-200 dark:bg-slate-800 flex items-center justify-center">
          <User className="text-slate-500 dark:text-slate-400" size={20} />
        </div>
      </div>
    </header>
  );
}
