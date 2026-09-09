import { z } from 'zod';

export const companySchema = z.object({
  id: z.string().optional(),
  name: z.string().min(2, 'O nome da empresa é obrigatório'),
  sector: z.string().optional().default(''),
  lastActivity: z.string().optional().default(''),
  mainContact: z.string().optional().default(''),
  status: z.enum(['Parceiro Ativo', 'Ativo', 'Pendente', 'Parceria']),
  description: z.string().optional().default(''),
  iconType: z.enum(['tree', 'gear', 'novo', 'textil', 'tech', 'building']),
  isLinkedToUser: z.boolean(),
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
