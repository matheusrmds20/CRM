import { api } from './api';

export interface CompanyApiResponse {
  id: number;
  name: string;
  cnpj: string;
  created_at: string;
  updated_at: string | null;
}

export interface CompanyCreatePayload {
  name: string;
  cnpj: string;
  is_active?: boolean;
}

export interface CompanyUpdatePayload {
  name?: string;
  cnpj?: string;
}

export const companiesService = {
  async getAll(): Promise<CompanyApiResponse[]> {
    const response = await api.get<CompanyApiResponse[]>('/companies');
    return response.data;
  },

  async create(payload: CompanyCreatePayload): Promise<CompanyApiResponse> {
    const response = await api.post<CompanyApiResponse>('/companies/create', payload);
    return response.data;
  },

  async update(id: number, payload: CompanyUpdatePayload): Promise<CompanyApiResponse> {
    const response = await api.patch<CompanyApiResponse>(`/companies/update/${id}`, payload);
    return response.data;
  },

  async delete(id: number): Promise<CompanyApiResponse> {
    const response = await api.delete<CompanyApiResponse>(`/companies/delete/${id}`);
    return response.data;
  },
};
