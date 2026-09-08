import { api } from './api';
import { type UserResponse } from './auth.service';

export interface UserUpdateUsernamePayload {
  username: string;
}

export interface UserUpdatePasswordPayload {
  current_password: string;
  new_password: string;
}

export const usersService = {
  async getAll(): Promise<UserResponse[]> {
    const response = await api.get<UserResponse[]>('/users');
    return response.data;
  },

  async getById(userId: number): Promise<UserResponse> {
    const response = await api.get<UserResponse>(`/users/list/by_id/${userId}`);
    return response.data;
  },

  async updateUsername(userId: number, payload: UserUpdateUsernamePayload): Promise<UserResponse> {
    const response = await api.patch<UserResponse>(`/users/update_username/${userId}`, payload);
    return response.data;
  },

  async updatePassword(userId: number, payload: UserUpdatePasswordPayload): Promise<UserResponse> {
    const response = await api.patch<UserResponse>(`/users/update_password/${userId}`, payload);
    return response.data;
  },

  async deleteUser(userId: number): Promise<UserResponse> {
    const response = await api.delete<UserResponse>(`/users/delete/${userId}`);
    return response.data;
  },
};
