import React from 'react';
import { Command, Home, FileText, Settings, User } from 'lucide-react';
import clsx from 'clsx';
import ThemeToggle from './ThemeToggle';

// Top-level navigation items rendered in the sidebar menu
const navLinks = [
  { name: 'Home', icon: Home },
  { name: 'Documents', icon: FileText },
  { name: 'Settings', icon: Settings },
];

interface SidebarProps {
  open?: boolean;
  onClose?: () => void;
}

export default function Sidebar({ open = false, onClose }: SidebarProps) {
  const [active, setActive] = React.useState('Home');
  // Responsive: show as overlay on mobile
  return (
    <>
      {/* Backdrop for mobile overlay */}
      <div
        className={clsx(
          'fixed inset-0 bg-black/30 z-40 transition-opacity duration-300 md:hidden',
          open ? 'opacity-100 pointer-events-auto' : 'opacity-0 pointer-events-none'
        )}
        onClick={onClose}
        aria-hidden={!open}
      />
      <aside
        className={clsx(
          'h-screen w-64 bg-white/90 dark:bg-slate-950/90 border-r border-slate-100 dark:border-slate-900 flex flex-col justify-between fixed left-0 top-0 z-50 transition-transform duration-300',
          'transform md:translate-x-0',
          open ? 'translate-x-0' : '-translate-x-full',
          'md:translate-x-0 md:static md:block',
          'shadow-none'
        )}
        aria-label="Sidebar"
        tabIndex={-1}
      >
        <div>
          <div className="flex items-center gap-3 px-7 py-7">
            <Command className="text-brand-500" size={28} />
            <span className="font-bold text-xl tracking-tight text-slate-900 dark:text-white">DocuPro</span>
            {/* Close button on mobile */}
            <button
              className="ml-auto md:hidden p-2 rounded focus:outline-none focus:ring-2 focus:ring-brand-500 hover:bg-slate-100 dark:hover:bg-slate-800"
              onClick={onClose}
              aria-label="Close menu"
            >
              <svg width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>
            </button>
          </div>
          <nav className="mt-10 flex flex-col gap-2 px-3">
            {navLinks.map((link) => (
              <button
                key={link.name}
                className={clsx(
                  'flex items-center gap-3 px-4 py-2.5 rounded-lg text-base font-medium transition-all duration-200 relative',
                  active === link.name
                    ? 'bg-brand-50 dark:bg-brand-950 text-brand-600 dark:text-brand-400 border-l-4 border-brand-500'
                    : 'text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800'
                )}
                style={active === link.name ? { boxShadow: 'none' } : {}}
                onClick={() => setActive(link.name)}
              >
                <link.icon size={20} />
                {link.name}
              </button>
            ))}
          </nav>
        </div>
        <div className="px-7 pb-7">
          <div className="mb-5">
            <div className="flex justify-between items-center mb-1 text-xs text-slate-500 dark:text-slate-400">
              <span>Storage Used</span>
              <span>2.1 GB / 10 GB</span>
            </div>
            <div className="w-full h-2 bg-slate-100 dark:bg-slate-900 rounded-full overflow-hidden">
              <div className="h-2 bg-brand-500 rounded-full transition-all duration-300" style={{ width: '21%' }} />
            </div>
          </div>
          <div className="flex items-center gap-3 mb-5">
            <div className="w-9 h-9 rounded-full bg-slate-200 dark:bg-slate-900 flex items-center justify-center">
              <User className="text-slate-500 dark:text-slate-400" size={20} />
            </div>
            <div>
              <div className="font-semibold text-sm text-slate-900 dark:text-white">Jane Doe</div>
              <div className="text-xs text-slate-400 dark:text-slate-500">Product Manager</div>
            </div>
          </div>
          <ThemeToggle />
        </div>
      </aside>
    </>
  );
}
