"use client";

import { useState, useEffect } from 'react';
import axios from 'axios';
import UploadForm from './components/UploadForm';
import { CyberpunkProgress, CyberpunkResultCard, CyberpunkButton, CyberpunkToaster } from "@/components/ui";
import DownloadLink from './components/DownloadLink';

interface JobResult {
  title: string;
  company: string;
  location: string;
  description: string;
  match_score: number;
}

interface ResultsData {
  status: 'processing' | 'completed' | 'failed';
  results?: JobResult[];
  error?: string;
  csv_url?: string;
}

export default function Home() {
  const [taskId, setTaskId] = useState<string | null>(null);
  const [pollingInterval, setPollingInterval] = useState<NodeJS.Timeout | null>(null);
  const [results, setResults] = useState<ResultsData | null>(null);
  const [appState, setAppState] = useState<'initial' | 'processing' | 'success' | 'error'>('initial');

  // Handle successful upload
  const handleUploadSuccess = (id: string) => {
    setTaskId(id);
    setResults({ status: 'processing' });
    setAppState('processing');
  };

  // Poll for results
  useEffect(() => {
    if (!taskId) return;
    const startPolling = () => {
      const interval = setInterval(async () => {
        try {
          if (!taskId) {
            if (pollingInterval) clearInterval(pollingInterval);
            return;
          }
          const response = await axios.get(`http://localhost:8000/results/${taskId}`);
          const data = response.data as ResultsData;
          setResults(data);
          if (data.status !== 'processing') {
            if (pollingInterval) clearInterval(pollingInterval);
          }
        } catch (error) {
          setResults({
            status: 'failed',
            error: 'Failed to fetch results. The server may be down or the task may have expired.'
          });
          if (pollingInterval) clearInterval(pollingInterval);
        }
      }, 2000);
      setPollingInterval(interval);
    };
    startPolling();
    return () => {
      if (pollingInterval) clearInterval(pollingInterval);
    };
  }, [taskId]);

  // Render content based on app state
  const renderContent = () => {
    if (!taskId) {
      return (
        <div className="max-w-xl mx-auto mt-10">
          <div className="bg-white dark:bg-zinc-900 rounded-lg shadow p-8">
            <UploadForm onUploadSuccess={handleUploadSuccess} />
          </div>
        </div>
      );
    }
    if (results?.status === 'processing') {
      return (
        <div className="max-w-xl mx-auto mt-10">
          <div className="bg-white dark:bg-zinc-900 rounded-lg shadow p-8">
            <CyberpunkProgress step={1} totalSteps={3} label="Analyzing your resume and matching with job opportunities..." />
          </div>
        </div>
      );
    }
    if (results?.status === 'completed' && results.results) {
      return (
        <div className="max-w-3xl mx-auto mt-10">
          <div className="bg-white dark:bg-zinc-900 rounded-lg shadow p-8 mb-6 text-center">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Your Results Are Ready!</h2>
            <p className="text-base text-gray-600 dark:text-gray-300 mb-6">
              We found <span className="font-semibold text-indigo-600 dark:text-indigo-400">{results.results.length}</span> job listings that match your resume and skills.
            </p>
            <div className="flex flex-col md:flex-row justify-center items-center space-y-4 md:space-y-0 md:space-x-4">
              <DownloadLink csvUrl={results.csv_url} />
              <CyberpunkButton
                onClick={() => {
                  setTaskId(null);
                  setResults(null);
                  setAppState('initial');
                  if (pollingInterval) clearInterval(pollingInterval);
                }}
              >
                New Search
              </CyberpunkButton>
            </div>
          </div>
          <div className="mb-8">
            <div className="flex items-center justify-between mb-6 border-b border-gray-200 pb-4 dark:border-zinc-700">
              <h3 className="text-2xl font-bold text-gray-800 dark:text-white">Top Matching Jobs</h3>
              <div className="badge badge-primary">Sorted by match score</div>
            </div>
            <div className="grid grid-cols-1 gap-6">
              {results.results
                .sort((a, b) => b.match_score - a.match_score)
                .map((job, index) => (
                  <CyberpunkResultCard key={index} job={{ ...job, score: job.match_score }} index={index} />
                ))}
            </div>
          </div>
        </div>
      );
    }
    if (results?.status === 'failed') {
      return (
        <div className="max-w-xl mx-auto mt-10">
          <div className="bg-white dark:bg-zinc-900 rounded-lg shadow p-8 border-l-4 border-red-500">
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Error Processing Your Request</h3>
            <p className="text-base text-gray-700 dark:text-gray-300 mb-4">{results.error || 'Something went wrong. Please try again.'}</p>
            <CyberpunkButton
              onClick={() => {
                setTaskId(null);
                setResults(null);
                setAppState('initial');
              }}
            >
              Try Again
            </CyberpunkButton>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-zinc-950 pb-12">
      <nav className="bg-white dark:bg-zinc-900 shadow-sm sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center">
              <span className="ml-2 font-bold text-lg text-gray-800 dark:text-white">Job Match AI</span>
            </div>
            <div className="flex items-center space-x-4">
              <a href="#how-it-works" className="text-gray-600 dark:text-gray-300 hover:text-indigo-600">How It Works</a>
              <a href="#features" className="text-gray-600 dark:text-gray-300 hover:text-indigo-600">Features</a>
            </div>
          </div>
        </div>
      </nav>
      <main className="pt-8">
        <div className="max-w-5xl mx-auto px-4">
          <div className="mb-12 text-center">
            <h1 className="text-4xl md:text-5xl font-bold text-indigo-700 dark:text-indigo-400 mb-4">Find Your Perfect Job Match with AI</h1>
            <p className="text-lg text-gray-700 dark:text-gray-300 max-w-2xl mx-auto">
              Our advanced AI analyzes your resume and compares it with job listings to find the perfect matches based on your skills and experience.
            </p>
          </div>
          {renderContent()}
        </div>
      </main>
      <footer className="bg-gray-900 text-white mt-6 py-8">
        <div className="max-w-5xl mx-auto px-4">
          <div className="md:flex md:items-center md:justify-between">
            <span className="font-semibold text-lg">Job Match AI</span>
            <div className="flex space-x-6 mb-6 md:mb-0">
              <a href="#features" className="text-gray-400 hover:text-indigo-300 transition-colors duration-200">Features</a>
              <a href="#how-it-works" className="text-gray-400 hover:text-indigo-300 transition-colors duration-200">How It Works</a>
              <a href="#" className="text-gray-400 hover:text-indigo-300 transition-colors duration-200">Privacy</a>
            </div>
            <p className="text-gray-500">&copy; {new Date().getFullYear()} Job Match AI | Powered by AI Resume Analysis</p>
          </div>
        </div>
      </footer>
      <CyberpunkToaster />
    </div>
  );
}
