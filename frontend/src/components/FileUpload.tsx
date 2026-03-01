import React, { useRef, useState } from 'react';
import { UploadCloud, CheckCircle, AlertCircle, FileText, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useDropzone } from 'react-dropzone';
import { uploadPdf } from '../lib/api';
import { showSuccess, showError } from '../lib/toast';
import clsx from 'clsx';

// PDF file upload component with drag-and-drop support and progress tracking
interface FileUploadProps {
  onUploadComplete?: (filename: string) => void;
}

const FileUpload: React.FC<FileUploadProps> = ({ onUploadComplete }) => {
  const [status, setStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');
  const [progress, setProgress] = useState(0);
  const [filename, setFilename] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const inputRef = useRef<HTMLInputElement>(null);

  const onDrop = async (acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      const file = acceptedFiles[0];
      setStatus('uploading');
      setFilename(file.name);
      setProgress(0);
      setErrorMsg('');
      try {
        // Simulate upload progress steps for visual feedback before the real request
        for (let p = 10; p <= 90; p += 20) {
          setProgress(p);
          await new Promise(res => setTimeout(res, 100));
        }
        // Actual upload
        await uploadPdf(file);
        setProgress(100);
        setStatus('success');
        showSuccess('PDF uploaded successfully');
        if (onUploadComplete) onUploadComplete(file.name);
      } catch (err: unknown) {
        setStatus('error');
        let errorMessage = 'Upload failed';
        
        // Extract meaningful error from axios or network error
        // Provides user-friendly messages instead of raw exception text
        if (err instanceof Error) {
          if (err.message.includes('timeout')) {
            errorMessage = 'Upload timeout - backend may be busy';
          } else if (err.message.includes('network') || err.message.includes('Network')) {
            errorMessage = 'Network error - check backend connection';
          } else {
            errorMessage = err.message || 'Upload failed';
          }
        }
        
        setErrorMsg(errorMessage);
        showError(errorMessage);
      }
    }
  };

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    multiple: false,
    disabled: status === 'uploading'
  });

  const resetUpload = (e: React.MouseEvent) => {
    e.stopPropagation();
    setStatus('idle');
    setProgress(0);
    setFilename('');
  };

    // Removed duplicate and broken resetUpload function

    return (
      <div className="w-full max-w-2xl mx-auto">
        <AnimatePresence mode="wait">
          {status === 'idle' || status === 'error' ? (
            <div
              {...getRootProps({ refKey: 'ref' })}
              className={clsx(
                "relative group cursor-pointer flex flex-col items-center justify-center w-full h-64 rounded-3xl border-2 border-dashed transition-all duration-300",
                isDragActive 
                  ? "border-blue-500 bg-blue-50/50 dark:bg-blue-900/20" 
                  : "border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-900 hover:border-blue-400 dark:hover:border-blue-500 hover:bg-slate-50 dark:hover:bg-slate-800/50",
                status === 'error' && "border-red-300 bg-red-50/50 dark:border-red-900 dark:bg-red-900/10"
              )}
            >
              <motion.div
                key="dropzone"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="w-full h-full flex flex-col items-center justify-center"
              >
                <input {...getInputProps()} />
                <div className="relative z-10 flex flex-col items-center space-y-4 text-center p-6">
                  <div className={clsx(
                    "p-4 rounded-full transition-colors duration-300",
                    isDragActive ? "bg-blue-100 text-blue-600" : "bg-slate-100 text-slate-500 dark:bg-slate-800 dark:text-slate-400 group-hover:bg-blue-50 group-hover:text-blue-600 dark:group-hover:bg-slate-700 dark:group-hover:text-blue-400",
                    status === 'error' && "bg-red-100 text-red-500 dark:bg-red-900/30"
                  )}>
                    {status === 'error' ? <AlertCircle className="w-8 h-8" /> : <UploadCloud className="w-8 h-8" />}
                  </div>
                  <div className="space-y-1">
                    <p className="text-lg font-medium text-slate-700 dark:text-slate-200">
                      {status === 'error' ? 'Upload Failed' : 'Click to upload or drag and drop'}
                    </p>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      {status === 'error' ? errorMsg : 'PDF (max 10MB)'}
                    </p>
                  </div>
                </div>
              </motion.div>
            </div>
          ) : (
            <motion.div
              key="progress"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="w-full bg-white dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800 p-8 shadow-sm"
            >
              <div className="flex items-center justify-between mb-6">
                <div className="flex items-center space-x-4">
                  <div className={clsx(
                    "p-3 rounded-2xl",
                    status === 'success' ? "bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400" : "bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400"
                  )}>
                    {status === 'success' ? <CheckCircle className="w-6 h-6" /> : <FileText className="w-6 h-6" />}
                  </div>
                  <div>
                    <h3 className="font-medium text-slate-900 dark:text-white truncate max-w-[200px] sm:max-w-xs">
                      {filename}
                    </h3>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      {status === 'success' ? 'Ready for search' : 'Uploading...'}
                    </p>
                  </div>
                </div>
              
                {status === 'uploading' && (
                  <button 
                    onClick={resetUpload}
                    className="p-2 hover:bg-slate-100 dark:hover:bg-slate-800 rounded-full text-slate-400 hover:text-slate-600 transition-colors"
                  >
                    <X className="w-5 h-5" />
                  </button>
                )}
              </div>

              <div className="space-y-2">
                <div className="flex justify-between text-sm font-medium">
                  <span className={status === 'success' ? "text-green-600 dark:text-green-400" : "text-blue-600 dark:text-blue-400"}>
                    {progress}%
                  </span>
                </div>
                <div className="h-3 w-full bg-slate-100 dark:bg-slate-800 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ ease: "easeInOut" }}
                    className={clsx(
                      "h-full rounded-full transition-all duration-300",
                      status === 'success' ? "bg-green-500" : "bg-blue-500"
                    )}
                  />
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    );
  };
export default FileUpload;
