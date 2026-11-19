import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { useState, useCallback, useRef } from 'react';
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
      cnpj: '',
      lastActivity: '',
      mainContact: '',
      status: 'Ativo',
      description: '',
      iconType: 'building',
      isLinkedToUser: true,
    },
  });

  const [isClosing, setIsClosing] = useState(false);
  const closeTimeoutRef = useRef<number | null>(null);
  const onCloseRef = useRef(onClose);

  useEffect(() => {
    onCloseRef.current = onClose;
  }, [onClose]);

  const closeModal = useCallback(() => {
    if (closeTimeoutRef.current !== null) window.clearTimeout(closeTimeoutRef.current);
    setIsClosing(true);
    closeTimeoutRef.current = window.setTimeout(() => {
      closeTimeoutRef.current = null;
      onCloseRef.current();
    }, 250);
  }, []);

  useEffect(() => {
    if (isOpen) {
      if (closeTimeoutRef.current !== null) window.clearTimeout(closeTimeoutRef.current);
      closeTimeoutRef.current = null;
      setIsClosing(false);
    }
    return () => {
      if (closeTimeoutRef.current !== null) window.clearTimeout(closeTimeoutRef.current);
    };
  }, [isOpen]);

  const handleFormSubmit = async (data: CompanyFormData) => {
    await onSave(data);
    closeModal();
  };

  useEffect(() => {
    if (initialData) {
      reset({
        name: initialData.name,
        
        cnpj: initialData.sector,
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
        cnpj: '',
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
    <div className={`fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-md ${isClosing ? 'animate-overlay-exit' : 'animate-overlay-fade'}`}>
      <div className={`relative w-full max-w-lg bg-[#FAF6F0] rounded-[2rem] border border-[#E3DBD0] shadow-[0_25px_60px_-15px_rgba(59,35,23,0.35)] overflow-hidden ${isClosing ? 'animate-modal-exit' : 'animate-modal-enter'} hover:shadow-[0_30px_70px_-15px_rgba(59,35,23,0.45)]`}>
        
        {}
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
            onClick={closeModal}
            className="p-1.5 text-[#7D7068] hover:text-[#3B2317] hover:bg-black/5 rounded-full transition-colors cursor-pointer"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Formulário */}
        <form onSubmit={handleSubmit(handleFormSubmit)} className="p-6 space-y-4">
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
                errors.name ? 'border-red-400' : 'border-[#B8AA9A]'
              } rounded-xl text-sm text-[#3B2317] focus:outline-none focus:ring-2 focus:ring-[#77917B]/20`}
            />
            {errors.name && (
              <p className="text-xs text-red-500 mt-1 ml-1">{errors.name.message}</p>
            )}
          </div>
          {}
          <div>
            <label className="block text-xs font-semibold text-[#48372F] mb-1.5 ml-1">
              CNPJ <span className="text-red-400">*</span>
            </label>
            <input
              type="text"
              placeholder="Ex: 11.222.333/0001-81"
              {...register('cnpj')}
              className={`w-full px-4 py-2.5 bg-[#F4F1EA] border ${
                errors.cnpj ? 'border-red-400' : 'border-[#B8AA9A]'
              } rounded-xl text-sm text-[#3B2317] focus:outline-none focus:ring-2 focus:ring-[#77917B]/20`}
            />
            <p className="text-[10px] text-[#8A7B72] mt-1 ml-1">Digite um CNPJ válido com ou sem pontuação.</p>
            {errors.cnpj && (
              <p className="text-xs text-red-500 mt-1 ml-1">{errors.cnpj.message}</p>
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
                errors.lastActivity ? 'border-red-400' : 'border-[#B8AA9A]'
              } rounded-xl text-sm text-[#3B2317] focus:outline-none focus:ring-2 focus:ring-[#77917B]/20`}
            />
          </div>

          {/* Botões de Ação */}
          <div className="flex items-center justify-end gap-3 pt-4 border-t border-[#E3DBD0]">
            <button
              type="button"
              onClick={closeModal}
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