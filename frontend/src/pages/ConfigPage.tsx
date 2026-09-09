import React, { useEffect, useMemo, useState } from 'react';
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
import { type UserResponse } from '../services/auth.service';
import { UserManagementModal } from '../components/users/UserManagementModal';

interface ConfigPageProps {
  onNavigate?: (path: string) => void;
  isAdmin?: boolean;
}

export const ConfigPage: React.FC<ConfigPageProps> = ({ onNavigate, isAdmin = true }) => {
  const { user, refreshUser } = useAuth();
  const [profileMessage, setProfileMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [userMessage, setUserMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [registeredUsers, setRegisteredUsers] = useState<UserResponse[]>([]);
  const [usersPage, setUsersPage] = useState(1);
  const [selectedUser, setSelectedUser] = useState<UserResponse | null>(null);
  const [isUsersLoading, setIsUsersLoading] = useState(isAdmin);

  useEffect(() => {
    if (!isAdmin) return;

    usersService.getAll()
      .then(setRegisteredUsers)
      .catch((err) => console.error('Erro ao carregar usuários:', err))
      .finally(() => setIsUsersLoading(false));
  }, [isAdmin]);

  const usersPerPage = 5;
  const totalUsersPages = Math.max(1, Math.ceil(registeredUsers.length / usersPerPage));
  const visibleUsers = useMemo(
    () => registeredUsers.slice((usersPage - 1) * usersPerPage, usersPage * usersPerPage),
    [registeredUsers, usersPage],
  );

  const formatRole = (role: UserResponse['role']) => ({ admin: 'Administrador', manager: 'Gerente', sales: 'Vendedor' })[role];

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
      username: '',
      password: '',
      confirmPassword: '',
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
      const roleMapped = (data.role === 'admin' ? 'admin' : data.role === 'manager' ? 'manager' : 'sales') as 'admin' | 'manager' | 'sales';

      const createdUser = await authService.register({
        username: data.username,
        password: data.password,
        role: roleMapped,
        is_active: true,
      });

      setRegisteredUsers((current) => [createdUser, ...current]);
      setUsersPage(1);

      setUserMessage({ 
        type: 'success', 
        text: `Usuário "${data.username}" criado! (Perfil: ${data.role === 'sales' ? 'Vendedor' : data.role === 'manager' ? 'Gerente' : 'Administrador'})`
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

  const handleUpdateUser = async (userId: number, payload: { username: string; role: UserResponse['role'] }) => {
    const updatedUser = await usersService.updateUser(userId, payload);
    setRegisteredUsers((current) => current.map((registeredUser) => registeredUser.id === userId ? updatedUser : registeredUser));
  };

  const handleDeleteUser = async (userId: number) => {
    await usersService.deleteUser(userId);
    setRegisteredUsers((current) => {
      const remainingUsers = current.filter((registeredUser) => registeredUser.id !== userId);
      const remainingPages = Math.max(1, Math.ceil(remainingUsers.length / usersPerPage));
      setUsersPage((page) => Math.min(page, remainingPages));
      return remainingUsers;
    });
  };

  return (
    <div className="flex h-screen w-screen bg-[#FAF6F0] overflow-hidden">
      {/* Sidebar sem 'Atividades' */}
      <Sidebar currentPath="config" onNavigate={onNavigate} />

      {/* Conteúdo Principal */}
      <div className="flex-1 flex flex-col overflow-y-auto">
        <Header userName="Maria Silva" onNavigate={onNavigate} />

        <main className="p-8 sm:p-10 max-w-6xl space-y-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
            
            {/* CARD 1: Profile Settings */}
            <div>
              <h2 className="text-2xl font-bold text-[#8A4A28] mb-4">
                Configurações de perfil
              </h2>

              <div className="bg-[#EFE8DC] rounded-3xl p-6 sm:p-8 border border-[#DFD6C7] shadow-sm">
                {/* Header do Perfil com Avatar e Botão Update */}
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-16 h-16 rounded-full border-2 border-white bg-[#98AE9D] text-white text-2xl font-bold shadow-sm shrink-0 flex items-center justify-center">
                    {(user?.username || 'Usuário').charAt(0).toUpperCase()}
                  </div>

                  <div>
                    <button
                      type="button"
                      className="px-4 py-1 bg-[#98AE9D] hover:bg-[#879D8C] text-white text-xs font-semibold rounded-full shadow-2xs transition-all cursor-pointer mb-1"
                    >
                      Atualizar
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
                      Usuário
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
                      Alterar senha
                    </h4>

                    {/* Current Password */}
                    <div className="mb-3">
                      <input
                        type="password"
                        placeholder="Senha atual"
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
                        placeholder="Nova senha"
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
                        placeholder="Confirmar nova senha"
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
                      Salvar alterações
                    </button>
                  </div>
                </form>
              </div>
            </div>

            {/* CARD 2: Admin: User Management (visível apenas para admin ou conforme imagem) */}
            {isAdmin && (
              <div>
                <h2 className="text-2xl font-bold text-[#8A4A28] mb-4">
                  Administração: gerenciamento de usuários
                </h2>

                <div className="bg-[#EFE8DC] rounded-3xl p-6 sm:p-8 border border-[#DFD6C7] shadow-sm">
                  <h3 className="text-base font-bold text-[#3B2317] mb-6">
                    Criar novo usuário
                  </h3>

                  {userMessage && (
                    <div className={`p-3.5 mb-4 text-xs font-medium rounded-2xl ${
                      userMessage.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {userMessage.text}
                    </div>
                  )}

                  <form onSubmit={handleSubmitUser(onUserSubmit)} className="space-y-5">
                    {/* Username */}
                    <div>
                      <input
                        type="text"
                        placeholder="Usuário"
                        {...registerUser('username')}
                        className="w-full pb-2 bg-transparent border-b border-[#A3968C] text-sm text-[#3B2317] placeholder-[#8C7F76] focus:outline-none focus:border-[#BA5827] transition-colors"
                      />
                      {userErrors.username && (
                        <p className="text-xs text-red-500 mt-1">{userErrors.username.message}</p>
                      )}
                    </div>

                    {/* Password */}
                    <div>
                      <input
                        type="password"
                        placeholder="Senha"
                        {...registerUser('password')}
                        className="w-full pb-2 bg-transparent border-b border-[#A3968C] text-sm text-[#3B2317] placeholder-[#8C7F76] focus:outline-none focus:border-[#BA5827] transition-colors"
                      />
                      {userErrors.password && (
                        <p className="text-xs text-red-500 mt-1">{userErrors.password.message}</p>
                      )}
                    </div>

                    {/* Confirm Password */}
                    <div>
                      <input
                        type="password"
                        placeholder="Confirmar senha"
                        {...registerUser('confirmPassword')}
                        className="w-full pb-2 bg-transparent border-b border-[#A3968C] text-sm text-[#3B2317] placeholder-[#8C7F76] focus:outline-none focus:border-[#BA5827] transition-colors"
                      />
                      {userErrors.confirmPassword && (
                        <p className="text-xs text-red-500 mt-1">{userErrors.confirmPassword.message}</p>
                      )}
                    </div>

                    {/* Assign Role */}
                    <div>
                      <label className="block text-xs font-semibold text-[#5A4B42] mb-1.5">
                        Atribuir perfil
                      </label>
                      <div className="relative">
                        <select
                          {...registerUser('role')}
                          className="w-full px-4 py-2.5 bg-[#FAF6F0] border border-[#BACBB9] rounded-xl text-sm text-[#3B2317] focus:outline-none focus:ring-2 focus:ring-[#77917B]/20 cursor-pointer appearance-none"
                        >
                          <option value="sales">Vendedor</option>
                          <option value="manager">Gerente</option>
                          <option value="admin">Administrador</option>
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
                        Criar usuário
                      </button>

                      <button
                        type="button"
                        onClick={() => resetUser()}
                        className="text-xs font-semibold text-[#BA5827] hover:underline cursor-pointer"
                      >
                        Cancelar
                      </button>
                    </div>
                  </form>

                  <section className="mt-8 border-t border-[#D8CFC2] pt-6">
                    <div className="mb-4 flex items-center justify-between gap-3">
                      <div>
                        <h3 className="text-base font-bold text-[#3B2317]">Usuários registrados</h3>
                        <p className="text-xs text-[#7D7068]">Selecione um usuário para gerenciá-lo.</p>
                      </div>
                      <span className="rounded-full bg-[#FAF6F0] px-3 py-1 text-xs font-bold text-[#685A52]">{registeredUsers.length}</span>
                    </div>

                    {isUsersLoading ? (
                      <p className="py-6 text-center text-sm text-[#7D7068]">Carregando usuários...</p>
                    ) : visibleUsers.length === 0 ? (
                      <p className="py-6 text-center text-sm text-[#7D7068]">Nenhum usuário cadastrado.</p>
                    ) : (
                      <div className="space-y-2">
                        {visibleUsers.map((registeredUser) => (
                          <button
                            key={registeredUser.id}
                            type="button"
                            onClick={() => setSelectedUser(registeredUser)}
                            className="flex w-full items-center gap-3 rounded-2xl border border-[#DFD6C7] bg-[#FAF6F0] p-3 text-left transition-colors hover:border-[#BA5827] hover:bg-white cursor-pointer"
                          >
                            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-[#98AE9D] text-sm font-bold text-white">{registeredUser.username.charAt(0).toUpperCase()}</span>
                            <span className="min-w-0 flex-1">
                              <span className="block truncate text-sm font-semibold text-[#3B2317]">{registeredUser.username}</span>
                              <span className="block text-xs text-[#7D7068]">{formatRole(registeredUser.role)}</span>
                            </span>
                          </button>
                        ))}
                      </div>
                    )}

                    {totalUsersPages > 1 && (
                      <div className="mt-4 flex items-center justify-between">
                        <button type="button" onClick={() => setUsersPage((page) => Math.max(1, page - 1))} disabled={usersPage === 1} className="px-3 py-1.5 text-xs font-semibold text-[#685A52] disabled:opacity-40 cursor-pointer">Anterior</button>
                        <span className="text-xs font-medium text-[#7D7068]">Página {usersPage} de {totalUsersPages}</span>
                        <button type="button" onClick={() => setUsersPage((page) => Math.min(totalUsersPages, page + 1))} disabled={usersPage === totalUsersPages} className="px-3 py-1.5 text-xs font-semibold text-[#685A52] disabled:opacity-40 cursor-pointer">Próxima</button>
                      </div>
                    )}
                  </section>
                </div>
              </div>
            )}

          </div>
        </main>
      </div>
      <UserManagementModal
        user={selectedUser}
        isOpen={selectedUser !== null}
        onClose={() => setSelectedUser(null)}
        onSave={handleUpdateUser}
        onDelete={handleDeleteUser}
      />
    </div>
  );
};
