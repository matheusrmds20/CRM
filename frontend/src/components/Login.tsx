import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { User, Lock } from 'lucide-react';
import { loginSchema, type LoginFormData } from '../schemas/auth.schema';

interface LoginCardProps {
  onSuccessLogin?: (data: LoginFormData) => void;
}

export const LoginCard: React.FC<LoginCardProps> = ({ onSuccessLogin }) => {
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

  const onSubmit = (data: LoginFormData) => {
    console.log('Login submetido com sucesso:', data);
    if (onSuccessLogin) {
      onSuccessLogin(data);
    }
  };

  return (
    <div className="relative z-10 w-full max-w-4xl bg-[#FAF6F0] border-[3px] border-[#1F1E1C] rounded-[32px] shadow-2xl overflow-hidden grid grid-cols-1 md:grid-cols-2 min-h-[520px]">
      {/* Lado Esquerdo - Visual Gradiente & Logo */}
      <div className="relative bg-gradient-to-br from-[#CD8463] via-[#C59B80] to-[#98AE9D] flex items-center justify-center p-8 overflow-hidden min-h-[260px] md:min-h-full">
        {/* Ondas decorativas em SVG */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none opacity-30">
          <svg
            className="w-[150%] h-[150%]"
            viewBox="0 0 500 500"
            fill="none"
            stroke="white"
            strokeWidth="0.8"
          >
            {[...Array(12)].map((_, i) => (
              <ellipse
                key={i}
                cx="250"
                cy="250"
                rx={70 + i * 16}
                ry={45 + i * 13}
                strokeDasharray="3 3"
              />
            ))}
          </svg>
        </div>

        {/* Logo Central */}
        <div className="relative z-10 w-28 h-28 rounded-full border-[3px] border-white/70 bg-white/15 backdrop-blur-md shadow-lg flex items-center justify-center">
          <span className="text-5xl font-black text-white/90 drop-shadow select-none">
            C
          </span>
          <div className="absolute top-4 right-4 w-2.5 h-2.5 bg-white/90 rounded-full" />
        </div>
      </div>

      {/* Lado Direito - Formulário */}
      <div className="bg-[#FAF6F0] p-8 sm:p-12 flex flex-col justify-center">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-[#3B2317] tracking-tight mb-2">
            Welcome Back
          </h1>
          <p className="text-sm text-[#73635B]">
            Log in to your CRM dashboard
          </p>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-5 max-w-xs sm:max-w-sm mx-auto w-full">
          {/* Username Field */}
          <div>
            <label className="block text-xs font-semibold text-[#48372F] mb-1.5 ml-1">
              Username
            </label>
            <div className="relative flex items-center">
              <User className="absolute left-3.5 w-4 h-4 text-[#8B988C]" />
              <input
                type="text"
                placeholder="Username"
                {...register('username')}
                className={`w-full pl-10 pr-4 py-2.5 bg-[#F4F1EA] border ${
                  errors.username ? 'border-red-400 focus:border-red-500' : 'border-[#A3B3A5] focus:border-[#77917B]'
                } rounded-xl text-sm text-[#3B2317] placeholder-[#A09890] focus:outline-none focus:ring-2 focus:ring-[#77917B]/20 transition-all`}
              />
            </div>
            {errors.username && (
              <p className="text-xs text-red-500 mt-1 ml-1">{errors.username.message}</p>
            )}
          </div>

          {/* Password Field */}
          <div>
            <label className="block text-xs font-semibold text-[#48372F] mb-1.5 ml-1">
              Password
            </label>
            <div className="relative flex items-center">
              <Lock className="absolute left-3.5 w-4 h-4 text-[#8B988C]" />
              <input
                type="password"
                placeholder="Password"
                {...register('password')}
                className={`w-full pl-10 pr-4 py-2.5 bg-[#F4F1EA] border ${
                  errors.password ? 'border-red-400 focus:border-red-500' : 'border-[#A3B3A5] focus:border-[#77917B]'
                } rounded-xl text-sm text-[#3B2317] placeholder-[#A09890] focus:outline-none focus:ring-2 focus:ring-[#77917B]/20 transition-all`}
              />
            </div>
            {errors.password && (
              <p className="text-xs text-red-500 mt-1 ml-1">{errors.password.message}</p>
            )}
          </div>

          {/* Botão Sign In */}
          <div className="pt-2">
            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full py-3 bg-[#B75828] hover:bg-[#A14A1E] active:scale-[0.99] text-white font-medium rounded-full shadow-md transition-all text-sm tracking-wide cursor-pointer"
            >
              Sign In
            </button>
          </div>

          {/* Forgot Password Link */}
          <div className="text-center pt-2">
            <a
              href="#forgot-password"
              className="text-xs text-[#7B6C64] hover:text-[#3B2317] hover:underline transition-colors"
            >
              Forgot password?
            </a>
          </div>
        </form>
      </div>
    </div>
  );
};
