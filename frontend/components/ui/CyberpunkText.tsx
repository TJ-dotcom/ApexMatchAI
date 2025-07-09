import React from "react";
import clsx from "clsx";

interface CyberpunkTextProps {
  children: React.ReactNode;
  className?: string;
}

export const CyberpunkText: React.FC<CyberpunkTextProps> = ({ children, className }) => (
  <span
    className={clsx(
      "font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 via-pink-400 to-yellow-300 animate-cyberpunk-glow drop-shadow-cyberpunk",
      className
    )}
  >
    {children}
  </span>
);

export default CyberpunkText;
