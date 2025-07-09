import { useState, FormEvent, ChangeEvent, DragEvent } from 'react';
import axios from 'axios';
import { DocumentArrowUpIcon, GlobeAltIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { motion } from 'framer-motion';
import { CyberpunkButton } from "@/components/ui";

interface UploadFormProps {
  onUploadSuccess: (taskId: string) => void;
  isProcessing?: boolean;
}

const UploadForm: React.FC<UploadFormProps> = ({ onUploadSuccess, isProcessing = false }) => {
  const [file, setFile] = useState<File | null>(null);
  const [jobUrl, setJobUrl] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);

  // Cyberpunk glitch effect timing
  const glitchVariants = {
    hidden: { opacity: 0, y: -10 },
    visible: { 
      opacity: 1, 
      y: 0,
      transition: {
        duration: 0.4,
        ease: "easeOut"
      }
    }
  };

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      validateAndSetFile(selectedFile);
    }
  };

  const validateAndSetFile = (selectedFile: File) => {
    // Check file type
    const fileType = selectedFile.type;
    if (fileType === 'application/pdf' || 
        fileType === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
      setFile(selectedFile);
      setError(null);
    } else {
      setFile(null);
      setError('Please upload a PDF or DOCX file.');
    }
  };

  const handleUrlChange = (e: ChangeEvent<HTMLInputElement>) => {
    setJobUrl(e.target.value);
  };

  const handleDragOver = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    const droppedFiles = e.dataTransfer.files;
    if (droppedFiles.length > 0) {
      validateAndSetFile(droppedFiles[0]);
    }
  };

  const clearFile = () => {
    setFile(null);
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please upload a resume file.');
      return;
    }
    
    if (!jobUrl) {
      setError('Please enter a job board URL.');
      return;
    }
    
    // Validate URL format
    try {
      new URL(jobUrl);
    } catch (e) {
      setError('Please enter a valid URL (e.g., https://example.com).');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    // Create form data
    const formData = new FormData();
    formData.append('resume', file);
    formData.append('job_url', jobUrl);
    
    try {
      const response = await axios.post('http://localhost:8000/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000, // 30 second timeout
      });
      
      if (response.data && response.data.task_id) {
        onUploadSuccess(response.data.task_id);
      } else {
        setError('Something went wrong. Please try again. The server response was missing a task ID.');
      }
    } catch (error) {
      console.error('Upload error:', error);
      // Provide more detailed error message
      if (axios.isAxiosError(error)) {
        if (error.code === 'ECONNABORTED') {
          setError('Request timed out. The server is taking too long to respond.');
        } else if (error.response) {
          setError(`Server error (${error.response.status}): ${error.response.data.detail || 'Unknown error'}`);
        } else if (error.request) {
          setError('No response from server. Please check if the server is running.');
        } else {
          setError(`Error: ${error.message}`);
        }
      } else {
        setError('Failed to upload. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <motion.div 
      className="w-full max-w-3xl mx-auto rounded-xl shadow-lg overflow-hidden noise"
      style={{background: '#0d1117', border: '1px solid rgba(59, 130, 246, 0.5)'}}
      initial="hidden"
      animate="visible"
      variants={{
        hidden: { opacity: 0 },
        visible: { 
          opacity: 1,
          transition: {
            when: "beforeChildren",
            staggerChildren: 0.2
          }
        }
      }}
    >
      <div className="bg-gradient-to-r from-blue-900 to-indigo-900 p-6 neon-border-blue scan-line">
        <motion.h2 
          className="text-2xl font-bold mb-2 text-blue-300 glitch-text"
          variants={glitchVariants}
        >
          <span className="glitch-offset text-pink-500">FIND YOUR NEXT GIG</span>
          FIND YOUR NEXT GIG
        </motion.h2>
        <motion.p 
          className="text-blue-200 text-sm flicker"
          variants={glitchVariants}
        >
          AI-powered resume matching for the cyberpunk future
        </motion.p>
      </div>

      <div className="bg-gray-900 p-4 border-b border-blue-900">
        <div className="flex items-start">
          <div className="flex-shrink-0 p-1">
            <motion.div 
              className="data-indicator"
              animate={{
                boxShadow: ['0 0 5px rgba(59, 130, 246, 0.8)', '0 0 10px rgba(59, 130, 246, 0.8)', '0 0 5px rgba(59, 130, 246, 0.8)']
              }}
              transition={{
                duration: 1.5,
                repeat: Infinity,
                repeatType: "reverse"
              }}
            ></motion.div>
          </div>
          <div className="ml-3">
            <motion.h3 
              className="text-sm font-medium text-blue-400 digital-distort"
              variants={glitchVariants}
            >
              SYSTEM INSTRUCTIONS
            </motion.h3>
            <motion.p 
              className="mt-1 text-sm text-blue-300 typing-text"
              variants={glitchVariants}
            >
              Upload your resume and provide a job board URL. Our AI will analyze your skills and match you with the most relevant job listings.
            </motion.p>
          </div>
        </div>
      </div>
      
      <div className="p-6 scan-line" style={{background: 'linear-gradient(180deg, rgba(13,17,23,1) 0%, rgba(23,27,33,0.8) 100%)'}}>
        <form onSubmit={handleSubmit} className="space-y-6">
          <motion.div 
            className="relative"
            variants={glitchVariants}
          >
            <label htmlFor="resume" className="block text-sm font-medium text-blue-400 mb-1 color-cycle">
              UPLOAD YOUR RESUME
            </label>
            <div 
              className={`relative border-2 border-dashed rounded-lg p-6 transition-all
                ${isDragging ? 'border-blue-500 bg-blue-900 bg-opacity-20' : 'border-blue-700 hover:border-blue-500'} 
                ${file ? 'bg-green-900 bg-opacity-20 border-green-600' : ''}`}
              style={{
                backdropFilter: 'blur(3px)',
                boxShadow: file ? '0 0 15px rgba(74, 222, 128, 0.2)' : '0 0 15px rgba(59, 130, 246, 0.2)'
              }}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <div className="text-center">
                {file ? (
                  <div className="flex flex-col items-center">
                    <motion.div
                      animate={{
                        y: [0, -5, 0],
                        scale: [1, 1.05, 1]
                      }}
                      transition={{
                        duration: 2,
                        repeat: Infinity,
                        repeatType: "reverse"
                      }}
                    >
                      <DocumentArrowUpIcon className="h-10 w-10 text-green-400" />
                    </motion.div>
                    <span className="mt-2 block text-sm font-medium text-green-400">{file.name}</span>
                    <span className="block text-sm text-green-500">
                      {(file.size / 1024 / 1024).toFixed(2)} MB
                    </span>
                    <button
                      type="button"
                      onClick={clearFile}
                      className="mt-2 inline-flex items-center px-3 py-1 border border-transparent text-xs font-medium rounded-md text-red-500 bg-red-900 bg-opacity-30 hover:bg-opacity-50 focus:outline-none border-red-500 neon-border-red"
                    >
                      PURGE
                    </button>
                  </div>
                ) : (
                  <>
                    <motion.div
                      animate={{
                        boxShadow: ['0 0 10px rgba(59, 130, 246, 0.3)', '0 0 20px rgba(59, 130, 246, 0.5)', '0 0 10px rgba(59, 130, 246, 0.3)']
                      }}
                      transition={{
                        duration: 2,
                        repeat: Infinity,
                        repeatType: "reverse"
                      }}
                    >
                      <DocumentArrowUpIcon className="mx-auto h-12 w-12 text-blue-400" />
                    </motion.div>
                    <p className="mt-2 text-sm text-blue-300">
                      <span className="font-semibold">CLICK TO UPLOAD</span> or DRAG AND DROP
                    </p>
                    <p className="mt-1 text-xs text-blue-500">PDF or DOCX files up to 10MB</p>
                  </>
                )}
              </div>
              
              {/* Hidden file input */}
              <input
                id="resume"
                name="resume"
                type="file"
                accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                onChange={handleFileChange}
                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                disabled={loading || isProcessing}
              />
            </div>
          </motion.div>

          <motion.div variants={glitchVariants}>
            <label htmlFor="jobUrl" className="block text-sm font-medium text-blue-400 mb-1 color-cycle">
              JOB BOARD URL
            </label>
            <div className="mt-1 relative rounded-md shadow-sm">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <GlobeAltIcon className="h-5 w-5 text-blue-500" aria-hidden="true" />
              </div>
              <input
                type="text"
                id="jobUrl"
                name="jobUrl"
                value={jobUrl}
                onChange={handleUrlChange}
                className="terminal-input block w-full pl-10 py-3 sm:text-sm rounded-md focus:outline-none bg-opacity-50"
                placeholder="https://www.linkedin.com/jobs/search?keywords=software"
                disabled={loading || isProcessing}
                style={{
                  background: 'linear-gradient(180deg, rgba(17, 24, 39, 0.7) 0%, rgba(17, 24, 39, 0.9) 100%)',
                }}
              />
            </div>
            <p className="mt-1 text-xs text-blue-500">
              Enter a URL from LinkedIn Jobs, Indeed, or other job boards
            </p>
          </motion.div>

          {error && (
            <motion.div 
              className="rounded-md p-4 noise"
              style={{
                background: 'rgba(153, 27, 27, 0.3)',
                border: '1px solid rgba(248, 113, 113, 0.5)',
                boxShadow: '0 0 15px rgba(248, 113, 113, 0.3)'
              }}
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
            >
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400 pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-300 digital-distort">SYSTEM ERROR</h3>
                  <div className="mt-1 text-sm text-red-300">{error}</div>
                </div>
              </div>
            </motion.div>
          )}

          <div className="flex justify-end">
            <CyberpunkButton
              type="submit"
              disabled={loading || isProcessing || !file || !jobUrl}
              className={`px-6 py-3 rounded-md text-white font-medium flex items-center space-x-3
                ${loading || isProcessing || !file || !jobUrl 
                  ? 'bg-gray-700 cursor-not-allowed opacity-50' 
                  : 'bg-gradient-to-r from-blue-800 to-indigo-900 hover:from-blue-700 hover:to-indigo-800 focus:outline-none neon-border-blue'}`}
            >
              {loading ? (
                <>
                  <ArrowPathIcon className="h-5 w-5 animate-spin text-blue-300" />
                  <span>PROCESSING...</span>
                </>
              ) : (
                <>
                  <span className="glitch-text">
                    <span className="glitch-offset text-pink-500">FIND MATCHING JOBS</span>
                    FIND MATCHING JOBS
                  </span>
                </>
              )}
            </CyberpunkButton>
          </div>
        </form>
      </div>
    </motion.div>
  );
};

export default UploadForm;
