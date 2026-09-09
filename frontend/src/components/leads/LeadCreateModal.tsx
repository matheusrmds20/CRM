import React, { useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Building2, UserPlus, X } from 'lucide-react';
import { type CompanyApiResponse } from '../../services/companies.service';
import {
  leadCreateSchema,
  type LeadCreateFormData,
} from '../../schemas/lead.schema';

interface LeadCreateModalProps {
  companies: CompanyApiResponse[];
  isOpen: boolean;
  isSaving: boolean;
  onClose: () => void;
  onSave: (data: LeadCreateFormData) => Promise<void>;
}

export const LeadCreateModal: React.FC<LeadCreateModalProps> = ({
  companies,
  isOpen,
  isSaving,
  onClose,
  onSave,
}) => {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<LeadCreateFormData>({
    resolver: zodResolver(leadCreateSchema),
    defaultValues: {
      name: '',
      email: '',
      phone: '',
      companyId: undefined,
      subject: '',
      description: '',
      estimatedValue: 0,
      status: 'new',
    },
  });

  const [apiError, setApiError] = React.useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      reset();
      setApiError(null);
    }
  }, [isOpen, reset]);

  const submit = async (data: LeadCreateFormData) => {
    setApiError(null);
    try {
      await onSave({
        ...data,
        description: data.description?.trim() || undefined,
      });
    } catch (err: any) {
      const status = err?.response?.status;
      const detail = err?.response?.data?.detail;

      if (status === 409) {
        setApiError('Já existe um lead cadastrado com este e-mail.');
      } else if (detail) {
        setApiError(typeof detail === 'string' ? detail : 'Erro ao criar lead. Tente novamente.');
      } else {
        setApiError('Erro inesperado ao criar lead. Tente novamente.');
      }
    }
  };

  if (!isOpen) return null;

  const inputClass = (hasError: boolean) => `w-full px-4 py-2.5 bg-[#F4F1EA] border ${
    hasError ? 'border-red-400' : 'border-[#B8AA9A]'
  } rounded-xl text-sm text-[#3B2317] placeholder-[#8C7F76] focus:outline-none focus:ring-2 focus:ring-[#77917B]/20`;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-md">
      <div className="relative w-full max-w-2xl max-h-[92vh] overflow-y-auto bg-[#FAF6F0] rounded-[2rem] border border-[#E3DBD0] shadow-[0_25px_60px_-15px_rgba(59,35,23,0.35)] animate-modal-enter">
        <div className="sticky top-0 z-10 flex items-center justify-between px-6 py-5 border-b border-[#E3DBD0] bg-[#EFE8DC]">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-full bg-[#BA5827] flex items-center justify-center text-white">
              <UserPlus className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-bold text-[#3B2317]">Criar Novo Lead</h3>
          </div>
          <button
            type="button"
            aria-label="Fechar modal"
            onClick={onClose}
            disabled={isSaving}
            className="p-1.5 text-[#7D7068] hover:text-[#3B2317] hover:bg-black/5 rounded-full transition-colors cursor-pointer disabled:opacity-50"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit(submit)} className="p-6 space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-[#48372F] mb-1.5 ml-1">Nome</label>
              <input type="text" placeholder="Ex: Ana Oliveira" {...register('name')} className={inputClass(Boolean(errors.name))} />
              {errors.name && <p className="text-xs text-red-500 mt-1 ml-1">{errors.name.message}</p>}
            </div>
            <div>
              <label className="block text-xs font-semibold text-[#48372F] mb-1.5 ml-1">E-mail</label>
              <input type="email" placeholder="ana@empresa.com" {...register('email')} className={inputClass(Boolean(errors.email))} />
              {errors.email && <p className="text-xs text-red-500 mt-1 ml-1">{errors.email.message}</p>}
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-[#48372F] mb-1.5 ml-1">Telefone</label>
              <input type="tel" placeholder="(11) 99999-9999" {...register('phone')} className={inputClass(Boolean(errors.phone))} />
              {errors.phone && <p className="text-xs text-red-500 mt-1 ml-1">{errors.phone.message}</p>}
            </div>
            <div>
              <label className="block text-xs font-semibold text-[#48372F] mb-1.5 ml-1">Assunto</label>
              <input type="text" placeholder="Ex: Demonstração do produto" {...register('subject')} className={inputClass(Boolean(errors.subject))} />
              {errors.subject && <p className="text-xs text-red-500 mt-1 ml-1">{errors.subject.message}</p>}
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-[#48372F] mb-1.5 ml-1">Empresa</label>
              <div className="relative">
                <Building2 className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#8C7F76] pointer-events-none" />
                <select
                  {...register('companyId', {
                    setValueAs: (value) => (value === '' ? undefined : Number(value)),
                  })}
                  className={`${inputClass(Boolean(errors.companyId))} pl-10`}
                >
                  <option value="">Sem empresa</option>
                  {companies.map((company) => <option key={company.id} value={company.id}>{company.name}</option>)}
                </select>
              </div>
              {errors.companyId && <p className="text-xs text-red-500 mt-1 ml-1">{errors.companyId.message}</p>}
            </div>
            <div>
              <label className="block text-xs font-semibold text-[#48372F] mb-1.5 ml-1">Valor estimado</label>
              <input
                type="number"
                min="0"
                step="0.01"
                placeholder="0,00"
                {...register('estimatedValue', { valueAsNumber: true })}
                className={inputClass(Boolean(errors.estimatedValue))}
              />
              {errors.estimatedValue && <p className="text-xs text-red-500 mt-1 ml-1">{errors.estimatedValue.message}</p>}
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-[#48372F] mb-1.5 ml-1">Status inicial</label>
            <select {...register('status')} className={inputClass(Boolean(errors.status))}>
              <option value="new">Novo</option>
              <option value="contacted">Em contato</option>
              <option value="won">Ganho</option>
              <option value="lost">Perdido</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-[#48372F] mb-1.5 ml-1">Descrição</label>
            <textarea rows={3} placeholder="Contexto ou próximos passos" {...register('description')} className={`${inputClass(Boolean(errors.description))} resize-y`} />
            {errors.description && <p className="text-xs text-red-500 mt-1 ml-1">{errors.description.message}</p>}
          </div>

          {/* Erro da API */}
          {apiError && (
            <div className="flex items-start gap-2.5 px-4 py-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-xs font-medium">
              <span className="mt-0.5 shrink-0">⚠️</span>
              <span>{apiError}</span>
            </div>
          )}

          <div className="flex items-center justify-end gap-3 pt-4 border-t border-[#E3DBD0]">
            <button type="button" onClick={onClose} disabled={isSaving} className="px-5 py-2.5 text-xs font-semibold text-[#685A52] hover:bg-[#EAE4D9] rounded-full transition-colors cursor-pointer disabled:opacity-50">Cancelar</button>
            <button type="submit" disabled={isSaving} className="px-6 py-2.5 bg-[#BA5827] hover:bg-[#A14A1E] text-white text-xs font-semibold rounded-full shadow-md transition-all cursor-pointer disabled:opacity-50">{isSaving ? 'Criando...' : 'Criar Lead'}</button>
          </div>
        </form>
      </div>
    </div>
  );
};
