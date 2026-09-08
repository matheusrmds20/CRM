import React, { useState, useMemo, useEffect } from 'react';
import { Sidebar } from '../components/layout/Sidebar';
import { Header } from '../components/layout/Header';
import { LeadCardDetailed } from '../components/dashboard/LeadCard';
import { type LeadItem, type LeadStatus } from '../schemas/lead.schema';
import { leadsService, type LeadApiResponse } from '../services/leads.service';
import { Filter, ArrowUpDown, Loader2, Search } from 'lucide-react';

const allStatuses: Array<'Todos os Statuses' | LeadStatus> = [
  'Todos os Statuses',
  'Novo',
  'Em Contato',
  'Qualificado',
  'Negociação',
  'Ganho',
  'Perdido',
];

const statusApiToFrontend: Record<string, LeadStatus> = {
  new: 'Novo',
  contacted: 'Em Contato',
  won: 'Ganho',
  lost: 'Perdido',
};

const avatarUrls = [
  'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=120&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=120&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=120&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=120&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=120&auto=format&fit=crop&q=80',
];

interface LeadsPageProps {
  onNavigate?: (path: string) => void;
}

export const LeadsPage: React.FC<LeadsPageProps> = ({ onNavigate }) => {
  const [leads, setLeads] = useState<LeadItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStatus, setSelectedStatus] = useState<'Todos os Statuses' | LeadStatus>('Todos os Statuses');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [isFilterOpen, setIsFilterOpen] = useState(false);

  useEffect(() => {
    const fetchLeads = async () => {
      try {
        setIsLoading(true);
        const data = await leadsService.getAll();
        const mapped: LeadItem[] = data.map((l: LeadApiResponse, index: number) => ({
          id: l.id.toString(),
          name: l.name,
          role: l.subject || 'Cliente Potencial',
          company: l.description || (l.company_id ? `Empresa #${l.company_id}` : 'Sem Empresa'),
          avatar: avatarUrls[index % avatarUrls.length],
          status: statusApiToFrontend[l.status] || 'Novo',
          date: new Date(l.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          targetDate: l.updated_at ? new Date(l.updated_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : undefined,
        }));
        setLeads(mapped);
      } catch (err) {
        console.error('Erro ao buscar leads:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchLeads();
  }, []);

  // Filtragem por status, busca por texto e Ordenação dos Leads
  const filteredAndSortedLeads = useMemo(() => {
    let result = [...leads];

    if (searchTerm.trim() !== '') {
      const term = searchTerm.toLowerCase();
      result = result.filter(
        (lead) =>
          lead.name.toLowerCase().includes(term) ||
          lead.company.toLowerCase().includes(term) ||
          lead.role.toLowerCase().includes(term)
      );
    }

    if (selectedStatus !== 'Todos os Statuses') {
      result = result.filter((lead) => lead.status === selectedStatus);
    }

    result.sort((a, b) => {
      if (sortOrder === 'asc') {
        return a.date.localeCompare(b.date);
      }
      return b.date.localeCompare(a.date);
    });

    return result;
  }, [leads, searchTerm, selectedStatus, sortOrder]);

  return (
    <div className="flex h-screen w-screen bg-[#FAF6F0] overflow-hidden">
      {/* Sidebar Lateral */}
      <Sidebar currentPath="leads" onNavigate={onNavigate} />

      {/* Área Central */}
      <div className="flex-1 flex flex-col overflow-y-auto">
        <Header userName="Maria Silva" />

        <main className="p-8 sm:p-10 space-y-8 max-w-7xl">
          {/* Header da Página com Título, Busca, Filtro e Ordenação */}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <h2 className="text-3xl font-bold text-[#3B2317] tracking-tight">
              Todas as Leads
            </h2>

            <div className="flex flex-wrap items-center gap-3 sm:gap-4 relative">
              {/* Barra de Busca de Leads */}
              <div className="relative flex items-center">
                <Search className="absolute left-3.5 w-4 h-4 text-[#8C988D]" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Pesquisar leads..."
                  className="w-56 sm:w-64 pl-10 pr-4 py-2 bg-[#DDE6DC]/70 border border-[#BACBB9] rounded-xl text-sm text-[#3B2317] placeholder-[#798C7B] focus:outline-none focus:ring-2 focus:ring-[#7A937D]/30 transition-all"
                />
              </div>

              {/* Dropdown de Filtros (Todos os Statuses) */}
              <div className="relative">
                <button
                  onClick={() => setIsFilterOpen(!isFilterOpen)}
                  className="flex items-center gap-2 px-4 py-2 bg-[#EFE8DC] hover:bg-[#E5DDD0] text-[#48372F] rounded-xl text-sm font-medium border border-[#DFD6C7] transition-all cursor-pointer"
                >
                  <Filter className="w-4 h-4 text-[#BA5827]" />
                  <span>Filtros ({selectedStatus})</span>
                </button>

                {isFilterOpen && (
                  <div className="absolute right-0 mt-2 w-52 bg-[#FAF6F0] rounded-2xl shadow-xl border border-[#DFD6C7] p-2 z-30 space-y-1">
                    {allStatuses.map((status) => (
                      <button
                        key={status}
                        onClick={() => {
                          setSelectedStatus(status);
                          setIsFilterOpen(false);
                        }}
                        className={`w-full text-left px-3 py-2 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                          selectedStatus === status
                            ? 'bg-[#BA5827] text-white'
                            : 'text-[#48372F] hover:bg-[#EFE8DC]'
                        }`}
                      >
                        {status}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              {/* Botão de Ordenar por Data */}
              <button
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                className="flex items-center gap-2 px-4 py-2 bg-[#EFE8DC] hover:bg-[#E5DDD0] text-[#48372F] rounded-xl text-sm font-medium border border-[#DFD6C7] transition-all cursor-pointer"
              >
                <ArrowUpDown className="w-4 h-4 text-[#BA5827]" />
                <span>Ordenar por Data</span>
              </button>
            </div>
          </div>

          {/* Grid de Cards de Leads */}
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20 bg-[#EFE8DC]/50 rounded-3xl border border-[#DFD6C7]">
              <Loader2 className="w-8 h-8 text-[#BA5827] animate-spin mb-2" />
              <p className="text-[#685A52] text-sm">Carregando leads...</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredAndSortedLeads.map((lead) => (
                <LeadCardDetailed key={lead.id} lead={lead} />
              ))}
            </div>
          )}

          {!isLoading && filteredAndSortedLeads.length === 0 && (
            <div className="text-center py-16 bg-[#EFE8DC]/50 rounded-3xl border border-[#DFD6C7]">
              <p className="text-[#7D7068] text-sm">Nenhum lead encontrado.</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};
