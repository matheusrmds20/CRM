import React from 'react';
import { LogOut } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

interface HeaderProps {
  userName?: string;
  onNavigate?: (path: string) => void;
}

export const Header: React.FC<HeaderProps> = ({ onNavigate }) => {
  const { user, logout } = useAuth();
  const displayName = user?.username ? user.username.charAt(0).toUpperCase() + user.username.slice(1) : 'Usuário';

  return (
    <header className="h-20 bg-transparent flex items-center justify-between px-8 py-4 border-b border-[#E3DBD0]">
      {/* Título de Boas-vindas */}
      <h2 className="text-2xl font-bold text-[#3B2317] tracking-tight">
        Boas-vindas, {displayName}
      </h2>

      {/* Logout & Perfil */}
      <div className="flex items-center gap-4">
        {/* Logout */}
        <button 
          onClick={logout}
          title="Sair do sistema"
          className="p-2 text-[#685A52] hover:text-red-600 transition-colors rounded-full hover:bg-red-50 cursor-pointer"
        >
          <LogOut className="w-5 h-5" />
        </button>

        {/* Perfil */}
        <button
          type="button"
          title="Abrir configurações"
          aria-label="Abrir configurações"
          onClick={() => onNavigate?.('config')}
          className="w-10 h-10 rounded-full border-2 border-white bg-[#98AE9D] text-white text-base font-bold shadow-sm cursor-pointer hover:ring-2 hover:ring-[#B75828]/40 transition-all"
        >
          {displayName.charAt(0).toUpperCase()}
        </button>
      </div>
    </header>
  );
};

