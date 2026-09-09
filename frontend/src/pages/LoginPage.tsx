import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { User, Lock, AlertCircle } from 'lucide-react';
import { loginSchema, type LoginFormData } from '../schemas/auth.schema';
import { useAuth } from '../contexts/AuthContext';

export const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const [apiError, setApiError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      username: '',
      password: '',
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    setApiError(null);
    try {
      await login(data.username, data.password);
    } catch (err: any) {
      console.error('Erro no login:', err);
      const detail = err.response?.data?.detail;
      if (typeof detail === 'string') {
        setApiError(detail);
      } else if (Array.isArray(detail) && detail[0]?.msg) {
        setApiError(detail[0].msg);
      } else {
        setApiError('Não foi possível conectar ao servidor. Verifique suas credenciais.');
      }
    }
  };

  return (
    <main className="h-screen w-screen overflow-hidden grid grid-cols-1 md:grid-cols-2">
      {/* Lado Esquerdo - Visual Gradiente & Logo em tela cheia */}
      <div className="relative bg-gradient-to-br from-[#CD8463] via-[#C59B80] to-[#98AE9D] flex items-center justify-center p-8 overflow-hidden h-full">
        {/* Ondas decorativas em SVG concêntricas */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-35">
          <svg
            className="w-[180%] h-[180%] max-w-none"
            viewBox="0 0 600 600"
            fill="none"
            stroke="white"
            strokeWidth="0.9"
          >
            {[...Array(16)].map((_, i) => (
              <ellipse
                key={i}
                cx="300"
                cy="300"
                rx={80 + i * 22}
                ry={55 + i * 18}
                strokeDasharray="4 4"
              />
            ))}
          </svg>
        </div>

        {/* Logo Central */}
        <div className="relative z-10 w-36 h-36 rounded-full border-[4px] border-white/75 bg-white/20 backdrop-blur-md shadow-2xl flex items-center justify-center transition-transform hover:scale-105 duration-300">
          <span className="text-6xl font-black text-white/95 drop-shadow-md select-none">
            C
          </span>
          <div className="absolute top-5 right-5 w-3 h-3 bg-white/95 rounded-full" />
        </div>
      </div>

      {/* Lado Direito - Formulário em tela cheia */}
      <div className="bg-[#FAF6F0] p-8 sm:p-16 lg:p-24 flex flex-col justify-center items-center h-full">
        <div className="w-full max-w-md">
          <div className="text-center mb-10">
            <h1 className="text-4xl font-bold text-[#3B2317] tracking-tight mb-3">
              Boas-vindas de volta
            </h1>
            <p className="text-base text-[#73635B]">
              Entre no seu painel de CRM
            </p>
          </div>

          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6 w-full">
            {apiError && (
              <div className="flex items-center gap-2.5 p-3.5 bg-red-100 border border-red-300 text-red-700 text-sm rounded-2xl">
                <AlertCircle className="w-5 h-5 shrink-0" />
                <span>{apiError}</span>
              </div>
            )}

            {/* Campo Username */}
            <div>
              <label className="block text-sm font-semibold text-[#48372F] mb-2 ml-1">
                Usuário
              </label>
              <div className="relative flex items-center">
                <User className="absolute left-4 w-5 h-5 text-[#8B988C]" />
                <input
                  type="text"
                  placeholder="Usuário"
                  {...register('username')}
                  className={`w-full pl-12 pr-4 py-3.5 bg-[#F4F1EA] border ${
                    errors.username ? 'border-red-400 focus:border-red-500' : 'border-[#A3B3A5] focus:border-[#77917B]'
                  } rounded-2xl text-base text-[#3B2317] placeholder-[#A09890] focus:outline-none focus:ring-2 focus:ring-[#77917B]/20 transition-all`}
                />
              </div>
              {errors.username && (
                <p className="text-xs text-red-500 mt-1.5 ml-1">{errors.username.message}</p>
              )}
            </div>

            {/* Campo Senha */}
            <div>
              <label className="block text-sm font-semibold text-[#48372F] mb-2 ml-1">
                Senha
              </label>
              <div className="relative flex items-center">
                <Lock className="absolute left-4 w-5 h-5 text-[#8B988C]" />
                <input
                  type="password"
                  placeholder="Senha"
                  {...register('password')}
                  className={`w-full pl-12 pr-4 py-3.5 bg-[#F4F1EA] border ${
                    errors.password ? 'border-red-400 focus:border-red-500' : 'border-[#A3B3A5] focus:border-[#77917B]'
                  } rounded-2xl text-base text-[#3B2317] placeholder-[#A09890] focus:outline-none focus:ring-2 focus:ring-[#77917B]/20 transition-all`}
                />
              </div>
              {errors.password && (
                <p className="text-xs text-red-500 mt-1.5 ml-1">{errors.password.message}</p>
              )}
            </div>

            {/* Botão Sign In */}
            <div className="pt-3">
              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full py-3.5 bg-[#B75828] hover:bg-[#A14A1E] active:scale-[0.99] text-white font-semibold rounded-full shadow-lg hover:shadow-xl transition-all text-base tracking-wide cursor-pointer"
              >
                Entrar
              </button>
            </div>

            {/* Forgot Password */}
            <div className="text-center pt-2">
              <a
                href="#forgot-password"
                className="text-sm text-[#7B6C64] hover:text-[#3B2317] hover:underline transition-colors"
              >
                Esqueceu a senha?
              </a>
            </div>
          </form>
        </div>
      </div>
    </main>
  );
};
