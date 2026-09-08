import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { X, Building2 } from 'lucide-react';
import { companySchema, type CompanyFormData, type CompanyItem } from '../../schemas/company.schema';

interface CompanyModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (data: CompanyFormData) => void;
  initialData?: CompanyItem | null;
}

export const CompanyModal: React.FC<CompanyModalProps> = ({
  isOpen,
  onClose,
  onSave,
  initialData,
}) => {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<CompanyFormData>({
    resolver: zodResolver(companySchema),
    defaultValues: {
      name: '',
      sector: '',
      lastActivity: 'Hoje, 10:00',
      mainContact: '',
      status: 'Ativo',
      description: '',
      iconType: 'building',
      isLinkedToUser: true,
    },
  });

  useEffect(() => {
    if (initialData) {
      reset({
        name: initialData.name,
        sector: initialData.sector,
        lastActivity: initialData.lastActivity,
        mainContact: initialData.mainContact,
        status: initialData.status,
        description: initialData.description,
        iconType: initialData.iconType,
        isLinkedToUser: initialData.isLinkedToUser,
        id: initialData.id,
      });
    } else {
      reset({
        name: '',
        sector: '',
        lastActivity: 'Hoje, 10:00',
        mainContact: '',
        status: 'Ativo',
        description: '',
        iconType: 'building',
        isLinkedToUser: true,
      });
    }
  }, [initialData, reset, isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs">
      <div className="relative w-full max-w-lg bg-[#FAF6F0] rounded-3xl border-[2px] border-[#1F1E1C] shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200">
        
        {/* Header do Modal */}
        <div className="flex items-center justify-between px-6 py-5 border-b border-[#E3DBD0] bg-[#EFE8DC]">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-[#BA5827] flex items-center justify-center text-white">
              <Building2 className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-[#3B2317]">
              {initialData ? 'Editar Empresa' : 'Adicionar Nova Empresa'}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-[#7D7068] hover:text-[#3B2317] hover:bg-black/5 rounded-full transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Formulário */}
        <form onSubmit={handleSubmit(onSave)} className="p-6 space-y-4">
          {/* Nome da Empresa */}
          <div>
            <label className="block text-xs font-semibold text-[#48372F] mb-1.5 ml-1">
              Nome da Empresa
            </label>
            <input
              type="text"
              placeholder="Ex: Oliveira & Filhos"
              {...register('name')}
              className={`w-full px-4 py-2.5 bg-[#F4F1EA] border ${
                errors.name ? 'border-red-400' : 'border-[#BACBB9]'
              } rounded-xl text-sm text-[#3B2317] focus:outline-none focus:ring-2 focus:ring-[#77917B]/20`}
            />
            {errors.name && (
              <p className="text-xs text-red-500 mt-1 ml-1">{errors.name.message}</p>
            )}
          </div>

          {/* Ramo de Atividade */}
          <div>
            <label className="block text-xs font-semibold text-[#48372F] mb-1.5 ml-1">
              Ramo de Atividade
            </label>
            <input
              type="text"
              placeholder="Ex: Consultoria Agrícola, Construção Civil..."
              {...register('sector')}
              className={`w-full px-4 py-2.5 bg-[#F4F1EA] border ${
                errors.sector ? 'border-red-400' : 'border-[#BACBB9]'
              } rounded-xl text-sm text-[#3B2317] focus:outline-none focus:ring-2 focus:ring-[#77917B]/20`}
            />
            {errors.sector && (
              <p className="text-xs text-red-500 mt-1 ml-1">{errors.sector.message}</p>
            )}
          </div>

          {/* Contato Principal */}
          <div>
            <label className="block text-xs font-semibold text-[#48372F] mb-1.5 ml-1">
              Contato Principal
            </label>
            <input
              type="text"
              placeholder="Ex: Maria Ferreira"
              {...register('mainContact')}
              className={`w-full px-4 py-2.5 bg-[#F4F1EA] border ${
                errors.mainContact ? 'border-red-400' : 'border-[#BACBB9]'
              } rounded-xl text-sm text-[#3B2317] focus:outline-none focus:ring-2 focus:ring-[#77917B]/20`}
            />
            {errors.mainContact && (
              <p className="text-xs text-red-500 mt-1 ml-1">{errors.mainContact.message}</p>
            )}
          </div>

          {/* Última Atividade */}
          <div>
            <label className="block text-xs font-semibold text-[#48372F] mb-1.5 ml-1">
              Última Atividade
            </label>
            <input
              type="text"
              placeholder="Ex: 27 Out, 16:30"
              {...register('lastActivity')}
              className={`w-full px-4 py-2.5 bg-[#F4F1EA] border ${
                errors.lastActivity ? 'border-red-400' : 'border-[#BACBB9]'
              } rounded-xl text-sm text-[#3B2317] focus:outline-none focus:ring-2 focus:ring-[#77917B]/20`}
            />
          </div>

          {/* Botões de Ação */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-[#E3DBD0]">
            <button
              type="button"
              onClick={onClose}
              className="px-5 py-2.5 text-xs font-semibold text-[#685A52] hover:bg-[#EAE4D9] rounded-full transition-colors cursor-pointer"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="px-6 py-2.5 bg-[#BA5827] hover:bg-[#A14A1E] text-white text-xs font-semibold rounded-full shadow-md transition-all cursor-pointer"
            >
              {initialData ? 'Salvar Alterações' : 'Adicionar Empresa'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
