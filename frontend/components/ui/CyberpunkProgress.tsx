import React from "react";

interface CyberpunkProgressProps {
  step: number;
  totalSteps: number;
  label?: string;
}

export const CyberpunkProgress: React.FC<CyberpunkProgressProps> = ({ step, totalSteps, label }) => {
  const percent = Math.round((step / totalSteps) * 100);
  return (
    <div className="w-full flex flex-col items-center gap-2">
      {label && <span className="text-cyan-300 font-mono text-sm mb-1 animate-cyberpunk-glow">{label}</span>}
      <div className="relative w-full h-6 bg-[#181825] rounded-lg overflow-hidden border-2 border-cyan-400 shadow-cyberpunk">
        <div
          className="absolute left-0 top-0 h-full bg-gradient-to-r from-cyan-400 via-pink-400 to-yellow-300 animate-pulse"
          style={{ width: `${percent}%`, transition: 'width 0.5s cubic-bezier(0.4,0,0.2,1)' }}
        />
        <div className="absolute inset-0 flex items-center justify-center font-mono text-cyan-200 text-xs tracking-widest">
          {step} / {totalSteps} [{percent}%]
        </div>
      </div>
      <div className="flex gap-1 mt-1">
        {Array.from({ length: totalSteps }).map((_, i) => (
          <span
            key={i}
            className={`w-4 h-1 rounded-full ${i < step ? 'bg-cyan-400' : 'bg-gray-700'} transition-all duration-300`}
          />
        ))}
      </div>
    </div>
  );
};

export default CyberpunkProgress;
