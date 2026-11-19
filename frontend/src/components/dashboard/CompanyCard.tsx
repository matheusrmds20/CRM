import React from 'react';
import { TreePine, Cog, Building, Sparkles } from 'lucide-react';

export interface Company {
  id: string;
  name: string;
  iconType: 'tree' | 'gear' | 'novo' | 'building';
}

export const CompanyCard: React.FC<{ company: Company }> = ({ company }) => {
  const renderIcon = () => {
    switch (company.iconType) {
      case 'tree':
        return <TreePine className="w-12 h-12 text-[#4A5D4E]" />;
      case 'gear':
        return <Cog className="w-12 h-12 text-[#3B2317]" />;
      case 'novo':
        return <Sparkles className="w-12 h-12 text-[#3B2317]" />;
      case 'building':
        return <Building className="w-12 h-12 text-[#3B2317]" />;
      default:
        return <Building className="w-12 h-12 text-[#3B2317]" />;
    }
  };

  return (
    <div className="flex flex-col items-center justify-center p-6 bg-transparent hover:bg-black/5 rounded-2xl transition-all cursor-pointer group">
      <div className="mb-3 transform group-hover:scale-110 transition-transform">
        {renderIcon()}
      </div>
      <span className="text-sm font-semibold text-[#3B2317] text-center">
        {company.name}
      </span>
    </div>
  );
};
