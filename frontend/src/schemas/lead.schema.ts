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
  status: leadStatusEnum,
  date: z.string().min(1, 'A data inicial é obrigatória'),
  targetDate: z.string().optional(),
});

export type LeadFormData = z.infer<typeof leadSchema>;

export const leadCreateSchema = z.object({
  name: z.string().min(3, 'O nome deve ter pelo menos 3 caracteres').max(100, 'O nome deve ter no máximo 100 caracteres'),
  email: z.string().email('Informe um e-mail válido'),
  phone: z.string().min(9, 'Informe um telefone válido').max(20, 'O telefone deve ter no máximo 20 caracteres'),
  companyId: z.number().int().positive().optional(),
  subject: z.string().min(3, 'O assunto deve ter pelo menos 3 caracteres').max(100, 'O assunto deve ter no máximo 100 caracteres'),
  description: z.string().max(500, 'A descrição deve ter no máximo 500 caracteres').optional(),
  estimatedValue: z.number().min(0, 'O valor estimado não pode ser negativo'),
  status: z.enum(['new', 'contacted', 'won', 'lost']),
});

export type LeadCreateFormData = z.infer<typeof leadCreateSchema>;

export interface LeadItem {
  id: string;
  name: string;
  role: string;
  company: string;
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
