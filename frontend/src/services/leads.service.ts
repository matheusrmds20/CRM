import { api } from './api';

export type LeadStatusApi = 'new' | 'contacted' | 'won' | 'lost';

export interface LeadApiResponse {
  id: number;
  name: string;
  email: string;
  phone: string | null;
  company_id: number | null;
  user_id: number;
  subject: string;
  description: string | null;
  estimated_value: number | null;
  status: LeadStatusApi;
  created_at: string;
  updated_at: string | null;
  is_active: boolean;
}

export interface LeadCreatePayload {
  name: string;
  email: string;
  phone: string;
  company_id?: number | null;
  subject: string;
  description?: string | null;
  estimated_value: number;
  status?: LeadStatusApi;
}

export interface LeadUpdatePayload {
  name?: string;
  email?: string;
  phone?: string | null;
  company_id?: number | null;
  status?: LeadStatusApi;
  subject?: string;
  description?: string | null;
  estimated_value?: number | null;
  is_active?: boolean;
}

export interface PaginationResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

export const leadsService = {
  async getAll(): Promise<LeadApiResponse[]> {
    const response = await api.get<LeadApiResponse[]>('/leads');
    return response.data;
  },

  async getPaginated(page: number = 1, pageSize: number = 10): Promise<PaginationResponse<LeadApiResponse>> {
    const response = await api.get<PaginationResponse<LeadApiResponse>>('/leads/list/query', {
      params: { page, page_size: pageSize },
    });
    return response.data;
  },

  async getById(id: number): Promise<LeadApiResponse> {
    const response = await api.get<LeadApiResponse>(`/leads/list/id/${id}`);
    return response.data;
  },

  async getByStatus(status: LeadStatusApi): Promise<LeadApiResponse[]> {
    const response = await api.get<LeadApiResponse[]>(`/leads/list/status/${status}`);
    return response.data;
  },

  async getByCompanyId(companyId: number): Promise<LeadApiResponse[]> {
    const response = await api.get<LeadApiResponse[]>(`/leads/list/company/${companyId}`);
    return response.data;
  },

  async create(payload: LeadCreatePayload): Promise<LeadApiResponse> {
    const response = await api.post<LeadApiResponse>('/leads/create', payload);
    return response.data;
  },

  async update(id: number, payload: LeadUpdatePayload): Promise<LeadApiResponse> {
    const response = await api.patch<LeadApiResponse>(`/leads/update/${id}`, payload);
    return response.data;
  },

  async delete(id: number): Promise<LeadApiResponse> {
    const response = await api.delete<LeadApiResponse>(`/leads/delete/${id}`);
    return response.data;
  },
};
