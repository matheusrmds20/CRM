import { z } from 'zod';

function digitsOnly(value: string): string {
  return value.replace(/\D/g, '');
}

function isValidCnpj(value: string): boolean {
  const cnpj = digitsOnly(value);
  if (cnpj.length !== 14) return false;
  if (/^(\d)\1{13}$/.test(cnpj)) return false;

  const checkDigit = (length: number): number => {
    let sum = 0;
    let pos = length - 7;
    for (let i = 0; i < length; i += 1) {
      sum += Number(cnpj[i]) * pos;
      pos -= 1;
      if (pos < 2) pos = 9;
    }
    const rest = sum % 11;
    return rest < 2 ? 0 : 11 - rest;
  };

  if (checkDigit(12) !== Number(cnpj[12])) return false;
  return checkDigit(13) === Number(cnpj[13]);
}

export const companySchema = z
  .object({
    id: z.string().optional(),
    name: z.string().min(2, 'O nome da empresa é obrigatório'),
    cnpj: z.string().optional(),
    lastActivity: z.string().optional(),
    mainContact: z.string().optional(),
    status: z.enum(['Parceiro Ativo', 'Ativo', 'Pendente', 'Parceria']),
    description: z.string().optional(),
    iconType: z.enum(['tree', 'gear', 'novo', 'textil', 'tech', 'building']),
    isLinkedToUser: z.boolean(),
  })
  .superRefine((data, ctx) => {
    if (data.cnpj && data.cnpj.trim() !== '' && !isValidCnpj(data.cnpj)) {
      ctx.addIssue({ code: z.ZodIssueCode.custom, message: 'CNPJ inválido', path: ['cnpj'] });
    }
  });

export type CompanyFormData = z.infer<typeof companySchema>;

export interface CompanyItem {
  id: string;
  name: string;
  sector: string;
  lastActivity: string;
  mainContact: string;
  status: 'Parceiro Ativo' | 'Ativo' | 'Pendente' | 'Parceria';
  description: string;
  iconType: 'tree' | 'gear' | 'novo' | 'textil' | 'tech' | 'building';
  isLinkedToUser: boolean;
}