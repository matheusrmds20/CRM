import React, { useState, useEffect } from 'react';
import { Sidebar } from '../components/layout/Sidebar';
import { Header } from '../components/layout/Header';
import { LeadCard, type Lead } from '../components/dashboard/LeadCard';
import { CompanyCard, type Company } from '../components/dashboard/CompanyCard';
import { LeadDetailModal } from '../components/leads/LeadDetailModal';
import { leadsService } from '../services/leads.service';
import { companiesService } from '../services/companies.service';
import { getApiErrorStatus } from '../services/apiError';
import { Loader2 } from 'lucide-react';

const statusApiToFrontend: Record<string, 'Novo' | 'Em Contato' | 'Ganho' | 'Perdido'> = {
  new: 'Novo',
  contacted: 'Em Contato',
  won: 'Ganho',
  lost: 'Perdido',
};

interface DashboardPageProps {
  onNavigate?: (path: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const [leads, setLeads] = useState<Lead[]>([]);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [isLeadModalOpen, setIsLeadModalOpen] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const [leadsData, companiesData] = await Promise.all([
          leadsService.getAll().catch(() => []),
          companiesService.getAll().catch(() => []),
        ]);

        const mappedLeads: Lead[] = leadsData.slice(0, 3).map((l) => ({
          id: l.id.toString(),
          name: l.name,
          role: l.subject || 'Cliente Potencial',
          company: l.description || (l.company_id ? `Empresa #${l.company_id}` : 'Sem Empresa'),
          status: statusApiToFrontend[l.status] || 'Novo',
          date: new Date(l.created_at).toLocaleDateString('pt-BR', { month: 'short', day: 'numeric' }),
          createdDate: new Date(l.created_at).getTime(),
          email: l.email,
          phone: l.phone || undefined,
          subject: l.subject,
          description: l.description || undefined,
          estimatedValue: l.estimated_value ?? undefined,
        }));

        const iconTypes: Array<Company['iconType']> = ['tree', 'gear', 'novo', 'building'];
        const mappedCompanies: Company[] = companiesData.slice(0, 4).map((c, index) => ({
          id: c.id.toString(),
          name: c.name,
          iconType: iconTypes[index % iconTypes.length],
        }));

        setLeads(mappedLeads);
        setCompanies(mappedCompanies);
      } catch (err) {
        console.error('Erro ao carregar dados do dashboard:', err);
        setError(getApiErrorStatus(err) === 403
          ? 'Você não tem permissão para visualizar estes dados.'
          : 'Não foi possível carregar o dashboard. Tente novamente.');
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);
  return (
    <div className="flex h-screen w-screen bg-[#FAF6F0] overflow-hidden">
      {}
      <Sidebar currentPath="dashboard" onNavigate={onNavigate} />

      {}
      <div className="flex-1 flex flex-col overflow-y-auto">
        <Header onNavigate={onNavigate} />

        <main className="p-8 sm:p-10 space-y-10 max-w-7xl">
          {error && (
            <div className="bg-[#EFE8DC]/50 rounded-3xl border border-[#DFD6C7] p-6 text-center">
              <p className="text-[#B75828] text-sm font-semibold">{error}</p>
            </div>
          )}
          {}
          <section>
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-xl font-bold text-[#3B2317]">Leads recentes</h3>
            </div>
            {isLoading ? (
              <div className="flex items-center justify-center py-12 bg-[#EFE8DC]/50 rounded-3xl">
                <Loader2 className="w-6 h-6 text-[#BA5827] animate-spin" />
              </div>
            ) : leads.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {leads.map((lead) => (
                  <LeadCard
                    key={lead.id}
                    lead={lead}
                    onClick={(clickedLead) => {
                      setSelectedLead(clickedLead);
                      setIsLeadModalOpen(true);
                    }}
                  />
                ))}
              </div>
            ) : (
              <div className="py-8 text-center text-sm text-[#7D7068] bg-[#EFE8DC]/40 rounded-2xl">
                Nenhum lead recente cadastrado.
              </div>
            )}
          </section>

          {/* Seção Linked Companies & Funil */}
          <section>
            <div className="flex items-center justify-between mb-5">
              <h3 className="text-xl font-bold text-[#3B2317]">Empresas vinculadas</h3>
              
              {/* Funil visual decorativo estilizado */}
              <div className="flex items-center gap-2">
                <div className="flex flex-col items-center gap-0.5">
                  <div className="w-12 h-2 bg-[#98AE9D] rounded-t-sm" />
                  <div className="w-9 h-2 bg-[#B75828]" />
                  <div className="w-6 h-2 bg-[#CD8463]" />
                  <div className="w-3 h-2 bg-[#E3DBD0] rounded-b-sm" />
                </div>
              </div>
            </div>

            {isLoading ? (
              <div className="flex items-center justify-center py-12 bg-[#EFE8DC]/50 rounded-3xl">
                <Loader2 className="w-6 h-6 text-[#BA5827] animate-spin" />
              </div>
            ) : companies.length > 0 ? (
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-6 bg-[#EFE8DC]/60 p-6 rounded-3xl border border-[#DFD6C7]">
                {companies.map((company) => (
                  <CompanyCard key={company.id} company={company} />
                ))}
              </div>
            ) : (
              <div className="py-8 text-center text-sm text-[#7D7068] bg-[#EFE8DC]/40 rounded-2xl">
                Nenhuma empresa associada cadastrada.
              </div>
            )}
          </section>
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
    </div>
  );
};