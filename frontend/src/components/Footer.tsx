import { Github, Linkedin } from 'lucide-react';

// Site footer with brand name and developer social links
const Footer = () => (
  <footer className="w-full border-t border-slate-200 dark:border-slate-800 py-6 bg-transparent">
    <div className="max-w-5xl mx-auto flex items-center justify-between px-4">
      {/* Brand Left */}
      <div className="text-sm font-medium text-slate-500 dark:text-slate-400">
        AI Document Q&A System
      </div>
      {/* Developer Info Right */}
      <div className="flex items-center gap-3">
        <a
          href="https://github.com/abdullahghaffar9"
          target="_blank"
          rel="noopener noreferrer"
          className="text-slate-400 hover:text-white transition-colors"
          aria-label="GitHub"
        >
          <Github className="w-4 h-4" />
        </a>
        <a
          href="https://www.linkedin.com/in/abdullahghaffar"
          target="_blank"
          rel="noopener noreferrer"
          className="text-slate-400 hover:text-white transition-colors"
          aria-label="LinkedIn"
        >
          <Linkedin className="w-4 h-4" />
        </a>
      </div>
    </div>
  </footer>
);

export default Footer;