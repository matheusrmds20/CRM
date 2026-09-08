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

export const activitiesService = {
  async getByLeadId(leadId: number): Promise<ActivityApiResponse[]> {
    const response = await api.get<ActivityApiResponse[]>(`/activities/lead_id/${leadId}`);
    return response.data;
  },
};
