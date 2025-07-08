import { useEffect, useState, useRef } from 'react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

interface ProgressIndicatorProps {
  active: boolean;
  message?: string;
}

// Helper function for cyberpunk effects
const getBlipColor = (color: string) => {
  switch (color) {
    case "red": return "bg-red-400";
    case "orange": return "bg-orange-400";
    case "yellow": return "bg-yellow-400";
    case "lime": return "bg-lime-400";
    case "green": default: return "bg-green-400";
  }
};

const getBlipShadow = (color: string) => {
  switch (color) {
    case "red": return "0 0 8px rgba(248, 113, 113, 0.8)";
    case "orange": return "0 0 8px rgba(251, 146, 60, 0.8)";
    case "yellow": return "0 0 8px rgba(250, 204, 21, 0.8)";
    case "lime": return "0 0 8px rgba(163, 230, 53, 0.8)";
    case "green": default: return "0 0 8px rgba(74, 222, 128, 0.8)";
  }
};

const ProgressIndicator: React.FC<ProgressIndicatorProps> = ({ 
  active, 
  message = 'Processing your resume and matching with job listings...' 
}) => {
  const [dots, setDots] = useState('');
  const [step, setStep] = useState(1);
  const [stepText, setStepText] = useState('Scanning resume data...');
  const [progress, setProgress] = useState(10);
  const [glitchText, setGlitchText] = useState('PROCESSING');
  const [radarAngle, setRadarAngle] = useState(0);
  const [anomalyBlips, setAnomalyBlips] = useState<Array<{
    id: number;
    x: number;
    y: number;
    size: number;
    opacity: number;
    color: string;
  }>>([]);
  const radarRef = useRef<HTMLDivElement>(null);
  
  // Define steps with cyberpunk terms
  const steps = [
    {
      number: 1,
      title: 'SCANNING',
      description: 'Scanning neural network for skills extraction...'
    },
    {
      number: 2,
      title: 'INFILTRATING',
      description: 'Infiltrating corporate databases and bypassing firewalls...'
    },
    {
      number: 3,
      title: 'CALCULATING',
      description: 'Calculating match probabilities and constructing network map...'
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
            setStepText('Scanning resume data and extracting neural patterns...');
            setProgress(30);
            setGlitchText('SCANNING');
            break;
          case 2:
            setStepText('Infiltrating corporate databases and accessing job listings...');
            setProgress(60);
            setGlitchText('INFILTRATING');
            break;
          case 3:
            setStepText('Calculating match probabilities and ranking potential targets...');
            setProgress(90);
            setGlitchText('CALCULATING');
            break;
          default:
            setStepText('Processing...');
        }
        
        return newStep;
      });
    }, 5000);
    
    // Radar animation
    const radarInterval = setInterval(() => {
      setRadarAngle((prev) => (prev + 2) % 360);
    }, 50);

    // Generate anomaly blips
    const generateAnomalies = () => {      if (active) {
        const newAnomalies: Array<{
          id: number;
          x: number;
          y: number;
          size: number;
          opacity: number;
          color: string;
        }> = [];
        const count = Math.floor(Math.random() * 3) + 1; // 1-3 anomalies

        for (let i = 0; i < count; i++) {
          const angle = Math.random() * Math.PI * 2;
          const distance = Math.random() * 0.9;
          const x = 50 + Math.cos(angle) * distance * 50;
          const y = 50 + Math.sin(angle) * distance * 50;

          // Different colors for different threat levels
          const colors = ["red", "orange", "yellow", "lime"];
          const color = colors[Math.floor(Math.random() * colors.length)];

          newAnomalies.push({
            id: Date.now() + i,
            x,
            y,
            size: Math.random() * 4 + 2, // Larger for anomalies
            opacity: 0.9,
            color,
          });
        }

        setAnomalyBlips((prev) =>
          [
            ...prev
              .filter((blip) => blip.opacity > 0.1)
              .map((blip) => ({
                ...blip,
                opacity: blip.opacity * 0.92,
              })),
            ...newAnomalies,
          ].slice(0, 15)
        );
      }
    };

    const anomalyInterval = setInterval(generateAnomalies, 800);
    
    // Glitch effect for title
    const glitchInterval = setInterval(() => {
      const glitchChars = "!@#$%^&*()_+-=[]{}|;:,.<>?";
      const original = glitchText;
      let glitched = "";

      for (let i = 0; i < original.length; i++) {
        if (Math.random() < 0.1) {
          glitched += glitchChars[Math.floor(Math.random() * glitchChars.length)];
        } else {
          glitched += original[i];
        }
      }

      setGlitchText(glitched);

      setTimeout(() => setGlitchText(original), 100);
    }, 2000);
    
    return () => {
      clearInterval(dotsInterval);
      clearInterval(stepsInterval);
      clearInterval(radarInterval);
      clearInterval(anomalyInterval);
      clearInterval(glitchInterval);
    };
  }, [active]);
    if (!active) return null;
  
  return (
    <div className="w-full max-w-3xl mx-auto bg-black/80 border border-blue-500/30 rounded-xl shadow-lg overflow-hidden my-6 backdrop-blur-sm">
      <div className="p-6">        <h2 className="text-lg font-medium text-blue-400 mb-6">
          <span className="relative">
            {glitchText} JOB NETWORKS{dots}
            <span className="absolute top-0 left-0 -ml-0.5 text-red-400 opacity-70">
              {glitchText} JOB NETWORKS{dots}
            </span>
          </span>
        </h2>
        
        {/* Radar display */}
        <div className="relative w-full h-40 mb-4 opacity-50">
          <div ref={radarRef} className="absolute inset-0 flex items-center justify-center">
            {/* Radar circles */}
            <div className="absolute inset-0 border-2 border-green-500/40 rounded-full"></div>
            <div className="absolute inset-[15%] border border-green-500/30 rounded-full"></div>
            <div className="absolute inset-[30%] border border-green-500/20 rounded-full"></div>
            <div className="absolute inset-[45%] border border-green-500/10 rounded-full"></div>

            {/* Radar sweep */}
            <div 
              className="absolute top-1/2 left-1/2 w-1/2 h-0.5 bg-green-500/60 origin-left"
              style={{ 
                transform: `translateX(-1px) translateY(-1px) rotate(${radarAngle}deg)`,
                boxShadow: "0 0 10px rgba(74, 222, 128, 0.8)"
              }}
            ></div>
            
            {/* Anomaly blips */}
            {anomalyBlips.map((blip) => (
              <div
                key={blip.id}
                className={`absolute rounded-full ${
                  blip.color === "red" ? "bg-red-400" :
                  blip.color === "orange" ? "bg-orange-400" :
                  blip.color === "yellow" ? "bg-yellow-400" :
                  blip.color === "lime" ? "bg-lime-400" :
                  "bg-green-400"
                }`}
                style={{
                  left: `${blip.x}%`,
                  top: `${blip.y}%`,
                  width: `${blip.size}px`,
                  height: `${blip.size}px`,
                  opacity: blip.opacity,
                  boxShadow: `0 0 8px rgba(${
                    blip.color === "red" ? "248, 113, 113" :
                    blip.color === "orange" ? "251, 146, 60" :
                    blip.color === "yellow" ? "250, 204, 21" :
                    blip.color === "lime" ? "163, 230, 53" :
                    "74, 222, 128"
                  }, 0.8)`,
                }}
              ></div>
            ))}
          </div>
        </div>
        
        {/* Animated progress bar */}<motion.div
          className="relative h-2 rounded-sm bg-gray-800 overflow-hidden my-4 border border-blue-500/30"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
        >
          <motion.div 
            className="absolute h-full bg-gradient-to-r from-blue-500 to-purple-600 rounded-sm"
            initial={{ width: "5%" }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.8, ease: "easeInOut" }}
          />
        </motion.div>
        
        {/* Steps indicator */}
        <div className="my-8">
          <div className="flex justify-between items-center mb-4">
            {steps.map((s, i) => (
              <div key={i} className="flex flex-col items-center relative">
                {/* Line between circles */}                {i < steps.length - 1 && (
                  <div className="absolute top-4 left-1/2 w-full h-0.5 bg-gray-800">
                    <motion.div 
                      className="h-full bg-blue-500" 
                      initial={{ width: "0%" }}
                      animate={{ width: step > s.number ? "100%" : "0%" }}
                      transition={{ duration: 0.5 }}
                    />
                  </div>
                )}
                  {/* Circle indicator */}
                <motion.div 
                  className={`z-10 flex items-center justify-center w-8 h-8 rounded-full border-2 ${
                    step === s.number 
                      ? 'border-blue-500 bg-blue-900/30' 
                      : step > s.number
                        ? 'border-blue-500 bg-blue-500/80'
                        : 'border-gray-700 bg-gray-900'
                  }`}
                  animate={{
                    scale: step === s.number ? [1, 1.1, 1] : 1
                  }}
                  transition={{
                    duration: 1,
                    repeat: step === s.number ? Infinity : 0,
                    repeatType: "reverse"
                  }}
                >
                  {step > s.number ? (
                    <svg className="w-4 h-4 text-blue-100" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  ) : (
                    <span className={`text-sm font-medium ${step === s.number ? 'text-blue-400' : 'text-gray-400'}`}>
                      {s.number}
                    </span>
                  )}
                </motion.div>
                  {/* Step title */}
                <div className="mt-2 text-center">
                  <p className={`text-sm font-medium ${step >= s.number ? 'text-blue-400' : 'text-gray-500'}`}>
                    {s.title}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
          {/* Current step description */}
        <div className="text-center">
          <motion.p 
            className="text-gray-300"
            key={step} // Force re-render on step change
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            {stepText}{dots}
          </motion.p>
          
          {/* Floating dots animation */}
          <div className="flex justify-center mt-6 space-x-2">
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                className="w-2.5 h-2.5 rounded-full bg-blue-500"
                style={{
                  boxShadow: "0 0 8px rgba(59, 130, 246, 0.8)"
                }}
                animate={{
                  y: [0, -10, 0],
                  opacity: [0.5, 1, 0.5]
                }}
                transition={{
                  duration: 1,
                  repeat: Infinity,
                  delay: i * 0.2
                }}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProgressIndicator;
