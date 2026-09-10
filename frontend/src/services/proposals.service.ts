import { api } from './api';

export type ProposalStatusApi = 'pending' | 'accepted' | 'rejected';

export interface ProposalApiResponse {
  id: number;
  lead_id: number;
  user_id: number;
  status: ProposalStatusApi;
  value: number;
  sent_at: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface ProposalCreatePayload {
  lead_id: number;
  status?: ProposalStatusApi;
  value: number;
  sent_at?: string | null;
}

export interface ProposalUpdatePayload {
  status?: ProposalStatusApi;
  value?: number;
  sent_at?: string | null;
}

export const proposalsService = {
  async create(payload: ProposalCreatePayload): Promise<ProposalApiResponse> {
    const response = await api.post<ProposalApiResponse>('/proposals/create', payload);
    return response.data;
  },
  async update(id: number, payload: ProposalUpdatePayload): Promise<ProposalApiResponse> {
    const response = await api.patch<ProposalApiResponse>(`/proposals/update/${id}`, payload);
    return response.data;
  },
  async delete(id: number): Promise<ProposalApiResponse> {
    const response = await api.delete<ProposalApiResponse>(`/proposals/delete/${id}`);
    return response.data;
  },
  async getByLeadId(leadId: number): Promise<ProposalApiResponse[]> {
    const response = await api.get<ProposalApiResponse[]>(`/proposals/lead_id/${leadId}`);
    return response.data;
  },
};
