import { z } from 'zod';

export const companySchema = z.object({
  id: z.string().optional(),
  name: z.string().min(2, 'O nome da empresa é obrigatório'),
  sector: z.string().min(2, 'O ramo de atividade é obrigatório'),
  lastActivity: z.string().min(2, 'A última atividade é obrigatória'),
  mainContact: z.string().min(2, 'O contato principal é obrigatório'),
  status: z.enum(['Parceiro Ativo', 'Ativo', 'Pendente', 'Parceria']),
  description: z.string(),
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
