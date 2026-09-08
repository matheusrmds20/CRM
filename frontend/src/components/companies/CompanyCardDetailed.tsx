import React from 'react';
import { TreePine, Cog, Sparkles, Shirt, Cpu, Building, Edit2, Trash2 } from 'lucide-react';
import { type CompanyItem } from '../../schemas/company.schema';

interface CompanyCardDetailedProps {
  company: CompanyItem;
  isAdmin?: boolean;
  onEdit?: (company: CompanyItem) => void;
  onDelete?: (id: string) => void;
}

const statusColorMap: Record<CompanyItem['status'], { bg: string; text: string }> = {
  'Parceiro Ativo': { bg: 'bg-[#536E58]', text: 'text-white' },
  'Ativo': { bg: 'bg-[#5E7A63]', text: 'text-white' },
  'Pendente': { bg: 'bg-[#C26B33]', text: 'text-white' },
  'Parceria': { bg: 'bg-[#98471D]', text: 'text-white' },
};

export const CompanyCardDetailed: React.FC<CompanyCardDetailedProps> = ({
  company,
  isAdmin = false,
  onEdit,
  onDelete,
}) => {
  const statusStyle = statusColorMap[company.status] || { bg: 'bg-stone-500', text: 'text-white' };

  const renderIcon = () => {
    switch (company.iconType) {
      case 'tree':
        return (
          <div className="w-12 h-12 rounded-full bg-[#E5EADF] flex items-center justify-center border border-[#BACBB9]">
            <TreePine className="w-7 h-7 text-[#495F4D]" />
          </div>
        );
      case 'gear':
        return (
          <div className="w-12 h-12 rounded-full bg-[#EFE8DC] flex items-center justify-center border border-[#DFD6C7]">
            <Cog className="w-7 h-7 text-[#3B2317]" />
          </div>
        );
      case 'novo':
        return (
          <div className="w-12 h-12 rounded-full bg-[#EFE8DC] flex items-center justify-center border border-[#DFD6C7]">
            <Sparkles className="w-7 h-7 text-[#3B2317]" />
          </div>
        );
      case 'textil':
        return (
          <div className="w-12 h-12 rounded-full bg-[#E5EADF] flex items-center justify-center border border-[#BACBB9]">
            <Shirt className="w-7 h-7 text-[#495F4D]" />
          </div>
        );
      case 'tech':
        return (
          <div className="w-12 h-12 rounded-full bg-[#E5EADF] flex items-center justify-center border border-[#BACBB9]">
            <Cpu className="w-7 h-7 text-[#495F4D]" />
          </div>
        );
      case 'building':
      default:
        return (
          <div className="w-12 h-12 rounded-full bg-[#EFE8DC] flex items-center justify-center border border-[#DFD6C7]">
            <Building className="w-7 h-7 text-[#3B2317]" />
          </div>
        );
    }
  };

  return (
    <div className="relative bg-[#EFE8DC] rounded-3xl p-6 border border-[#DFD6C7] shadow-sm hover:shadow-md transition-all flex flex-col justify-between overflow-hidden group min-h-[190px]">
      {/* Ondas decorativas no canto superior direito */}
      <div className="absolute top-0 right-0 w-28 h-28 pointer-events-none opacity-20">
        <svg viewBox="0 0 100 100" fill="none" stroke="#685A52" strokeWidth="1">
          <ellipse cx="100" cy="0" rx="30" ry="30" strokeDasharray="3 3" />
          <ellipse cx="100" cy="0" rx="55" ry="55" strokeDasharray="3 3" />
          <ellipse cx="100" cy="0" rx="80" ry="80" strokeDasharray="3 3" />
        </svg>
      </div>

      <div>
        {/* Topo do Card com Ícone e Nome */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3.5">
            {renderIcon()}
            <h4 className="font-bold text-[#3B2317] text-lg leading-snug">
              {company.name}
            </h4>
          </div>

          {/* Botões de Ação para Admin */}
          {isAdmin && (
            <div className="flex items-center gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity bg-white/60 backdrop-blur-xs p-1 rounded-xl shadow-xs">
              <button
                onClick={() => onEdit && onEdit(company)}
                title="Editar Empresa"
                className="p-1.5 text-[#5A4B42] hover:text-[#B75828] hover:bg-white rounded-lg transition-colors cursor-pointer"
              >
                <Edit2 className="w-4 h-4" />
              </button>
              <button
                onClick={() => onDelete && onDelete(company.id)}
                title="Excluir Empresa"
                className="p-1.5 text-[#5A4B42] hover:text-red-600 hover:bg-white rounded-lg transition-colors cursor-pointer"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>

        {/* Badge de Status */}
        <div className="flex items-center gap-2 mb-3">
          <span className="text-xs font-semibold text-[#5A4B42]">Status:</span>
          <span className={`text-xs px-3 py-0.5 rounded-full font-medium ${statusStyle.bg} ${statusStyle.text}`}>
            {company.status}
          </span>
        </div>

        {/* Descrição da Empresa */}
        <p className="text-xs sm:text-sm text-[#5B4C44] leading-relaxed">
          {company.description}
        </p>
      </div>
    </div>
  );
};
