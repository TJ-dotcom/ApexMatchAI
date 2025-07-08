import React, { ReactNode } from 'react';
import CyberpunkContainer from './ui/CyberpunkContainer';

interface MainLayoutProps {
  children: ReactNode;
  title?: string;
  subtitle?: string;
}

const MainLayout: React.FC<MainLayoutProps> = ({ 
  children,
  title = 'JOB SEARCH RESUME MATCHER',
  subtitle = 'AI-powered resume matching for the cyberpunk future'
}) => {
  return (
    <div className="min-h-screen cyberpunk-bg noise">
      {/* Military Radar - Background */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-[800px] h-[800px] relative opacity-20">
          {/* Radar circles */}
          <div className="absolute inset-0 border-2 border-green-500 rounded-full"></div>
          <div className="absolute inset-[15%] border border-green-500 rounded-full"></div>
          <div className="absolute inset-[30%] border border-green-500 rounded-full"></div>
          <div className="absolute inset-[45%] border border-green-500 rounded-full"></div>
          <div className="absolute inset-[60%] border border-green-500 rounded-full"></div>
          <div className="absolute inset-[75%] border border-green-500 rounded-full"></div>

          {/* Radar cross lines */}
          <div className="absolute top-1/2 left-0 right-0 h-px bg-green-500/50"></div>
          <div className="absolute top-0 bottom-0 left-1/2 w-px bg-green-500/50"></div>

          {/* Radar coordinates */}
          <div className="absolute top-1 left-1 text-green-500 text-xs font-mono">N 40°45'12.3"</div>
          <div className="absolute bottom-1 right-1 text-green-500 text-xs font-mono">E 73°58'44.1"</div>
          <div className="absolute top-1 right-1 text-green-500 text-xs font-mono">RANGE: 50KM</div>
          <div className="absolute bottom-1 left-1 text-green-500 text-xs font-mono">SYSTEM ACTIVE</div>
        </div>
      </div>

      {/* Grid Pattern */}
      <div className="absolute inset-0 opacity-5">
        <div
          className="absolute inset-0"
          style={{
            backgroundImage: `
            linear-gradient(rgba(255,165,0,0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,165,0,0.1) 1px, transparent 1px)
          `,
            backgroundSize: "50px 50px",
          }}
        />
      </div>

      {/* Rust/Damage Overlays */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-gradient-radial from-orange-900/20 to-transparent rounded-full blur-3xl" />
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-gradient-radial from-red-900/20 to-transparent rounded-full blur-3xl" />
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-gradient-radial from-orange-600/5 to-transparent rounded-full blur-3xl" />

      <div className="relative z-10 container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-12 animate-fade-in-up">
          <h1 className="text-6xl font-black bg-gradient-to-r from-orange-400 via-red-400 to-orange-600 bg-clip-text text-transparent font-mono tracking-wider glitch-text mb-4">
            {title}
          </h1>
          <p className="text-xl text-gray-300 max-w-4xl mx-auto leading-relaxed">
            {subtitle}
            <span className="text-orange-400 font-semibold"> Fortune favors the bold.</span>
          </p>
        </div>

        {/* Main content */}
        <div className="relative animate-fade-in">
          {children}
        </div>

        {/* Footer */}
        <div className="text-center mt-16 text-sm text-gray-500 animate-fade-in">
          <p>CYBERPUNK JOB SEARCH SYSTEM v2.0.77 • ALL RIGHTS RESERVED © 2077</p>
          <p className="mt-1">SECURE CONNECTION ESTABLISHED • ENCRYPTION LEVEL: MAXIMUM</p>
        </div>
      </div>
    </div>
  );
};

export default MainLayout;
