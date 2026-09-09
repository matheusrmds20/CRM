import { z } from 'zod';

// Schema para Alteração de Perfil e Senha
export const profileSettingsSchema = z.object({
  username: z.string().min(3, 'O username deve ter no mínimo 3 caracteres'),
  currentPassword: z.string().min(1, 'A senha atual é obrigatória'),
  newPassword: z.string().min(6, 'A nova senha deve ter no mínimo 6 caracteres'),
  confirmNewPassword: z.string().min(6, 'Confirmação de senha obrigatória'),
}).refine((data) => data.newPassword === data.confirmNewPassword, {
  message: 'As senhas não coincidem',
  path: ['confirmNewPassword'],
});

export type ProfileSettingsFormData = z.infer<typeof profileSettingsSchema>;

// Schema para Criação de Usuário (Admin)
export const createUserSchema = z.object({
  username: z.string()
    .min(3, 'O usuário deve ter pelo menos 3 caracteres')
    .max(20, 'O usuário deve ter no máximo 20 caracteres'),
  password: z.string().min(8, 'A senha deve ter no mínimo 8 caracteres'),
  confirmPassword: z.string().min(1, 'Confirme a senha'),
  role: z.enum(['admin', 'sales', 'manager', 'viewer'], {
    error: 'Selecione um perfil válido',
  }),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'As senhas não coincidem',
  path: ['confirmPassword'],
});

export type CreateUserFormData = z.infer<typeof createUserSchema>;
