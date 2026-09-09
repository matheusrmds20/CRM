import React from 'react';
import { type LeadItem, type LeadStatus } from '../../schemas/lead.schema';

export type Lead = LeadItem;

interface LeadCardDetailedProps {
  lead: LeadItem;
  onClick?: (lead: LeadItem) => void;
}

const statusBadgeStyles: Record<LeadStatus, { bg: string; text: string }> = {
  'Novo': { bg: 'bg-[#98AE9D]', text: 'text-white' },
  'Em Contato': { bg: 'bg-[#C26B33]', text: 'text-white' },
  'Qualificado': { bg: 'bg-[#89A18E]', text: 'text-white' },
  'Negociação': { bg: 'bg-[#B75828]', text: 'text-white' },
  'Ganho': { bg: 'bg-[#98471D]', text: 'text-white' },
  'Perdido': { bg: 'bg-[#8D827A]', text: 'text-white' },
};

export const LeadCard: React.FC<LeadCardDetailedProps> = ({ lead, onClick }) => {
  const badgeStyle = statusBadgeStyles[lead.status] || { bg: 'bg-stone-500', text: 'text-white' };

  return (
    <div 
      onClick={() => onClick && onClick(lead)}
      className="relative bg-[#EFE8DC] rounded-3xl p-5 border border-[#DFD6C7] shadow-sm hover:shadow-md transition-all flex flex-col justify-between overflow-hidden cursor-pointer group min-h-[175px]"
    >
      {/* Ondas decorativas em SVG no canto superior direito */}
      <div className="absolute top-0 right-0 w-28 h-28 pointer-events-none opacity-25">
        <svg viewBox="0 0 100 100" fill="none" stroke="#685A52" strokeWidth="0.9">
          <ellipse cx="100" cy="0" rx="30" ry="30" strokeDasharray="3 3" />
          <ellipse cx="100" cy="0" rx="55" ry="55" strokeDasharray="3 3" />
          <ellipse cx="100" cy="0" rx="80" ry="80" strokeDasharray="3 3" />
        </svg>
      </div>

      <div>
        {/* Info do Contato */}
        <div className="flex items-center gap-3.5 mb-3.5">
          <div className="w-12 h-12 rounded-full bg-[#98AE9D] text-white font-bold flex items-center justify-center border-2 border-white shadow-sm shrink-0">
            {lead.name.charAt(0).toUpperCase()}
          </div>
          <div className="overflow-hidden">
            <h4 className="font-bold text-[#3B2317] text-base leading-tight truncate">
              {lead.name}
            </h4>
            <p className="text-xs text-[#7D7068] font-medium truncate mt-0.5">
              {lead.role} na {lead.company}
            </p>
          </div>
        </div>

        {/* Badge de Status */}
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xs font-semibold text-[#5A4B42]">Status:</span>
          <span className={`text-xs px-3 py-0.5 rounded-full font-medium shadow-2xs ${badgeStyle.bg} ${badgeStyle.text}`}>
            {lead.status}
          </span>
        </div>
      </div>

      {/* Datas */}
      <div className="flex items-center justify-between text-xs text-[#7D7068] font-medium border-t border-[#DFD6C7] pt-2.5 mt-1">
        <span>Data: {lead.date}</span>
        {lead.targetDate && <span>{lead.targetDate}</span>}
      </div>
    </div>
  );
};

export const LeadCardDetailed = LeadCard;
