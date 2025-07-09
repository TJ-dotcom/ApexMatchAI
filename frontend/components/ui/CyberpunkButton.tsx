import React from "react";
import clsx from "clsx";

interface CyberpunkButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
}

export const CyberpunkButton: React.FC<CyberpunkButtonProps> = ({ children, className, ...props }) => (
  <button
    {...props}
    className={clsx(
      "relative px-6 py-2 font-bold uppercase tracking-wider text-cyan-200 bg-[#232946] border border-cyan-400 rounded-lg overflow-hidden transition-all duration-200 hover:bg-cyan-900 hover:text-pink-400 focus:outline-none",
      "before:absolute before:inset-0 before:bg-gradient-to-r before:from-cyan-400/30 before:to-pink-400/20 before:opacity-0 hover:before:opacity-100 before:transition-opacity before:duration-300",
      "after:absolute after:inset-0 after:pointer-events-none after:bg-[repeating-linear-gradient(90deg,transparent,transparent_2px,#00fff7_2px,#00fff7_4px)] after:opacity-10",
      className
    )}
  >
    <span className="relative z-10">{children}</span>
  </button>
);

export default CyberpunkButton;
