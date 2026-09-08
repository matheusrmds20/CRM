import React, { useState, useEffect } from 'react';
import { Sidebar } from '../components/layout/Sidebar';
import { Header } from '../components/layout/Header';
import { CompanyCardDetailed } from '../components/companies/CompanyCardDetailed';
import { type CompanyItem } from '../schemas/company.schema';
import { companiesService } from '../services/companies.service';
import { Filter, Loader2 } from 'lucide-react';

interface CompaniesPageProps {
  onNavigate?: (path: string) => void;
}

export const CompaniesPage: React.FC<CompaniesPageProps> = ({ onNavigate }) => {
  const [companies, setCompanies] = useState<CompanyItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchCompanies = async () => {
      try {
        setIsLoading(true);
        const data = await companiesService.getAll();
        const mapped: CompanyItem[] = data.map((c, index) => {
          const iconTypes: Array<CompanyItem['iconType']> = ['tree', 'gear', 'novo', 'textil', 'tech', 'building'];
          return {
            id: c.id.toString(),
            name: c.name,
            sector: c.cnpj || 'Geral',
            lastActivity: new Date(c.created_at).toLocaleDateString('pt-BR'),
            mainContact: 'Responsável',
            status: 'Ativo',
            description: `CNPJ: ${c.cnpj}`,
            iconType: iconTypes[index % iconTypes.length],
            isLinkedToUser: true,
          };
        });
        setCompanies(mapped);
      } catch (err) {
        console.error('Erro ao buscar empresas:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCompanies();
  }, []);

  return (
    <div className="flex h-screen w-screen bg-[#FAF6F0] overflow-hidden">
      {/* Sidebar Lateral */}
      <Sidebar currentPath="empresas" onNavigate={onNavigate} />

      {/* Conteúdo Principal */}
      <div className="flex-1 flex flex-col overflow-y-auto">
        <Header userName="Maria Silva" />

        <main className="p-8 sm:p-10 space-y-8 max-w-7xl">
          {/* Header da Página */}
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-3xl font-bold text-[#3B2317] tracking-tight">
                Empresas
              </h2>
            </div>

            {/* Filtro */}
            <button 
              title="Filtrar Empresas"
              className="p-2.5 text-[#5A4B42] hover:text-[#3B2317] hover:bg-[#EFE8DC] rounded-xl border border-[#DFD6C7] transition-all cursor-pointer"
            >
              <Filter className="w-5 h-5" />
            </button>
          </div>

          {/* Grid de Cards de Empresas do Usuário */}
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-20 bg-[#EFE8DC]/50 rounded-3xl border border-[#DFD6C7]">
              <Loader2 className="w-8 h-8 text-[#BA5827] animate-spin mb-2" />
              <p className="text-[#685A52] text-sm">Carregando empresas...</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {companies.map((company) => (
                <CompanyCardDetailed
                  key={company.id}
                  company={company}
                  isAdmin={false}
                />
              ))}
            </div>
          )}

          {!isLoading && companies.length === 0 && (
            <div className="text-center py-16 bg-[#EFE8DC]/50 rounded-3xl border border-[#DFD6C7]">
              <p className="text-[#7D7068] text-sm">Nenhuma empresa encontrada.</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};
