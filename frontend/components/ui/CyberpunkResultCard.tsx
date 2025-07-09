import React from "react";
import { CyberpunkContainer, CyberpunkText } from ".";

interface CyberpunkResultCardProps {
  job: {
    title: string;
    company: string;
    location?: string;
    score: number;
    description?: string;
    url?: string;
  };
  index?: number;
}

export const CyberpunkResultCard: React.FC<CyberpunkResultCardProps> = ({ job, index }) => (
  <CyberpunkContainer className="mb-6 p-6 border-2 border-pink-400/60 shadow-cyberpunk bg-[#181825]/80">
    <div className="flex items-center gap-4 mb-2">
      <CyberpunkText className="text-2xl">{job.title}</CyberpunkText>
      <span className="text-cyan-300 font-mono text-xs px-2 py-1 rounded bg-cyan-900/40 border border-cyan-400 ml-auto">
        {job.score}% match
      </span>
    </div>
    <div className="text-pink-200 font-mono text-lg mb-1">{job.company}</div>
    {job.location && <div className="text-yellow-300 text-xs mb-2">{job.location}</div>}
    {job.description && <div className="text-cyan-100 text-sm mb-2 line-clamp-3">{job.description}</div>}
    {job.url && (
      <a
        href={job.url}
        target="_blank"
        rel="noopener noreferrer"
        className="inline-block mt-2 px-4 py-1 text-xs font-bold text-pink-300 border border-pink-400 rounded hover:bg-pink-400 hover:text-black transition-all duration-200"
      >
        View Job
      </a>
    )}
  </CyberpunkContainer>
);

export default CyberpunkResultCard;
