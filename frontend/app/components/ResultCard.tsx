import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  BriefcaseIcon, 
  MapPinIcon, 
  ClockIcon,
  CurrencyDollarIcon,
  ChevronDownIcon, 
  ChevronUpIcon, 
  BookmarkIcon,
  HeartIcon
} from '@heroicons/react/24/outline';
import { HeartIcon as HeartSolidIcon } from '@heroicons/react/24/solid';
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
  const scoreValue = Math.round(job.match_score * 100);
  
  // Get match color based on score
  const getMatchColor = (score: number) => {
    if (score >= 90) return "from-lime-400 to-green-400";
    if (score >= 80) return "from-orange-400 to-red-400";
    if (score >= 70) return "from-yellow-400 to-orange-400";
    return "from-red-400 to-red-600";
  };
  
  // Get difficulty based on score
  const getDifficulty = (score: number) => {
    if (score >= 90) return "rookie";
    if (score >= 80) return "veteran";
    if (score >= 70) return "elite";
    return "legendary";
  };
  
  // Get difficulty color
  const getDifficultyColor = (level: string) => {
    switch (level) {
      case "legendary":
        return "text-purple-400 bg-purple-900/30 border-purple-400";
      case "elite":
        return "text-red-400 bg-red-900/30 border-red-400";
      case "veteran":
        return "text-orange-400 bg-orange-900/30 border-orange-400";
      case "rookie":
        return "text-lime-400 bg-lime-900/30 border-lime-400";
      default:
        return "text-gray-400 bg-gray-900/30 border-gray-400";
    }
  };
    // Render hearts based on score
  const renderHearts = (score: number) => {
    const getHeartFill = (heartIndex: number, score: number) => {
      // Each heart represents 20% (100% ÷ 5 hearts)
      // Heart 1: 0-20%, Heart 2: 20-40%, Heart 3: 40-60%, Heart 4: 60-80%, Heart 5: 80-100%
      const heartStartValue = heartIndex * 20;
      const heartEndValue = (heartIndex + 1) * 20;

      if (score >= heartEndValue) {
        return "full"; // Score is above this heart's range
      } else if (score > heartStartValue) {
        // Score falls within this heart's range - calculate partial fill
        const progressInHeart = score - heartStartValue;
        const percentageInHeart = (progressInHeart / 20) * 100;

        if (percentageInHeart >= 87.5) return "full"; // 17.5/20 = 87.5%
        if (percentageInHeart >= 62.5) return "three-quarter"; // 12.5/20 = 62.5%
        if (percentageInHeart >= 37.5) return "half"; // 7.5/20 = 37.5%
        if (percentageInHeart >= 12.5) return "quarter"; // 2.5/20 = 12.5%
        return "empty";
      } else {
        return "empty"; // Score is below this heart's range
      }
    };

    return (
      <div className="flex items-center gap-1">
        {Array.from({ length: 5 }, (_, i) => {
          const fillType = getHeartFill(i, score);
          return (            <div key={i} className="relative">
              <HeartIcon className="h-5 w-5 text-gray-700" />
              {fillType !== "empty" && (
                <div
                  className="absolute inset-0 overflow-hidden"
                  style={{
                    clipPath:
                      fillType === "full"
                        ? "none"
                        : fillType === "three-quarter"
                          ? "polygon(0 0, 75% 0, 75% 100%, 0 100%)"
                          : fillType === "half"
                            ? "polygon(0 0, 50% 0, 50% 100%, 0 100%)"
                            : "polygon(0 0, 25% 0, 25% 100%, 0 100%)",
                  }}
                >
                  <HeartSolidIcon 
                    className="h-5 w-5 text-red-400"
                    style={{ 
                      filter: "drop-shadow(0 0 3px rgba(248, 113, 113, 0.6))" 
                    }}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>
    );
  };
  
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
        "overflow-hidden transition-all bg-black/80 border border-blue-500/30 backdrop-blur-sm",
        expanded && "ring-2 ring-blue-400/30"
      )}>
        <div 
          className="cursor-pointer relative" 
          onClick={toggleExpanded}
          style={{
            backgroundImage: expanded ? 
              "radial-gradient(circle at 50% 10%, rgba(59, 130, 246, 0.1), transparent 70%)" : 
              "none"
          }}>
          <CardHeader className="p-5 pb-0">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center mb-1.5">                <CardTitle className="text-lg text-blue-300 font-mono">
                  <span className="relative inline-block">
                    {job.title}
                    <span className="absolute top-0 left-0 -ml-0.5 text-red-400 opacity-30">
                      {job.title}
                    </span>
                  </span>
                </CardTitle>
                  <Badge 
                    variant="outline" 
                    className={cn(
                      "ml-2",
                      getDifficultyColor(getDifficulty(scoreValue))
                    )}
                  >
                    {getDifficulty(scoreValue).toUpperCase()}
                  </Badge>                  {job.new_grad_friendly && (
                    <Badge variant="secondary" className="ml-2 bg-cyan-900/30 text-cyan-400 border-cyan-500">
                      NEW GRAD
                    </Badge>
                  )}
                </div>
                  <CardDescription className="flex flex-wrap items-center text-sm mb-3 text-blue-200/70">
                  <div className="flex items-center mr-4">
                    <BriefcaseIcon className="h-4 w-4 mr-1 text-blue-400" />
                    <span>{job.company}</span>
                  </div>
                  
                  {job.location && (
                    <div className="flex items-center">
                      <MapPinIcon className="h-4 w-4 mr-1 text-blue-400" />
                      <span>{job.location}</span>
                    </div>
                  )}
                  
                  {job.date_posted && (
                    <span className="hidden sm:inline-block ml-4 text-cyan-400/80 border-l border-cyan-900/50 pl-3">
                      {job.date_posted}
                    </span>
                  )}
                </CardDescription>
              </div>
                <div className="flex flex-col items-end ml-4">
                <Badge variant="outline"
                className={cn(
                  "px-3 py-1.5",
                  badgeStyle.bgColor,
                  badgeStyle.textColor,
                  "border",
                  badgeStyle.borderColor,
                  "hover:" + badgeStyle.bgColor
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
            <div className="flex justify-between items-center mb-3 mt-1">
              <div>
                {renderHearts(scoreValue)}
              </div>
              <div className="text-xs text-muted-foreground">
                Match Score: {formattedScore}
              </div>
            </div>            <div className="text-sm text-blue-200/80 mb-4 border-l-2 border-blue-500/30 pl-3">
              {expanded ? job.description : truncatedDescription}
            </div>
            
            {!expanded && (
              <div className="flex items-center justify-between mt-1">                <div className="flex flex-wrap gap-1">
                  {job.matched_skills?.slice(0, 3).map((skill, i) => (
                    <Badge key={i} variant="outline" className="bg-lime-900/30 text-lime-400 border-lime-500 hover:bg-lime-900/50">
                      {skill}
                    </Badge>
                  ))}
                  {job.matched_skills && job.matched_skills.length > 3 && (
                    <Badge variant="outline" className="bg-blue-900/30 text-blue-400 border-blue-500 hover:bg-blue-900/50">
                      +{job.matched_skills.length - 3} more
                    </Badge>
                  )}
                </div>                <div className="flex items-center text-blue-400 text-sm font-medium">
                  <span className="mr-1 relative">
                    <span>{expanded ? 'COLLAPSE' : 'EXPAND DATA'}</span>
                    <span className="absolute top-0 left-0 -ml-0.5 text-red-400 opacity-30">
                      {expanded ? 'COLLAPSE' : 'EXPAND DATA'}
                    </span>
                  </span>
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
          <CardContent className="px-5 pb-5 border-t border-muted pt-3">            {/* Skills section */}
            <div className="mb-5">
              <h4 className="text-sm font-medium mb-3 text-blue-300 border-b border-blue-500/30 pb-2">NEURAL SKILL ANALYSIS</h4>
              <div className="space-y-3">
                {job.matched_skills && job.matched_skills.length > 0 && (
                  <div>
                    <h5 className="text-xs font-medium text-lime-400 mb-2 flex items-center gap-1">
                      <span className="h-1.5 w-1.5 rounded-full bg-lime-500 inline-block"></span> 
                      COMPATIBLE SKILLS
                    </h5>
                    <div className="flex flex-wrap gap-2">                      {job.matched_skills.map((skill, i) => (
                        <Badge key={i} variant="outline" className="bg-lime-900/30 text-lime-400 border-lime-500 hover:bg-lime-900/50">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                
                {job.missing_skills && job.missing_skills.length > 0 && (
                  <div className="mt-3">
                    <h5 className="text-xs font-medium text-red-400 mb-2 flex items-center gap-1">
                      <span className="h-1.5 w-1.5 rounded-full bg-red-500 inline-block"></span>
                      SKILLS TO ACQUIRE
                    </h5>
                    <div className="flex flex-wrap gap-2">
                      {job.missing_skills.map((skill, i) => (
                        <Badge key={i} variant="outline" className="bg-red-900/30 text-red-400 border-red-500 hover:bg-red-900/50">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
              {/* Additional details */}
            <div className="grid grid-cols-2 gap-4 mb-5 mt-6 border-t border-blue-500/20 pt-4">
              {job.experience_level && (
                <div className="border border-blue-500/30 bg-blue-900/10 p-3 rounded-sm">
                  <h5 className="text-xs font-medium text-blue-400">EXP. REQUIREMENT</h5>
                  <p className="text-sm text-blue-200 mt-1 font-mono">{job.experience_level}</p>
                </div>
              )}
              
              {job.salary_range && (
                <div className="border border-blue-500/30 bg-blue-900/10 p-3 rounded-sm">
                  <h5 className="text-xs font-medium text-blue-400">COMPENSATION</h5>
                  <p className="text-sm text-blue-200 mt-1 font-mono">{job.salary_range}</p>
                </div>
              )}
            </div>
              {/* Action buttons */}
            <CardFooter className="px-0 pt-3 flex justify-between items-center border-t border-blue-500/20">
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={toggleExpanded}
                className="flex items-center text-blue-400 hover:bg-blue-900/30 hover:text-blue-300"
              >
                <ChevronUpIcon className="h-4 w-4 mr-1" />
                <span>COLLAPSE</span>
              </Button>
              
              <div className="space-x-3">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={toggleSaved}
                  className={cn(
                    "border border-blue-500/50 bg-blue-900/20 text-blue-300 hover:bg-blue-800/30",
                    isSaved && "bg-yellow-900/30 text-yellow-400 hover:bg-yellow-900/50 border-yellow-500/50"
                  )}
                >
                  <span className="relative">
                    {isSaved ? 'SAVED' : 'SAVE'}
                    <span className="absolute top-0 left-0 -ml-0.5 text-red-400 opacity-30">
                      {isSaved ? 'SAVED' : 'SAVE'}
                    </span>
                  </span>
                </Button>
                
                {job.url && (
                  <Button
                    size="sm"
                    onClick={handleApply}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-medium border-none"
                    style={{
                      textShadow: "0 0 5px rgba(59, 130, 246, 0.8)"
                    }}
                  >
                    <span className="relative">
                      APPLY NOW
                      <span className="absolute top-0 left-0 -ml-0.5 text-red-400 opacity-20">
                        APPLY NOW
                      </span>
                    </span>
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
