import React, { useState } from 'react';
import axios from 'axios';
import { 
  ArrowDownTrayIcon, 
  CheckCircleIcon, 
  ExclamationCircleIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import { motion } from 'framer-motion';

interface DownloadLinkProps {
  csvUrl?: string;
}

const DownloadLink: React.FC<DownloadLinkProps> = ({ csvUrl }) => {
  const [isDownloading, setIsDownloading] = useState(false);
  const [isDownloaded, setIsDownloaded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!csvUrl) return null;
  
  const handleDownload = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    
    if (isDownloading) return;
    
    setIsDownloading(true);
    setError(null);
    
    try {
      console.log(`Attempting to download from: http://localhost:8000${csvUrl}`);
      
      // Use JavaScript to trigger the file download
      window.location.href = `http://localhost:8000${csvUrl}`;
      
      // Give browser time to start download
      setTimeout(() => {
        setIsDownloading(false);
        setIsDownloaded(true);
        
        // Reset "downloaded" state after a while
        setTimeout(() => {
          setIsDownloaded(false);
        }, 5000);
      }, 2000);
      
    } catch (err) {
      console.error('Download error:', err);
      setError('Failed to download results. Please try again.');
      setIsDownloading(false);
    }
  };
    return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="mt-6 flex flex-col items-center"
    >
      <div className="w-full max-w-md">
        <div className="bg-black/80 border border-blue-500/30 shadow-lg rounded-lg px-6 py-5">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium text-blue-400 relative">
              <span className="relative">
                DATA EXTRACTION
                <span className="absolute top-0 left-0 -ml-0.5 text-red-400 opacity-70">
                  DATA EXTRACTION
                </span>
              </span>
            </h3>
            <span className="text-sm text-cyan-500 border border-cyan-800 px-2 py-0.5 rounded-sm">CSV FORMAT</span>
          </div>
          
          <p className="text-sm text-gray-400 mb-4 border-l-2 border-blue-500/50 pl-3">
            Extract job intelligence data to external system or integrate with data analysis matrix.
          </p>
          
          <div className="flex justify-center">
            <button
              onClick={handleDownload}
              disabled={isDownloading}
              className={`relative flex items-center justify-center px-4 py-3 rounded-sm font-medium 
                transition-all duration-200 w-full sm:w-auto border
                ${isDownloaded 
                  ? 'bg-green-900/30 text-green-400 border-green-500 hover:shadow-[0_0_15px_rgba(74,222,128,0.5)]' 
                  : error 
                    ? 'bg-red-900/30 text-red-400 border-red-500 hover:shadow-[0_0_15px_rgba(248,113,113,0.5)]' 
                    : 'bg-blue-900/30 text-blue-400 border-blue-500 hover:shadow-[0_0_15px_rgba(59,130,246,0.5)]'}`}
            >
              <div className="relative">
                <span className="relative z-10 flex items-center">
                  {isDownloading ? (
                    <>
                      <ArrowPathIcon className="animate-spin h-5 w-5 mr-2" />
                      <span>EXTRACTING DATA...</span>
                    </>
                  ) : isDownloaded ? (
                    <>
                      <CheckCircleIcon className="h-5 w-5 mr-2" />
                      <span>DATA RETRIEVED</span>
                    </>
                  ) : error ? (
                    <>
                      <ExclamationCircleIcon className="h-5 w-5 mr-2" />
                      <span>CONNECTION FAILURE - RETRY</span>
                    </>
                  ) : (
                    <>
                      <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
                      <span>EXTRACT MATCH DATA</span>
                    </>
                  )}
                </span>
                <span className="absolute inset-0 flex items-center z-0 text-red-500 opacity-50">
                  {isDownloading ? "EXTRACTING DATA..." : isDownloaded ? "DATA RETRIEVED" : error ? "CONNECTION FAILURE" : "EXTRACT MATCH DATA"}
                </span>
              </div>
            </button>
          </div>
          
          {error && (
            <p className="mt-2 text-center text-sm text-red-500">{error}</p>
          )}
        </div>
        
        <div className="text-center text-xs text-cyan-600 mt-2 border-t border-cyan-900/30 pt-2">
          <span className="bg-black/70 px-2">SYSTEM LOG: Save data artifact for future infiltration operations</span>
        </div>
      </div>
    </motion.div>
  );
};

export default DownloadLink;
