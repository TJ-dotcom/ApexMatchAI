import React, { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface CyberpunkContainerProps {
  children: ReactNode;
  className?: string;
  variant?: 'default' | 'terminal' | 'card' | 'radar';
  glowColor?: 'blue' | 'red' | 'green' | 'pink' | 'orange';
  animate?: boolean;
  noise?: boolean;
  scanLine?: boolean;
}

const CyberpunkContainer: React.FC<CyberpunkContainerProps> = ({
  children,
  className = '',
  variant = 'default',
  glowColor = 'blue',
  noise = true,
  scanLine = true
}) => {
  // Map glow colors to their CSS classes
  const glowColorMap = {
    blue: 'neon-border-blue',
    red: 'neon-border-red',
    green: 'neon-border-green',
    pink: 'border-pink-500 shadow-[0_0_15px_rgba(236,72,153,0.5)]',
    orange: 'border-orange-500 shadow-[0_0_15px_rgba(234,88,12,0.5)]'
  };

  // Map variants to their base styles
  const variantStyles = {
    default: 'bg-gray-900 border-2 rounded-md p-4',
    terminal: 'bg-black border-2 p-4 rounded-md font-mono',
    card: 'bg-gray-900/80 backdrop-blur-xl border-2 rounded-xl p-6',
    radar: 'bg-black border-2 rounded-full relative overflow-hidden'
  };

  // Combine all classes
  const containerClasses = cn(
    variantStyles[variant],
    glowColorMap[glowColor],
    noise && 'noise',
    scanLine && 'scan-line',
    className
  );

  return (
    <div className={containerClasses}>
      {children}
    </div>
  );
};

export default CyberpunkContainer;
