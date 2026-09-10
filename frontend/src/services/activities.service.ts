import { api } from './api';

export type ActivityTypeApi = 'call' | 'meeting' | 'email' | 'whatsapp' | 'other';

export interface ActivityApiResponse {
  id: number;
  lead_id: number;
  user_id: number;
  description: string;
  activity_type: ActivityTypeApi;
  done_at: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface ActivityCreatePayload {
  lead_id: number;
  description: string;
  activity_type: ActivityTypeApi;
  done_at?: string | null;
}

export interface ActivityUpdatePayload {
  description?: string;
  activity_type?: ActivityTypeApi;
  done_at?: string | null;
}

export const activitiesService = {
  async create(payload: ActivityCreatePayload): Promise<ActivityApiResponse> {
    const response = await api.post<ActivityApiResponse>('/activities/create', payload);
    return response.data;
  },
  async update(id: number, payload: ActivityUpdatePayload): Promise<ActivityApiResponse> {
    const response = await api.patch<ActivityApiResponse>(`/activities/update/${id}`, payload);
    return response.data;
  },
  async delete(id: number): Promise<ActivityApiResponse> {
    const response = await api.delete<ActivityApiResponse>(`/activities/delete/${id}`);
    return response.data;
  },
  async getByLeadId(leadId: number): Promise<ActivityApiResponse[]> {
    const response = await api.get<ActivityApiResponse[]>(`/activities/lead_id/${leadId}`);
    return response.data;
  },
};
