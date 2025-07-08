import React, { ButtonHTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

interface CyberpunkButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'destructive' | 'success' | 'warning' | 'orange';
  size?: 'sm' | 'md' | 'lg' | 'xl';
  glowEffect?: boolean;
  scanLine?: boolean;
  isLoading?: boolean;
  loadingText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const CyberpunkButton: React.FC<CyberpunkButtonProps> = ({
  children,
  className,
  variant = 'primary',
  size = 'md',
  glowEffect = true,
  scanLine = true,
  isLoading = false,
  loadingText = 'PROCESSING...',
  leftIcon,
  rightIcon,
  ...props
}) => {
  // Variant styles
  const variantStyles = {
    primary: 'bg-gradient-to-r from-blue-800 to-indigo-900 hover:from-blue-700 hover:to-indigo-800 text-white border-blue-500',
    secondary: 'bg-gradient-to-r from-gray-800 to-gray-900 hover:from-gray-700 hover:to-gray-800 text-blue-300 border-gray-600',
    destructive: 'bg-gradient-to-r from-red-800 to-pink-900 hover:from-red-700 hover:to-pink-800 text-white border-red-500',
    success: 'bg-gradient-to-r from-green-800 to-teal-900 hover:from-green-700 hover:to-teal-800 text-white border-green-500',
    warning: 'bg-gradient-to-r from-orange-700 to-amber-800 hover:from-orange-600 hover:to-amber-700 text-white border-orange-500',
    orange: 'bg-gradient-to-r from-orange-500 via-red-500 to-orange-600 hover:from-orange-400 hover:via-red-400 hover:to-orange-500 text-white border-orange-500',
  };

  // Size styles
  const sizeStyles = {
    sm: 'px-3 py-1 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg',
    xl: 'px-6 py-3 text-xl font-bold',
  };

  // Glow effect based on variant
  const glowStyles = glowEffect
    ? variant === 'primary'
      ? 'neon-border-blue'
      : variant === 'destructive'
      ? 'neon-border-red'
      : variant === 'success'
      ? 'neon-border-green'
      : variant === 'orange'
      ? 'shadow-[0_0_15px_rgba(234,88,12,0.5)]'
      : ''
    : '';

  return (
    <button
      className={cn(
        'relative border-2 rounded-md font-medium tracking-wide transition-all duration-300 font-mono transform hover:scale-105 active:scale-95',
        variantStyles[variant],
        sizeStyles[size],
        glowStyles,
        scanLine ? 'scan-line' : '',
        isLoading ? 'opacity-80 cursor-not-allowed' : '',
        className
      )}
      disabled={isLoading || props.disabled}
      {...props}
    >
      <div className="flex items-center justify-center gap-2">
        {isLoading ? (
          <>
            <span className="data-indicator"></span>
            <span>{loadingText}</span>
          </>
        ) : (
          <>
            {leftIcon && <span>{leftIcon}</span>}
            <span className="glitch-text">
              <span className="glitch-offset text-pink-500">{children}</span>
              {children}
            </span>
            {rightIcon && <span>{rightIcon}</span>}
          </>
        )}
      </div>
      
      {/* Scan line animation */}
      {scanLine && (
        <div className="absolute inset-0 overflow-hidden rounded-md pointer-events-none">
          <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent transform -skew-x-12 -translate-x-full animate-scanner"></div>
        </div>
      )}
    </button>
  );
};

export default CyberpunkButton;
