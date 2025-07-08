import * as React from 'react';
import { useCyberpunkEffect } from '@/src/lib/useCyberpunkEffect';
import { cn } from '@/lib/utils';

interface CyberpunkTextProps {
  text: string;
  as?: keyof React.JSX.IntrinsicElements;
  className?: string;
  variant?: 'glitch' | 'typing' | 'flicker' | 'color-cycle' | 'digital-distort';
  glitchColor?: string;
  animate?: boolean;
  enableGlitch?: boolean;
  glitchOptions?: {
    glitchProbability?: number;
    glitchDuration?: number;
    glitchInterval?: number;
    glitchCharacters?: string;
  };
}

const CyberpunkText: React.FC<CyberpunkTextProps> = ({
  text,
  as: Component = 'span',
  className = '',
  variant = 'glitch',
  glitchColor = '#ec4899', // Pink default
  animate = true,
  enableGlitch = true,
  glitchOptions = {}
}) => {
  const displayText = enableGlitch ? useCyberpunkEffect(text, glitchOptions) : text;

  // Classes based on variant
  const variantClasses = {
    glitch: 'glitch-text',
    typing: 'typing-text',
    flicker: 'flicker',
    'color-cycle': 'color-cycle',
    'digital-distort': 'digital-distort'
  };

  // Animation classes
  const animationClass = animate ? 'transform transition-all duration-300' : '';

  // Combine classes
  const combinedClassName = cn(className, variantClasses[variant], animationClass);

  return variant === 'glitch' ? (
    <Component className={combinedClassName}>
      <span className="glitch-offset" style={{ color: glitchColor }}>{displayText}</span>
      {displayText}
    </Component>
  ) : (
    <Component className={combinedClassName}>
      {displayText}
    </Component>
  );
};

export default CyberpunkText;
