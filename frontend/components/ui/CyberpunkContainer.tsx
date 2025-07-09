import React from "react";
import clsx from "clsx";

interface CyberpunkContainerProps {
  children: React.ReactNode;
  className?: string;
}

export const CyberpunkContainer: React.FC<CyberpunkContainerProps> = ({ children, className }) => (
  <div
    className={clsx(
      "bg-gradient-to-br from-[#1a1a2e] via-[#232946] to-[#0f3460] border border-cyan-400/40 rounded-xl shadow-cyberpunk p-6 backdrop-blur-md",
      className
    )}
    style={{ boxShadow: "0 0 24px 4px #00fff7, 0 0 2px 1px #ff00cc inset" }}
  >
    {children}
  </div>
);

export default CyberpunkContainer;
