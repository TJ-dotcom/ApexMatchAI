import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  BriefcaseIcon, 
  MapPinIcon, 
  ChevronDownIcon, 
  ChevronUpIcon, 
  BookmarkIcon 
} from '@heroicons/react/24/outline';
import { BookmarkIcon as BookmarkSolidIcon } from '@heroicons/react/24/solid';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface JobResult {
  title: string;
  company: string;
  location: string;
  description: string;
  match_score: number;
  matched_skills?: string[];
  missing_skills?: string[];
  is_fallback?: boolean;
  url?: string;
  date_posted?: string;
  experience_level?: string;
  salary_range?: string;
  new_grad_friendly?: boolean;
}

interface ResultCardProps {
  job: JobResult;
  index: number;
}

const ResultCard: React.FC<ResultCardProps> = ({ job, index }) => {
  const [expanded, setExpanded] = useState(false);
  const [isSaved, setIsSaved] = useState(false);
  
  // Format the match score as a percentage
  const formattedScore = `${Math.round(job.match_score * 100)}%`;
  
  // Determine the badge color and class based on match score
  const getMatchScoreBadge = (score: number) => {
    const scorePercentage = score * 100;
    
    if (scorePercentage >= 80) {
      return {
        bgColor: 'bg-green-100',
        textColor: 'text-green-800',
        borderColor: 'border-green-300',
        label: 'Great Match'
      };
    } else if (scorePercentage >= 60) {
      return {
        bgColor: 'bg-blue-100',
        textColor: 'text-blue-800',
        borderColor: 'border-blue-300',
        label: 'Good Match'
      };
    } else if (scorePercentage >= 40) {
      return {
        bgColor: 'bg-yellow-100',
        textColor: 'text-yellow-800',
        borderColor: 'border-yellow-300',
        label: 'Possible Match'
      };
    } else {
      return {
        bgColor: 'bg-gray-100',
        textColor: 'text-gray-800',
        borderColor: 'border-gray-300',
        label: 'Low Match'
      };
    }
  };
  
  const badgeStyle = getMatchScoreBadge(job.match_score);
  
  // Truncate longer descriptions
  const truncatedDescription = job.description.length > 160 
    ? job.description.substring(0, 160) + '...' 
    : job.description;
    
  const toggleExpanded = () => {
    setExpanded(!expanded);
  };
  
  const toggleSaved = (e: React.MouseEvent) => {
    e.stopPropagation();
    setIsSaved(!isSaved);
  };
  
  const handleApply = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (job.url) {
      window.open(job.url, '_blank');
    }
  };
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.1 }}
    >
      <Card className={cn(
        "overflow-hidden transition-all",
        expanded && "ring-2 ring-primary/20"
      )}>
        <div className="cursor-pointer" onClick={toggleExpanded}>
          <CardHeader className="p-5 pb-0">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center mb-1.5">
                  <CardTitle className="text-lg">{job.title}</CardTitle>
                  {job.new_grad_friendly && (
                    <Badge variant="secondary" className="ml-2">
                      New Grad
                    </Badge>
                  )}
                </div>
                
                <CardDescription className="flex flex-wrap items-center text-sm mb-3">
                  <div className="flex items-center mr-4">
                    <BriefcaseIcon className="h-4 w-4 mr-1" />
                    <span>{job.company}</span>
                  </div>
                  
                  {job.location && (
                    <div className="flex items-center">
                      <MapPinIcon className="h-4 w-4 mr-1" />
                      <span>{job.location}</span>
                    </div>
                  )}
                  
                  {job.date_posted && (
                    <span className="hidden sm:inline-block ml-4 text-muted-foreground">
                      Posted {job.date_posted}
                    </span>
                  )}
                </CardDescription>
              </div>
              
              <div className="flex flex-col items-end ml-4">
                <Badge variant={
                  job.match_score >= 0.8 ? "default" : 
                  job.match_score >= 0.6 ? "secondary" : 
                  job.match_score >= 0.4 ? "outline" : "outline"
                } 
                className={cn(
                  "px-3 py-1.5",
                  job.match_score >= 0.8 && "bg-green-100 text-green-800 hover:bg-green-100",
                  job.match_score >= 0.6 && job.match_score < 0.8 && "bg-blue-100 text-blue-800 hover:bg-blue-100",
                  job.match_score >= 0.4 && job.match_score < 0.6 && "bg-yellow-100 text-yellow-800 hover:bg-yellow-100",
                  job.match_score < 0.4 && "bg-gray-100 text-gray-800 hover:bg-gray-100"
                )}>
                  <span className="font-semibold mr-1">{formattedScore}</span>
                  <span className="text-xs hidden md:inline-block">{badgeStyle.label}</span>
                </Badge>
                
                <button
                  onClick={toggleSaved}
                  className="mt-2 p-1 rounded-full hover:bg-accent focus:outline-none"
                  aria-label={isSaved ? "Unsave job" : "Save job"}
                >
                  {isSaved ? (
                    <BookmarkSolidIcon className="h-5 w-5 text-yellow-500" />
                  ) : (
                    <BookmarkIcon className="h-5 w-5 text-muted-foreground" />
                  )}
                </button>
              </div>
            </div>
          </CardHeader>
          
          <CardContent className="p-5 pt-2">
            <div className="text-sm text-muted-foreground mt-2 mb-4">
              {expanded ? job.description : truncatedDescription}
            </div>
            
            {!expanded && (
              <div className="flex items-center justify-between mt-1">
                <div className="flex flex-wrap gap-1">
                  {job.matched_skills?.slice(0, 3).map((skill, i) => (
                    <Badge key={i} variant="outline" className="bg-green-100 text-green-800 hover:bg-green-100">
                      {skill}
                    </Badge>
                  ))}
                  {job.matched_skills && job.matched_skills.length > 3 && (
                    <Badge variant="outline" className="bg-gray-100 text-gray-800 hover:bg-gray-100">
                      +{job.matched_skills.length - 3} more
                    </Badge>
                  )}
                </div>
                <div className="flex items-center text-primary text-sm font-medium">
                  <span className="mr-1">{expanded ? 'Show less' : 'Show details'}</span>
                  {expanded ? (
                    <ChevronUpIcon className="h-4 w-4" />
                  ) : (
                    <ChevronDownIcon className="h-4 w-4" />
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </div>
        
        {/* Expanded content */}
        {expanded && (
          <CardContent className="px-5 pb-5 border-t border-muted pt-3">
            {/* Skills section */}
            <div className="mb-5">
              <h4 className="text-sm font-medium mb-3">Skills Match</h4>
              <div className="space-y-3">
                {job.matched_skills && job.matched_skills.length > 0 && (
                  <div>
                    <h5 className="text-xs font-medium text-muted-foreground mb-2">Matching Skills</h5>
                    <div className="flex flex-wrap gap-2">
                      {job.matched_skills.map((skill, i) => (
                        <Badge key={i} variant="outline" className="bg-green-100 text-green-800 hover:bg-green-100">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                
                {job.missing_skills && job.missing_skills.length > 0 && (
                  <div className="mt-3">
                    <h5 className="text-xs font-medium text-muted-foreground mb-2">Skills to Develop</h5>
                    <div className="flex flex-wrap gap-2">
                      {job.missing_skills.map((skill, i) => (
                        <Badge key={i} variant="outline" className="bg-gray-100 text-gray-800 hover:bg-gray-100">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
            
            {/* Additional details */}
            <div className="grid grid-cols-2 gap-4 mb-5">
              {job.experience_level && (
                <div>
                  <h5 className="text-xs font-medium text-muted-foreground">Experience Level</h5>
                  <p className="text-sm">{job.experience_level}</p>
                </div>
              )}
              
              {job.salary_range && (
                <div>
                  <h5 className="text-xs font-medium text-muted-foreground">Salary Range</h5>
                  <p className="text-sm">{job.salary_range}</p>
                </div>
              )}
            </div>
            
            {/* Action buttons */}
            <CardFooter className="px-0 pt-3 flex justify-between items-center">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={toggleExpanded}
                className="flex items-center text-muted-foreground"
              >
                <ChevronUpIcon className="h-4 w-4 mr-1" />
                <span>Show less</span>
              </Button>
              
              <div className="space-x-3">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={toggleSaved}
                  className={cn(
                    isSaved && "bg-yellow-100 text-yellow-800 hover:bg-yellow-200 border-yellow-200"
                  )}
                >
                  {isSaved ? 'Saved' : 'Save'}
                </Button>
                
                {job.url && (
                  <Button
                    size="sm"
                    onClick={handleApply}
                  >
                    Apply Now
                  </Button>
                )}
              </div>
            </CardFooter>
          </CardContent>
        )}
      </Card>
    </motion.div>
  );
};

export default ResultCard;
