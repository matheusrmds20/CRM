import React, { useEffect, useState } from 'react';
import { Shield, Trash2, UserRound, X } from 'lucide-react';
import { type UserResponse } from '../../services/auth.service';
import { type AdminUserRole } from '../../services/users.service';

interface UserManagementModalProps {
  user: UserResponse | null;
  isOpen: boolean;
  onClose: () => void;
  onSave: (userId: number, payload: { username: string; role: AdminUserRole }) => Promise<void>;
  onDelete: (userId: number) => Promise<void>;
}

const roleLabels: Record<AdminUserRole, string> = {
  admin: 'Administrador',
  manager: 'Gerente',
  sales: 'Vendedor',
};

const formatDate = (date?: string) =>
  date ? new Date(date).toLocaleDateString('pt-BR', { dateStyle: 'long' }) : 'Não informado';

export const UserManagementModal: React.FC<UserManagementModalProps> = ({
  user,
  isOpen,
  onClose,
  onSave,
  onDelete,
}) => {
  const [username, setUsername] = useState('');
  const [role, setRole] = useState<AdminUserRole>('sales');
  const [isSaving, setIsSaving] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user || !isOpen) return;
    setUsername(user.username);
    setRole(user.role);
    setConfirmDelete(false);
    setError(null);
  }, [user, isOpen]);

  if (!isOpen || !user) return null;

  const handleSave = async () => {
    setIsSaving(true);
    setError(null);
    try {
      await onSave(user.id, { username, role });
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Não foi possível atualizar o usuário.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    setError(null);
    try {
      await onDelete(user.id);
      onClose();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Não foi possível excluir o usuário.');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-md">
      <div className="w-full max-w-lg overflow-hidden rounded-[2rem] border border-[#E3DBD0] bg-[#FAF6F0] shadow-[0_25px_60px_-15px_rgba(59,35,23,0.35)] animate-modal-enter">
        <div className="flex items-center justify-between border-b border-[#E3DBD0] bg-[#EFE8DC] px-6 py-5">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#98AE9D] text-white">
              <UserRound className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-[#3B2317]">Gerenciar usuário</h3>
              <p className="text-xs text-[#7D7068]">ID #{user.id}</p>
            </div>
          </div>
          <button onClick={onClose} aria-label="Fechar modal" className="rounded-full p-1.5 text-[#7D7068] transition-colors hover:bg-black/5 hover:text-[#3B2317] cursor-pointer">
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-5 p-6">
          <div className="flex items-center gap-3 rounded-2xl border border-[#DFD6C7] bg-[#F4F1EA] p-4">
            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-[#BA5827] text-base font-bold text-white">
              {user.username.charAt(0).toUpperCase()}
            </div>
            <div className="min-w-0">
              <p className="truncate font-semibold text-[#3B2317]">{user.username}</p>
              <p className="text-xs text-[#7D7068]">Cadastrado em {formatDate(user.created_at)}</p>
            </div>
          </div>

          <div>
            <label className="mb-1.5 ml-1 block text-xs font-semibold text-[#48372F]">Usuário</label>
            <input value={username} onChange={(event) => setUsername(event.target.value)} className="w-full rounded-xl border border-[#B8AA9A] bg-white px-4 py-2.5 text-sm text-[#3B2317] focus:outline-none focus:ring-2 focus:ring-[#77917B]/20" />
          </div>

          <div>
            <label className="mb-1.5 ml-1 block text-xs font-semibold text-[#48372F]">Perfil</label>
            <div className="relative">
              <Shield className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-[#5A4B42]" />
              <select value={role} onChange={(event) => setRole(event.target.value as AdminUserRole)} className="w-full appearance-none rounded-xl border border-[#B8AA9A] bg-white py-2.5 pl-10 pr-4 text-sm text-[#3B2317] focus:outline-none focus:ring-2 focus:ring-[#77917B]/20 cursor-pointer">
                {(Object.keys(roleLabels) as AdminUserRole[]).map((value) => <option key={value} value={value}>{roleLabels[value]}</option>)}
              </select>
            </div>
          </div>

          {error && <p className="rounded-xl bg-red-100 p-3 text-xs font-medium text-red-700">{error}</p>}

          {confirmDelete ? (
            <div className="rounded-2xl border border-red-200 bg-red-50 p-4">
              <p className="text-sm font-semibold text-red-800">Excluir este usuário?</p>
              <p className="mt-1 text-xs text-red-700">Esta ação não pode ser desfeita.</p>
              <div className="mt-3 flex justify-end gap-3">
                <button onClick={() => setConfirmDelete(false)} disabled={isDeleting} className="px-4 py-2 text-xs font-semibold text-[#685A52] cursor-pointer">Cancelar</button>
                <button onClick={handleDelete} disabled={isDeleting} className="rounded-xl bg-red-600 px-4 py-2 text-xs font-semibold text-white hover:bg-red-700 disabled:opacity-50 cursor-pointer">{isDeleting ? 'Excluindo...' : 'Excluir usuário'}</button>
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-between border-t border-[#E3DBD0] pt-5">
              <button onClick={() => setConfirmDelete(true)} className="flex items-center gap-2 rounded-xl px-3 py-2 text-xs font-semibold text-red-700 hover:bg-red-50 cursor-pointer">
                <Trash2 className="h-4 w-4" /> Excluir
              </button>
              <div className="flex gap-3">
                <button onClick={onClose} disabled={isSaving} className="px-4 py-2 text-xs font-semibold text-[#685A52] cursor-pointer">Cancelar</button>
                <button onClick={handleSave} disabled={isSaving || username.trim().length < 3} className="rounded-xl bg-[#BA5827] px-5 py-2 text-xs font-semibold text-white shadow-sm hover:bg-[#A14A1E] disabled:opacity-50 cursor-pointer">{isSaving ? 'Salvando...' : 'Salvar alterações'}</button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
