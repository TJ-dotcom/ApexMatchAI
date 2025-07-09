import { Toaster, toast } from "sonner";
import React from "react";

export const CyberpunkToaster = () => (
  <Toaster
    position="top-center"
    toastOptions={{
      className: "bg-[#232946] border-2 border-cyan-400 text-cyan-200 font-mono shadow-cyberpunk animate-cyberpunk-glow",
      style: { boxShadow: "0 0 24px 4px #00fff7, 0 0 2px 1px #ff00cc inset" },
    }}
  />
);

export { toast };
