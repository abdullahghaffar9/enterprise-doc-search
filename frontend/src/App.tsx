

import React from 'react';
import Header from './components/Header';
import Footer from './components/Footer';
import FileUpload from './components/FileUpload';
import SearchDashboard from './components/SearchDashboard';

function SectionTitle({ children }: { children: React.ReactNode }) {
  return (
    <h2 className="text-2xl font-bold tracking-tight text-slate-900 dark:text-white mb-2">{children}</h2>
  );
}

export default function App() {
  return (
    <div className="min-h-screen flex flex-col bg-slate-50 dark:bg-slate-950 transition-colors duration-300">
      <Header />
      <main className="flex-grow container mx-auto px-4 py-20 max-w-5xl">
        <div className="space-y-12">
          <SectionTitle>Upload Knowledge</SectionTitle>
          <FileUpload />

          <div className="my-12 border-t border-slate-200 dark:border-slate-800" />

          <SectionTitle>Ask Questions</SectionTitle>
          <SearchDashboard />
        </div>
      </main>
      <Footer />
    </div>
  );
}
