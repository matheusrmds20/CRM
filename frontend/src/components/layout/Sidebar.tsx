import React from 'react';
import { 
  LayoutDashboard, 
  Building2, 
  Users, 
  Settings 
} from 'lucide-react';

interface SidebarProps {
  currentPath?: string;
  onNavigate?: (path: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ currentPath = 'dashboard', onNavigate }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'empresas', label: 'Empresas', icon: Building2 },
    { id: 'leads', label: 'Leads', icon: Users },
    { id: 'config', label: 'Config', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-[#EFE9DF] border-r border-[#DED7CB] flex flex-col justify-between p-6 select-none shrink-0">
      <div>
        {/* Brand / Logo */}
        <div className="flex items-center gap-3 mb-10 px-2 cursor-pointer" onClick={() => onNavigate && onNavigate('dashboard')}>
          <div className="w-10 h-10 rounded-full border-2 border-[#98AE9D] bg-white/40 flex items-center justify-center shadow-sm">
            <span className="text-xl font-bold text-[#4A382F]">C</span>
          </div>
          <div>
            <h1 className="text-lg font-bold text-[#3B2317] leading-none">Clientel</h1>
            <span className="text-xs font-semibold text-[#8B7D74] tracking-wider uppercase">CRM</span>
          </div>
        </div>

        {/* Navigation Items (Sem Atividades) */}
        <nav className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPath === item.id;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate && onNavigate(item.id)}
                className={`w-full flex items-center gap-3.5 px-4 py-3 rounded-2xl text-sm font-medium transition-all cursor-pointer ${
                  isActive
                    ? 'bg-[#FAF6F0] text-[#B75828] shadow-sm font-semibold relative before:content-[""] before:absolute before:right-0 before:top-2 before:bottom-2 before:w-1.5 before:bg-[#B75828] before:rounded-l-full'
                    : 'text-[#685A52] hover:bg-[#E7DFD4] hover:text-[#3B2317]'
                }`}
              >
                <Icon className={`w-5 h-5 ${isActive ? 'text-[#B75828]' : 'text-[#7D7068]'}`} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Rodapé da Sidebar */}
      <div className="text-xs text-[#9E9289] px-2">
        &copy; 2026 Clientel CRM
      </div>
    </aside>
  );
};
