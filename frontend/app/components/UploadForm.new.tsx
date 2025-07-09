import { useState, FormEvent, ChangeEvent, DragEvent } from 'react';
import axios from 'axios';
import { DocumentArrowUpIcon, GlobeAltIcon, ArrowPathIcon } from '@heroicons/react/24/outline';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { cn } from '@/lib/utils';

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
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      console.error('Error submitting form:', error);
      setError('Failed to process your request. Please try again later.');
      setLoading(false);
    }
  };
  
  // For demo purposes, simulate a successful upload
  const handleDemoSubmit = (e: FormEvent) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please upload a resume file.');
      return;
    }
    
    if (!jobUrl) {
      setError('Please enter a job board URL.');
      return;
    }
    
    setLoading(true);
    setError(null);
    
    // Simulate API call delay
    setTimeout(() => {
      onUploadSuccess('demo-task-id');
    }, 1000);
  };

  return (
    <Card className="w-full max-w-3xl mx-auto p-6 bg-card text-card-foreground">
      <CardHeader>
        <CardTitle className="text-2xl font-bold text-center">Match Your Resume to Job Listings</CardTitle>
        <CardDescription className="text-center max-w-lg mx-auto mt-2">
          Upload your resume and provide a job board URL. Our AI will analyze your skills and match you with the most suitable positions.
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        <form onSubmit={handleDemoSubmit} className="space-y-6">
          {/* Resume upload */}
          <div>
            <div className="mb-2 font-medium">Resume</div>
            <div
              className={cn(
                "w-full border-2 border-dashed rounded-lg p-6 cursor-pointer transition-colors",
                isDragging ? "border-primary bg-primary/5" : "border-muted",
                file ? "bg-muted/20" : "hover:bg-muted/10"
              )}
              onDragOver={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
              onClick={() => document.getElementById('resume-upload')?.click()}
            >
              <input
                type="file"
                id="resume-upload"
                className="hidden"
                onChange={handleFileChange}
                accept=".pdf,.docx"
              />
              <div className="flex flex-col items-center justify-center text-center">
                <DocumentArrowUpIcon className="h-10 w-10 text-muted-foreground mb-2" />
                
                {file ? (
                  <div className="space-y-2">
                    <p className="font-medium text-card-foreground">{file.name}</p>
                    <p className="text-sm text-muted-foreground">{Math.round(file.size / 1024)} KB</p>
                    <Button
                      type="button"
                      variant="outline"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        clearFile();
                      }}
                      className="mt-2"
                    >
                      Change File
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-1">
                    <p className="font-medium">Upload your resume</p>
                    <p className="text-sm text-muted-foreground">Drag and drop or click to browse</p>
                    <p className="text-sm text-muted-foreground">PDF or DOCX formats (5MB max)</p>
                  </div>
                )}
              </div>
            </div>
          </div>
          
          {/* Job board URL input */}
          <div>
            <label htmlFor="job-url" className="block mb-2 font-medium">
              Job Board URL
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <GlobeAltIcon className="h-5 w-5 text-muted-foreground" />
              </div>
              <Input
                id="job-url"
                type="url"
                placeholder="https://linkedin.com/jobs/search"
                value={jobUrl}
                onChange={handleUrlChange}
                className="pl-10"
              />
            </div>
            <p className="mt-1 text-sm text-muted-foreground">
              Enter URL to a job board with listings (e.g., LinkedIn, Indeed)
            </p>
          </div>
          
          {/* Error message */}
          {error && (
            <div className="rounded-md bg-destructive/10 p-3 text-sm text-destructive">
              {error}
            </div>
          )}
          
          {/* Submit button */}
          <Button 
            type="submit" 
            className="w-full" 
            disabled={loading}
          >
            {loading ? (
              <>
                <ArrowPathIcon className="h-5 w-5 mr-2 animate-spin" />
                Processing...
              </>
            ) : (
              'Find Matching Jobs'
            )}
          </Button>
          
          <p className="text-xs text-center text-muted-foreground">
            By clicking "Find Matching Jobs", you agree to our Terms of Service and Privacy Policy.
          </p>
        </form>
      </CardContent>
    </Card>
  );
};

export default UploadForm;
