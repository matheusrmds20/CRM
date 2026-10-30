import React, { useState, useMemo, useEffect } from 'react';
import { Sidebar } from '../components/layout/Sidebar';
import { Header } from '../components/layout/Header';
import { LeadCardDetailed } from '../components/dashboard/LeadCard';
import { LeadCreateModal } from '../components/leads/LeadCreateModal';
import { LeadDetailModal } from '../components/leads/LeadDetailModal';
import { type LeadCreateFormData, type LeadItem, type LeadStatus } from '../schemas/lead.schema';
import { leadsService, type LeadApiResponse } from '../services/leads.service';
import { companiesService, type CompanyApiResponse } from '../services/companies.service';
import { getApiErrorStatus } from '../services/apiError';
import { Filter, ArrowUpDown, Loader2, Plus, Search } from 'lucide-react';

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

const mapLead = (lead: LeadApiResponse): LeadItem => ({
  id: lead.id.toString(),
  name: lead.name,
  role: lead.subject || 'Cliente Potencial',
  company: lead.description || (lead.company_id ? `Empresa #${lead.company_id}` : 'Sem Empresa'),
  status: statusApiToFrontend[lead.status] || 'Novo',
  date: new Date(lead.created_at).toLocaleDateString('pt-BR', { month: 'short', day: 'numeric' }),
  createdDate: new Date(lead.created_at).getTime(),
  targetDate: lead.updated_at ? new Date(lead.updated_at).toLocaleDateString('pt-BR', { month: 'short', day: 'numeric' }) : undefined,
  email: lead.email,
  phone: lead.phone || undefined,
  subject: lead.subject,
  description: lead.description || undefined,
  estimatedValue: lead.estimated_value ?? undefined,
});

interface LeadsPageProps {
  onNavigate?: (path: string) => void;
}

export const LeadsPage: React.FC<LeadsPageProps> = ({ onNavigate }) => {
  const [leads, setLeads] = useState<LeadItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStatus, setSelectedStatus] = useState<'Todos os Statuses' | LeadStatus>('Todos os Statuses');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [selectedLead, setSelectedLead] = useState<LeadItem | null>(null);
  const [isLeadModalOpen, setIsLeadModalOpen] = useState(false);
  const [companies, setCompanies] = useState<CompanyApiResponse[]>([]);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isCreatingLead, setIsCreatingLead] = useState(false);

  useEffect(() => {
    let isMounted = true;

    Promise.all([leadsService.getAll(), companiesService.getAll()])
      .then(([leadData, companyData]) => {
        if (!isMounted) return;
        setLeads(leadData.map(mapLead));
        setCompanies(companyData);
      })
      .catch((err) => {
        if (!isMounted) return;
        console.error('Erro ao carregar dados de leads:', err);
        setError(getApiErrorStatus(err) === 403
          ? 'Você não tem permissão para visualizar os leads.'
          : 'Não foi possível carregar os leads. Tente novamente.');
      })
      .finally(() => {
        if (isMounted) setIsLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, []);

  const handleCreateLead = async (data: LeadCreateFormData) => {
    setIsCreatingLead(true);
    try {
      const created = await leadsService.create({
        name: data.name,
        email: data.email,
        phone: data.phone,
        company_id: data.companyId ?? null,
        subject: data.subject,
        description: data.description || null,
        estimated_value: data.estimatedValue,
        status: data.status,
      });
      setLeads((current) => [mapLead(created), ...current]);
      setIsCreateModalOpen(false);
    } catch (err) {
      console.error('Erro ao criar lead:', err);
      throw err;
    } finally {
      setIsCreatingLead(false);
    }
  };

  
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
        return a.createdDate - b.createdDate;
      }
      return b.createdDate - a.createdDate;
    });

    return result;
  }, [leads, searchTerm, selectedStatus, sortOrder]);

  return (
    <div className="flex h-screen w-screen bg-[#FAF6F0] overflow-hidden">
      {}
      <Sidebar currentPath="leads" onNavigate={onNavigate} />

      {}
      <div className="flex-1 flex flex-col overflow-y-auto">
        <Header onNavigate={onNavigate} />

        <main className="p-8 sm:p-10 space-y-8 max-w-7xl">
          {}
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <h2 className="text-3xl font-bold text-[#3B2317] tracking-tight">
              Todas as Leads
            </h2>

            <div className="flex flex-wrap items-center gap-3 sm:gap-4 relative">
              <button
                onClick={() => setIsCreateModalOpen(true)}
                className="flex items-center gap-2 px-5 py-2.5 bg-[#BA5827] hover:bg-[#A14A1E] active:scale-[0.99] text-white font-medium text-sm rounded-2xl shadow-md hover:shadow-lg transition-all cursor-pointer"
              >
                <Plus className="w-4 h-4" />
                <span>Criar Lead</span>
              </button>

              {}
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
                <LeadCardDetailed
                  key={lead.id}
                  lead={lead}
                  onClick={(clickedLead) => {
                    setSelectedLead(clickedLead);
                    setIsLeadModalOpen(true);
                  }}
                />
              ))}
            </div>
          )}

          {!isLoading && filteredAndSortedLeads.length === 0 && !error && (
            <div className="text-center py-16 bg-[#EFE8DC]/50 rounded-3xl border border-[#DFD6C7]">
              <p className="text-[#7D7068] text-sm">Nenhum lead encontrado.</p>
            </div>
          )}

          {!isLoading && error && (
            <div className="text-center py-16 bg-[#EFE8DC]/50 rounded-3xl border border-[#DFD6C7]">
              <p className="text-[#B75828] text-sm font-semibold">{error}</p>
            </div>
          )}
        </main>
      </div>

      {/* Modal de Detalhe do Lead */}
      <LeadDetailModal
        lead={selectedLead}
        isOpen={isLeadModalOpen}
        onClose={() => {
          setIsLeadModalOpen(false);
          setSelectedLead(null);
        }}
        onSaved={(updated) => {
          setLeads((prev) => prev.map((l) => (l.id === updated.id ? updated : l)));
        }}
        onDeleted={(id) => {
          setLeads((prev) => prev.filter((lead) => lead.id !== id));
        }}
      />

      <LeadCreateModal
        companies={companies}
        isOpen={isCreateModalOpen}
        isSaving={isCreatingLead}
        onClose={() => setIsCreateModalOpen(false)}
        onSave={handleCreateLead}
      />
    </div>
  );
};