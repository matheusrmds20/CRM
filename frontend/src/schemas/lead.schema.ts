import { z } from 'zod';

export const leadStatusEnum = z.enum([
  'Novo',
  'Em Contato',
  'Qualificado',
  'Negociação',
  'Ganho',
  'Perdido'
]);

export type LeadStatus = z.infer<typeof leadStatusEnum>;

export const leadSchema = z.object({
  id: z.string().optional(),
  name: z.string().min(2, 'O nome do lead é obrigatório'),
  role: z.string().min(2, 'O cargo é obrigatório'),
  company: z.string().min(2, 'A empresa é obrigatória'),
  avatar: z.string().url('URL do avatar inválida').or(z.string().min(1)),
  status: leadStatusEnum,
  date: z.string().min(1, 'A data inicial é obrigatória'),
  targetDate: z.string().optional(),
});

export type LeadFormData = z.infer<typeof leadSchema>;

export interface LeadItem {
  id: string;
  name: string;
  role: string;
  company: string;
  avatar: string;
  status: LeadStatus;
  date: string;
  targetDate?: string;
  // Campos detalhados usados no modal de detalhe
  email?: string;
  phone?: string;
  subject?: string;
  description?: string;
  estimatedValue?: number;
}
