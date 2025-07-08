import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface ProgressIndicatorProps {
  active: boolean;
  message?: string;
}

const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({ 
  active, 
  message = 'Processing your resume and matching with job listings...' 
}) => {
  const [dots, setDots] = useState('');
  const [step, setStep] = useState(1);
  const [stepText, setStepText] = useState('Analyzing your resume...');
  const [progress, setProgress] = useState(10);
  
  // Define steps
  const steps = [
    {
      number: 1,
      title: 'Analysis',
      description: 'Analyzing your resume and extracting skills...'
    },
    {
      number: 2,
      title: 'Scraping',
      description: 'Scraping job listings and processing requirements...'
    },
    {
      number: 3,
      title: 'Matching',
      description: 'Calculating match scores and ranking job opportunities...'
    }
  ];
  
  useEffect(() => {
    if (!active) return;
    
    // Animation for dots
    const dotsInterval = setInterval(() => {
      setDots(prev => {
        if (prev.length >= 3) return '';
        return prev + '.';
      });
    }, 500);
    
    // Animation for steps
    const stepsInterval = setInterval(() => {
      setStep(prev => {
        const newStep = prev >= 3 ? 1 : prev + 1;
        
        // Update step text
        switch (newStep) {
          case 1:
            setStepText('Analyzing your resume and extracting skills...');
            setProgress(30);
            break;
          case 2:
            setStepText('Scraping job listings and processing requirements...');
            setProgress(60);
            break;
          case 3:
            setStepText('Calculating match scores and ranking job opportunities...');
            setProgress(90);
            break;
          default:
            setStepText('Processing...');
        }
        
        return newStep;
      });
    }, 5000);
    
    return () => {
      clearInterval(dotsInterval);
      clearInterval(stepsInterval);
    };
  }, [active]);
  
  if (!active) return null;
  
  return (
    <Card className="w-full max-w-3xl mx-auto overflow-hidden my-6">
      <CardHeader className="pb-3">
        <CardTitle className="text-lg">Finding your perfect job matches</CardTitle>
      </CardHeader>
      
      <CardContent>
        {/* Animated progress bar */}
        <motion.div
          className="relative h-2 rounded-full bg-muted overflow-hidden my-4"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <motion.div 
            className="absolute h-full bg-primary rounded-full"
            initial={{ width: "5%" }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.8, ease: "easeInOut" }}
          />
        </motion.div>
        
        <div className="text-center text-sm text-muted-foreground mt-2 mb-6">
          {stepText}{dots}
        </div>
        
        {/* Steps */}
        <div className="flex items-center justify-between mb-2 px-2">
          {steps.map((s) => (
            <div key={s.number} className="flex flex-col items-center">
              <div 
                className={cn(
                  "w-10 h-10 rounded-full flex items-center justify-center mb-2 border-2",
                  step === s.number 
                    ? "border-primary bg-primary/10 text-primary"
                    : step > s.number
                      ? "border-primary bg-primary text-primary-foreground"
                      : "border-muted bg-muted/50 text-muted-foreground"
                )}
              >
                {step > s.number ? (
                  <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="lucide lucide-check">
                    <polyline points="20 6 9 17 4 12" />
                  </svg>
                ) : (
                  s.number
                )}
              </div>
              
              <p className={cn(
                "text-xs font-medium",
                step === s.number 
                  ? "text-primary"
                  : step > s.number
                    ? "text-primary"
                    : "text-muted-foreground"
              )}>
                {s.title}
              </p>
            </div>
          ))}
        </div>
        
        {/* Step connector */}
        <div className="flex items-center justify-center px-10 relative h-1 mt-2 mb-8">
          <div className="absolute top-1/2 left-0 right-0 h-0.5 bg-muted transform -translate-y-1/2"></div>
          <div 
            className="absolute top-1/2 left-0 h-0.5 bg-primary transform -translate-y-1/2"
            style={{ width: `${Math.max(0, ((step - 1) / 2) * 100)}%` }}
          ></div>
        </div>
        
        {/* Processing animation */}
        <div className="flex items-center justify-center mb-2">
          <div className="relative">
            <svg className="animate-spin h-8 w-8 text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            
            <div className="absolute inset-0 flex items-center justify-center">
              <Badge variant="outline" className="h-5 w-5 rounded-full p-0 flex items-center justify-center">
                {step}
              </Badge>
            </div>
          </div>
        </div>
        
        <p className="text-center text-sm text-muted-foreground">
          {message}
        </p>
      </CardContent>
    </Card>
  );
};

export default ProgressIndicator;
