import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Sidebar } from '../components/layout/Sidebar';
import { Header } from '../components/layout/Header';
import { 
  profileSettingsSchema, 
  createUserSchema, 
  type ProfileSettingsFormData, 
  type CreateUserFormData 
} from '../schemas/config.schema';
import { useAuth } from '../contexts/AuthContext';
import { usersService } from '../services/users.service';
import { authService } from '../services/auth.service';

interface ConfigPageProps {
  onNavigate?: (path: string) => void;
  isAdmin?: boolean;
}

export const ConfigPage: React.FC<ConfigPageProps> = ({ onNavigate, isAdmin = true }) => {
  const { user, refreshUser } = useAuth();
  const [profileMessage, setProfileMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [userMessage, setUserMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Formulário 1: Profile Settings
  const {
    register: registerProfile,
    handleSubmit: handleSubmitProfile,
    formState: { errors: profileErrors, isSubmitting: isProfileSubmitting },
    reset: resetProfile,
  } = useForm<ProfileSettingsFormData>({
    resolver: zodResolver(profileSettingsSchema),
    defaultValues: {
      username: user?.username || '',
      currentPassword: '',
      newPassword: '',
      confirmNewPassword: '',
    },
  });

  // Formulário 2: Admin Create User
  const {
    register: registerUser,
    handleSubmit: handleSubmitUser,
    formState: { errors: userErrors, isSubmitting: isUserSubmitting },
    reset: resetUser,
  } = useForm<CreateUserFormData>({
    resolver: zodResolver(createUserSchema),
    defaultValues: {
      fullName: '',
      email: '',
      role: 'sales',
    },
  });

  const onProfileSubmit = async (data: ProfileSettingsFormData) => {
    if (!user) return;
    setProfileMessage(null);
    try {
      // Se alterou o username
      if (data.username !== user.username) {
        await usersService.updateUsername(user.id, { username: data.username });
      }

      // Se informou nova senha
      if (data.newPassword && data.currentPassword) {
        await usersService.updatePassword(user.id, {
          current_password: data.currentPassword,
          new_password: data.newPassword,
        });
      }

      await refreshUser();
      setProfileMessage({ type: 'success', text: 'Alterações de perfil salvas com sucesso!' });
      resetProfile({
        username: data.username,
        currentPassword: '',
        newPassword: '',
        confirmNewPassword: '',
      });
    } catch (err: any) {
      console.error('Erro ao atualizar perfil:', err);
      const detail = err.response?.data?.detail;
      setProfileMessage({ 
        type: 'error', 
        text: typeof detail === 'string' ? detail : 'Erro ao atualizar dados do perfil.' 
      });
    }
  };

  const onUserSubmit = async (data: CreateUserFormData) => {
    setUserMessage(null);
    try {
      // Converte o nome completo para username único
      const usernameGenerated = data.fullName.toLowerCase().replace(/\s+/g, '_') + '_' + Math.floor(Math.random() * 1000);
      const roleMapped = (data.role === 'admin' ? 'admin' : data.role === 'manager' ? 'manager' : 'sales') as 'admin' | 'manager' | 'sales';

      await authService.register({
        username: usernameGenerated,
        password: 'Password123!', // Senha padrão inicial
        role: roleMapped,
        is_active: true,
      });

      setUserMessage({ 
        type: 'success', 
        text: `Usuário "${data.fullName}" criado! Usuário: ${usernameGenerated} (Perfil: ${roleMapped}, Senha padrão: Password123!)` 
      });
      resetUser();
    } catch (err: any) {
      console.error('Erro ao criar usuário:', err);
      const detail = err.response?.data?.detail;
      setUserMessage({ 
        type: 'error', 
        text: typeof detail === 'string' ? detail : 'Erro ao criar usuário.' 
      });
    }
  };

  return (
    <div className="flex h-screen w-screen bg-[#FAF6F0] overflow-hidden">
      {/* Sidebar sem 'Atividades' */}
      <Sidebar currentPath="config" onNavigate={onNavigate} />

      {/* Conteúdo Principal */}
      <div className="flex-1 flex flex-col overflow-y-auto">
        <Header userName="Maria Silva" />

        <main className="p-8 sm:p-10 max-w-6xl space-y-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
            
            {/* CARD 1: Profile Settings */}
            <div>
              <h2 className="text-2xl font-bold text-[#8A4A28] mb-4">
                Profile Settings
              </h2>

              <div className="bg-[#EFE8DC] rounded-3xl p-6 sm:p-8 border border-[#DFD6C7] shadow-sm">
                {/* Header do Perfil com Avatar e Botão Update */}
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-16 h-16 rounded-full overflow-hidden border-2 border-white shadow-sm shrink-0">
                    <img
                      src="https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=160&auto=format&fit=crop&q=80"
                      alt={user?.username || 'Usuário'}
                      className="w-full h-full object-cover"
                    />
                  </div>

                  <div>
                    <button
                      type="button"
                      className="px-4 py-1 bg-[#98AE9D] hover:bg-[#879D8C] text-white text-xs font-semibold rounded-full shadow-2xs transition-all cursor-pointer mb-1"
                    >
                      Update
                    </button>
                    <h3 className="text-lg font-bold text-[#3B2317]">{user?.username || 'Usuário'}</h3>
                  </div>
                </div>

                {profileMessage && (
                  <div className={`p-3.5 mb-4 text-xs font-medium rounded-2xl ${
                    profileMessage.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {profileMessage.text}
                  </div>
                )}

                {/* Formulário de Perfil */}
                <form onSubmit={handleSubmitProfile(onProfileSubmit)} className="space-y-4">
                  {/* Username */}
                  <div>
                    <label className="block text-xs font-semibold text-[#5A4B42] mb-1">
                      Username
                    </label>
                    <input
                      type="text"
                      {...registerProfile('username')}
                      className="w-full pb-2 bg-transparent border-b border-[#A3968C] text-sm text-[#3B2317] font-medium focus:outline-none focus:border-[#BA5827] transition-colors"
                    />
                    {profileErrors.username && (
                      <p className="text-xs text-red-500 mt-1">{profileErrors.username.message}</p>
                    )}
                  </div>

                  <div className="pt-2">
                    <h4 className="text-sm font-bold text-[#3B2317] mb-3">
                      Change Password
                    </h4>

                    {/* Current Password */}
                    <div className="mb-3">
                      <input
                        type="password"
                        placeholder="Current Password"
                        {...registerProfile('currentPassword')}
                        className="w-full pb-2 bg-transparent border-b border-[#A3968C] text-sm text-[#3B2317] placeholder-[#8C7F76] focus:outline-none focus:border-[#BA5827] transition-colors"
                      />
                      {profileErrors.currentPassword && (
                        <p className="text-xs text-red-500 mt-1">{profileErrors.currentPassword.message}</p>
                      )}
                    </div>

                    {/* New Password */}
                    <div className="mb-3">
                      <input
                        type="password"
                        placeholder="New Password"
                        {...registerProfile('newPassword')}
                        className="w-full pb-2 bg-transparent border-b border-[#A3968C] text-sm text-[#3B2317] placeholder-[#8C7F76] focus:outline-none focus:border-[#BA5827] transition-colors"
                      />
                      {profileErrors.newPassword && (
                        <p className="text-xs text-red-500 mt-1">{profileErrors.newPassword.message}</p>
                      )}
                    </div>

                    {/* Confirm New Password */}
                    <div>
                      <input
                        type="password"
                        placeholder="Confirm New Password"
                        {...registerProfile('confirmNewPassword')}
                        className="w-full pb-2 bg-transparent border-b border-[#A3968C] text-sm text-[#3B2317] placeholder-[#8C7F76] focus:outline-none focus:border-[#BA5827] transition-colors"
                      />
                      {profileErrors.confirmNewPassword && (
                        <p className="text-xs text-red-500 mt-1">{profileErrors.confirmNewPassword.message}</p>
                      )}
                    </div>
                  </div>

                  {/* Botão Salvar Alterações */}
                  <div className="pt-4">
                    <button
                      type="submit"
                      disabled={isProfileSubmitting}
                      className="w-full py-3 bg-[#98AE9D] hover:bg-[#859B8A] active:scale-[0.99] text-white font-semibold text-sm rounded-2xl shadow-sm transition-all cursor-pointer"
                    >
                      Save Changes
                    </button>
                  </div>
                </form>
              </div>
            </div>

            {/* CARD 2: Admin: User Management (visível apenas para admin ou conforme imagem) */}
            {isAdmin && (
              <div>
                <h2 className="text-2xl font-bold text-[#8A4A28] mb-4">
                  Admin: User Management
                </h2>

                <div className="bg-[#EFE8DC] rounded-3xl p-6 sm:p-8 border border-[#DFD6C7] shadow-sm">
                  <h3 className="text-base font-bold text-[#3B2317] mb-6">
                    Create New User
                  </h3>

                  {userMessage && (
                    <div className={`p-3.5 mb-4 text-xs font-medium rounded-2xl ${
                      userMessage.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {userMessage.text}
                    </div>
                  )}

                  <form onSubmit={handleSubmitUser(onUserSubmit)} className="space-y-5">
                    {/* Full Name */}
                    <div>
                      <input
                        type="text"
                        placeholder="Full Name"
                        {...registerUser('fullName')}
                        className="w-full pb-2 bg-transparent border-b border-[#A3968C] text-sm text-[#3B2317] placeholder-[#8C7F76] focus:outline-none focus:border-[#BA5827] transition-colors"
                      />
                      {userErrors.fullName && (
                        <p className="text-xs text-red-500 mt-1">{userErrors.fullName.message}</p>
                      )}
                    </div>

                    {/* Email Address */}
                    <div>
                      <input
                        type="email"
                        placeholder="Email Address"
                        {...registerUser('email')}
                        className="w-full pb-2 bg-transparent border-b border-[#A3968C] text-sm text-[#3B2317] placeholder-[#8C7F76] focus:outline-none focus:border-[#BA5827] transition-colors"
                      />
                      {userErrors.email && (
                        <p className="text-xs text-red-500 mt-1">{userErrors.email.message}</p>
                      )}
                    </div>

                    {/* Assign Role */}
                    <div>
                      <label className="block text-xs font-semibold text-[#5A4B42] mb-1.5">
                        Assign Role
                      </label>
                      <div className="relative">
                        <select
                          {...registerUser('role')}
                          className="w-full px-4 py-2.5 bg-[#FAF6F0] border border-[#BACBB9] rounded-xl text-sm text-[#3B2317] focus:outline-none focus:ring-2 focus:ring-[#77917B]/20 cursor-pointer appearance-none"
                        >
                          <option value="sales">Vendedor / Sales</option>
                          <option value="manager">Gerente / Manager</option>
                          <option value="admin">Administrador / Admin</option>
                          <option value="viewer">Visualizador / Viewer</option>
                        </select>
                        <div className="pointer-events-none absolute inset-y-0 right-0 flex items-center px-3 text-[#5A4B42]">
                          <svg className="fill-current h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">
                            <path d="M9.293 12.95l.707.707L15.657 8l-1.414-1.414L10 10.828 5.757 6.586 4.343 8z" />
                          </svg>
                        </div>
                      </div>
                    </div>

                    {/* Botões Create User e Cancel */}
                    <div className="pt-4 space-y-3 text-center">
                      <button
                        type="submit"
                        disabled={isUserSubmitting}
                        className="w-full py-3 bg-[#98AE9D] hover:bg-[#859B8A] active:scale-[0.99] text-white font-semibold text-sm rounded-2xl shadow-sm transition-all cursor-pointer"
                      >
                        Create User
                      </button>

                      <button
                        type="button"
                        onClick={() => resetUser()}
                        className="text-xs font-semibold text-[#BA5827] hover:underline cursor-pointer"
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            )}

          </div>
        </main>
      </div>
    </div>
  );
};
