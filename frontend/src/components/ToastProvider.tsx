import React from 'react';
import { Toaster } from 'sonner';

// Wraps the app with a global toast notification system (top-right, 3.5s auto-dismiss)
export default function ToastProvider({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Toaster
        position="top-right"
        richColors
        closeButton
        duration={3500}
        toastOptions={{
          className: 'font-sans text-sm shadow-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 text-slate-900 dark:text-white',
        }}
      />
      {children}
    </>
  );
}
