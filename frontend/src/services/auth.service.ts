import { api } from './api';

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export type UserRole = 'admin' | 'manager' | 'sales';

export interface UserResponse {
  id: number;
  username: string;
  role: UserRole;
  created_at?: string;
  updated_at?: string;
}

export interface UserCreateData {
  username: string;
  password: string;
  role?: UserRole;
  is_active?: boolean;
}

export const authService = {
  async login(username: string, password: string): Promise<TokenResponse> {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await api.post<TokenResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    return response.data;
  },

  async register(data: UserCreateData): Promise<UserResponse> {
    const response = await api.post<UserResponse>('/auth/register', data);
    return response.data;
  },

  async getMe(): Promise<UserResponse> {
    const response = await api.get<UserResponse>('/users/me');
    return response.data;
  },
};
