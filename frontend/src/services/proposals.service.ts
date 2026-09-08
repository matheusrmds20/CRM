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

export const proposalsService = {
  async getByLeadId(leadId: number): Promise<ProposalApiResponse[]> {
    const response = await api.get<ProposalApiResponse[]>(`/proposals/lead_id/${leadId}`);
    return response.data;
  },
};
