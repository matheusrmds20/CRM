import React, { useState, useEffect } from 'react';
import { Sidebar } from '../components/layout/Sidebar';
import { Header } from '../components/layout/Header';
import { CompanyModal } from '../components/companies/CompanyModal';
import { type CompanyItem, type CompanyFormData } from '../schemas/company.schema';
import { companiesService } from '../services/companies.service';
import { Plus, Edit3, Trash2, Loader2, ChevronLeft, ChevronRight } from 'lucide-react';

interface AdminCompaniesPageProps {
  onNavigate?: (path: string) => void;
}

export const AdminCompaniesPage: React.FC<AdminCompaniesPageProps> = ({ onNavigate }) => {
  const [companies, setCompanies] = useState<CompanyItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCompany, setEditingCompany] = useState<CompanyItem | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const companiesPerPage = 10;

  const fetchCompanies = async () => {
    try {
      setIsLoading(true);
      const data = await companiesService.getAll();
      const mappedCompanies: CompanyItem[] = data.map((c, index) => {
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
      setCompanies(mappedCompanies);
      setCurrentPage(1);
    } catch (err) {
      console.error('Erro ao buscar empresas:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCompanies();
  }, []);

  const totalPages = Math.ceil(companies.length / companiesPerPage);
  const firstCompanyIndex = (currentPage - 1) * companiesPerPage;
  const visibleCompanies = companies.slice(firstCompanyIndex, firstCompanyIndex + companiesPerPage);

  useEffect(() => {
    if (totalPages > 0 && currentPage > totalPages) {
      setCurrentPage(totalPages);
    }
  }, [currentPage, totalPages]);

  const handleCreateNew = () => {
    setEditingCompany(null);
    setIsModalOpen(true);
  };

  const handleEdit = (company: CompanyItem) => {
    setEditingCompany(company);
    setIsModalOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (confirm('Tem certeza que deseja excluir esta empresa?')) {
      try {
        await companiesService.delete(Number(id));
        setCompanies((prev) => prev.filter((c) => c.id !== id));
      } catch (err: any) {
        console.error('Erro ao deletar empresa:', err);
        alert(err.response?.data?.detail || 'Erro ao deletar empresa');
      }
    }
  };

  const handleSaveCompany = async (formData: CompanyFormData) => {
    try {
      // Gera um CNPJ válido aleatório para cadastro caso o usuário forneça setor/cnpj simples
      const cnpjValido = formData.sector.replace(/\D/g, '').length === 14 
        ? formData.sector 
        : '12.345.678/0001-95';

      if (editingCompany) {
        await companiesService.update(Number(editingCompany.id), {
          name: formData.name,
        });
      } else {
        await companiesService.create({
          name: formData.name,
          cnpj: cnpjValido,
        });
      }
      await fetchCompanies();
    } catch (err: any) {
      console.error('Erro ao salvar empresa:', err);
      alert(err.response?.data?.detail || 'Erro ao salvar empresa');
    }
  };

  return (
    <div className="flex h-screen w-screen bg-[#FAF6F0] overflow-hidden">
      {/* Sidebar Lateral */}
      <Sidebar currentPath="empresas" onNavigate={onNavigate} />

      {/* Conteúdo Principal */}
      <div className="flex-1 flex flex-col overflow-y-auto">
        <Header userName="Maria Silva" onNavigate={onNavigate} />

        <main className="p-8 sm:p-10 space-y-6 max-w-7xl">
          {/* Header da Página com Título e Botão de Adicionar */}
          <div className="flex items-center justify-between">
            <h2 className="text-3xl font-bold text-[#3B2317] tracking-tight">
              Gestão de Empresas
            </h2>

            <button
              onClick={handleCreateNew}
              className="flex items-center gap-2 px-5 py-2.5 bg-[#BA5827] hover:bg-[#A14A1E] active:scale-[0.99] text-white font-medium text-sm rounded-2xl shadow-md hover:shadow-lg transition-all cursor-pointer"
            >
              <Plus className="w-4 h-4" />
              <span>Adicionar Nova Empresa</span>
            </button>
          </div>

          {/* Tabela Customizada */}
          <div className="w-full overflow-x-auto">
            {isLoading ? (
              <div className="flex flex-col items-center justify-center py-20 bg-[#EFE8DC]/50 rounded-3xl border border-[#DFD6C7]">
                <Loader2 className="w-8 h-8 text-[#BA5827] animate-spin mb-2" />
                <p className="text-[#685A52] text-sm">Carregando empresas...</p>
              </div>
            ) : (
              <table className="w-full border-separate border-spacing-y-2.5 text-left">
                {/* Cabeçalho */}
                <thead>
                  <tr className="bg-[#EFE8DC] text-[#48372F] text-sm font-semibold rounded-2xl">
                    <th className="py-3.5 px-6 rounded-l-2xl">Empresa</th>
                    <th className="py-3.5 px-6">CNPJ / Ramo</th>
                    <th className="py-3.5 px-6">Criado em</th>
                    <th className="py-3.5 px-6">Contato Principal</th>
                    <th className="py-3.5 px-6 text-center rounded-r-2xl">Ações</th>
                  </tr>
                </thead>

                {/* Linhas de Empresas */}
                <tbody>
                  {visibleCompanies.map((company, index) => {
                    const isTerracotta = (firstCompanyIndex + index) % 2 === 0;
                    const rowClass = isTerracotta
                      ? 'bg-[#B75828] text-white'
                      : 'bg-[#98AE9D] text-[#222E24] font-medium';
                    const actionIconClass = isTerracotta
                      ? 'text-white/90 hover:text-white hover:bg-white/10'
                      : 'text-[#222E24]/90 hover:text-[#222E24] hover:bg-black/5';

                    return (
                      <tr
                        key={company.id}
                        className={`${rowClass} transition-transform hover:scale-[1.003] duration-150 shadow-sm`}
                      >
                        {/* Empresa */}
                        <td className="py-4 px-6 rounded-l-2xl font-semibold text-sm sm:text-base">
                          {company.name}
                        </td>

                        {/* Ramo de Atividade */}
                        <td className="py-4 px-6 text-sm">
                          {company.sector}
                        </td>

                        {/* Última Atividade */}
                        <td className="py-4 px-6 text-sm">
                          {company.lastActivity}
                        </td>

                        {/* Contato Principal */}
                        <td className="py-4 px-6 text-sm">
                          {company.mainContact}
                        </td>

                        {/* Ações */}
                        <td className="py-4 px-6 rounded-r-2xl text-center">
                          <div className="flex items-center justify-center gap-2">
                            <button
                              onClick={() => handleEdit(company)}
                              title="Editar"
                              className={`p-1.5 rounded-lg transition-colors cursor-pointer ${actionIconClass}`}
                            >
                              <Edit3 className="w-5 h-5" />
                            </button>
                            <button
                              onClick={() => handleDelete(company.id)}
                              title="Excluir"
                              className={`p-1.5 rounded-lg transition-colors cursor-pointer ${actionIconClass}`}
                            >
                              <Trash2 className="w-5 h-5" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                  {companies.length === 0 && (
                    <tr>
                      <td colSpan={5} className="py-10 text-center text-[#7D7068] bg-[#EFE8DC]/40 rounded-2xl">
                        Nenhuma empresa cadastrada. Clique em "Adicionar Nova Empresa" para começar.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            )}
          </div>

          {/* Paginação */}
          {totalPages > 1 && (
            <div className="flex flex-wrap items-center justify-center gap-2 pt-4 text-sm font-semibold text-[#685A52]">
              <button
                onClick={() => setCurrentPage((page) => Math.max(1, page - 1))}
                disabled={currentPage === 1}
                aria-label="Página anterior"
                className="flex items-center gap-1 rounded-xl border border-[#DFD6C7] bg-white px-3 py-2 transition-colors hover:bg-[#EFE8DC] disabled:cursor-not-allowed disabled:opacity-40"
              >
                <ChevronLeft className="h-4 w-4" />
                <span className="hidden sm:inline">Anterior</span>
              </button>

              {Array.from({ length: totalPages }, (_, index) => index + 1).map((page) => (
                <button
                  key={page}
                  onClick={() => setCurrentPage(page)}
                  aria-label={`Ir para a página ${page}`}
                  aria-current={currentPage === page ? 'page' : undefined}
                  className={`h-9 min-w-9 rounded-xl border px-3 transition-colors ${
                    currentPage === page
                      ? 'border-[#BA5827] bg-[#BA5827] text-white shadow-sm'
                      : 'border-[#DFD6C7] bg-white text-[#685A52] hover:bg-[#EFE8DC] hover:text-[#3B2317]'
                  }`}
                >
                  {page}
                </button>
              ))}

              <button
                onClick={() => setCurrentPage((page) => Math.min(totalPages, page + 1))}
                disabled={currentPage === totalPages}
                aria-label="Próxima página"
                className="flex items-center gap-1 rounded-xl border border-[#DFD6C7] bg-white px-3 py-2 transition-colors hover:bg-[#EFE8DC] disabled:cursor-not-allowed disabled:opacity-40"
              >
                <span className="hidden sm:inline">Próxima</span>
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          )}
        </main>
      </div>

      {/* Modal de CRUD */}
      <CompanyModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setEditingCompany(null);
        }}
        onSave={handleSaveCompany}
        initialData={editingCompany}
      />
    </div>
  );
};
