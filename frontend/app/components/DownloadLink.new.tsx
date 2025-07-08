import React, { useState } from 'react';
import axios from 'axios';
import { 
  ArrowDownTrayIcon, 
  CheckCircleIcon, 
  ExclamationCircleIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';
import { motion } from 'framer-motion';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

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
      className="mt-6"
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
    >
      <Card className="overflow-hidden">
        <CardContent className="p-6">
          <div className="flex items-center flex-col sm:flex-row justify-between gap-4">
            <div className="text-center sm:text-left">
              <h3 className="font-medium text-lg mb-1">Download Results</h3>
              <p className="text-muted-foreground text-sm">
                Save all job matches as a CSV spreadsheet
              </p>
            </div>
            
            <Button
              onClick={handleDownload}
              disabled={isDownloading || isDownloaded}
              className={cn(
                "px-4 py-2 flex items-center",
                isDownloaded && "bg-green-600 hover:bg-green-700"
              )}
            >
              {isDownloading ? (
                <>
                  <ArrowPathIcon className="h-5 w-5 mr-2 animate-spin" />
                  Downloading...
                </>
              ) : isDownloaded ? (
                <>
                  <CheckCircleIcon className="h-5 w-5 mr-2" />
                  Downloaded
                </>
              ) : (
                <>
                  <ArrowDownTrayIcon className="h-5 w-5 mr-2" />
                  Download CSV
                </>
              )}
            </Button>
          </div>
          
          {error && (
            <div className="mt-3 text-sm text-destructive bg-destructive/10 p-3 rounded-md">
              <div className="flex items-center">
                <ExclamationCircleIcon className="h-5 w-5 mr-2 flex-shrink-0" /> {error}
              </div>
              <div className="mt-2">
                <Button 
                  variant="secondary" 
                  size="sm" 
                  onClick={() => handleDownload} 
                  className="text-xs"
                >
                  Try Again
                </Button>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </motion.div>
  );
};

export default DownloadLink;
