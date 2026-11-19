import { z } from 'zod';

export const loginSchema = z.object({
  username: z
    .string()
    .min(1, 'O usuário é obrigatório')
    .min(3, 'O usuário deve ter no mínimo 3 caracteres'),
  password: z
    .string()
    .min(1, 'A senha é obrigatória')
    .min(6, 'A senha deve ter no mínimo 6 caracteres'),
});

export type LoginFormData = z.infer<typeof loginSchema>;
