import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface ModalProps {
  open: boolean;
  onClose: () => void;
  title?: string;
  children: React.ReactNode;
  size?: 'sm' | 'md' | 'lg';
}

// Maps the size prop to a Tailwind max-width class for the modal panel
const sizeMap = {
  sm: 'max-w-md',
  md: 'max-w-xl',
  lg: 'max-w-2xl',
};

export default function Modal({ open, onClose, title, children, size = 'md' }: ModalProps) {
  return (
    <AnimatePresence>
      {open && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <div
            className="absolute inset-0 bg-black/30 backdrop-blur-sm"
            onClick={onClose}
            aria-label="Close modal"
            // Clicking the backdrop outside the panel closes the modal
          />
          <motion.div
            className={`relative bg-white/95 dark:bg-slate-950/95 rounded-2xl border border-slate-100 dark:border-slate-900 w-full ${sizeMap[size]} mx-4 p-8 transition-all duration-200 shadow-none`}
            initial={{ scale: 0.96, y: 40, opacity: 0 }}
            animate={{ scale: 1, y: 0, opacity: 1 }}
            exit={{ scale: 0.96, y: 40, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 300, damping: 30 }}
            tabIndex={-1}
            role="dialog"
            aria-modal="true"
          >
            {title && <div className="text-xl font-bold mb-6 text-slate-900 dark:text-white">{title}</div>}
            <button
              className="absolute top-5 right-5 p-2 rounded focus:outline-none focus:ring-2 focus:ring-brand-500 hover:bg-slate-100 dark:hover:bg-slate-800"
              onClick={onClose}
              aria-label="Close"
            >
              <svg width="22" height="22" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18" /><line x1="6" y1="6" x2="18" y2="18" /></svg>
            </button>
            {children}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
