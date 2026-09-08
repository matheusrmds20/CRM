import React from 'react';
import { Bell, LogOut } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface HeaderProps {
  userName?: string;
  userAvatar?: string;
}

export const Header: React.FC<HeaderProps> = ({ 
  userAvatar = 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=120&auto=format&fit=crop&q=80'
}) => {
  const { user, logout } = useAuth();
  const displayName = user?.username ? user.username.charAt(0).toUpperCase() + user.username.slice(1) : 'Usuário';

  return (
    <header className="h-20 bg-transparent flex items-center justify-between px-8 py-4 border-b border-[#E3DBD0]">
      {/* Título de Boas-vindas */}
      <h2 className="text-2xl font-bold text-[#3B2317] tracking-tight">
        Welcome Back, {displayName}
      </h2>

      {/* Notificação, Logout & Perfil */}
      <div className="flex items-center gap-4">
        {/* Notificações */}
        <button className="relative p-2 text-[#685A52] hover:text-[#3B2317] transition-colors rounded-full hover:bg-black/5 cursor-pointer">
          <Bell className="w-5 h-5" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-[#B75828] rounded-full ring-2 ring-[#FAF6F0]" />
        </button>

        {/* Logout */}
        <button 
          onClick={logout}
          title="Sair do sistema"
          className="p-2 text-[#685A52] hover:text-red-600 transition-colors rounded-full hover:bg-red-50 cursor-pointer"
        >
          <LogOut className="w-5 h-5" />
        </button>

        {/* Avatar */}
        <div className="w-10 h-10 rounded-full overflow-hidden border-2 border-white shadow-sm cursor-pointer hover:ring-2 hover:ring-[#B75828]/40 transition-all">
          <img src={userAvatar} alt={displayName} className="w-full h-full object-cover" />
        </div>
      </div>
    </header>
  );
};

