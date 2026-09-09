import React, { useEffect, useState, useCallback, useRef } from 'react';
import { X, Phone, Calendar, Mail, MessageCircle, ChevronUp, ChevronDown, User, IndianRupee } from 'lucide-react';
import { type LeadItem, type LeadStatus } from '../../schemas/lead.schema';
import {
  activitiesService,
  type ActivityApiResponse,
  type ActivityTypeApi,
} from '../../services/activities.service';
import { proposalsService, type ProposalApiResponse } from '../../services/proposals.service';
import { leadsService, type LeadUpdatePayload } from '../../services/leads.service';

interface LeadDetailModalProps {
  lead: LeadItem | null;
  isOpen: boolean;
  onClose: () => void;
  onSaved?: (updated: LeadItem) => void;
}

const activityLabels: Record<ActivityTypeApi, string> = {
  call: 'Ligação',
  meeting: 'Reunião',
  email: 'E-mail',
  whatsapp: 'WhatsApp',
  other: 'Outro',
};

const activityStatusMap: Record<ActivityTypeApi, { label: string; icon: React.ReactNode }> = {
  call: {
    label: 'Ligação',
    icon: <Phone className="w-5 h-5" />,
  },
  meeting: {
    label: 'Reunião',
    icon: <Calendar className="w-5 h-5" />,
  },
  email: {
    label: 'E-mail',
    icon: <Mail className="w-5 h-5" />,
  },
  whatsapp: {
    label: 'WhatsApp',
    icon: <MessageCircle className="w-5 h-5" />,
  },
  other: {
    label: 'Outro',
    icon: <Phone className="w-5 h-5" />,
  },
};

const allStatuses: LeadStatus[] = [
  'Novo',
  'Em Contato',
  'Qualificado',
  'Negociação',
  'Ganho',
  'Perdido',
];

const statusToApi: Record<LeadStatus, string> = {
  'Novo': 'new',
  'Em Contato': 'contacted',
  'Qualificado': 'contacted',
  'Negociação': 'contacted',
  'Ganho': 'won',
  'Perdido': 'lost',
};

const apiToStatus: Record<string, LeadStatus> = {
  new: 'Novo',
  contacted: 'Em Contato',
  won: 'Ganho',
  lost: 'Perdido',
};

const proposalStatusLabels: Record<string, string> = {
  pending: 'Pendente',
  accepted: 'Aceita',
  rejected: 'Recusada',
};

// Traduz o dia para abreviação em pt-BR
function formatDay(dateStr: string): string {
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('pt-BR', { month: 'short', day: 'numeric' });
  } catch {
    return '';
  }
}

function formatCurrency(value: number): string {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    maximumFractionDigits: 0,
  }).format(value || 0);
}

export const LeadDetailModal: React.FC<LeadDetailModalProps> = ({
  lead,
  isOpen,
  onClose,
  onSaved,
}) => {
  const [activities, setActivities] = useState<ActivityApiResponse[]>([]);
  const [proposals, setProposals] = useState<ProposalApiResponse[]>([]);
  const [isActivityOpen, setIsActivityOpen] = useState(true);
  const [isProposalOpen, setIsProposalOpen] = useState(true);
  const [activeTab, setActiveTab] = useState<ActivityTypeApi>('call');
  const [isLoadingData, setIsLoadingData] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [isClosing, setIsClosing] = useState(false);
  const closeTimeoutRef = useRef<number | null>(null);
  const onCloseRef = useRef(onClose);

  useEffect(() => {
    onCloseRef.current = onClose;
  }, [onClose]);

  const closeModal = useCallback(() => {
    if (closeTimeoutRef.current !== null) {
      window.clearTimeout(closeTimeoutRef.current);
    }
    setIsClosing(true);
    closeTimeoutRef.current = window.setTimeout(() => {
      closeTimeoutRef.current = null;
      onCloseRef.current();
    }, 250);
  }, []);

  useEffect(() => {
    if (isOpen) {
      if (closeTimeoutRef.current !== null) {
        window.clearTimeout(closeTimeoutRef.current);
        closeTimeoutRef.current = null;
      }
      setIsClosing(false);
    }

    return () => {
      if (closeTimeoutRef.current !== null) {
        window.clearTimeout(closeTimeoutRef.current);
        closeTimeoutRef.current = null;
      }
    };
  }, [isOpen]);

  // Campos editáveis do lead
  const [name, setName] = useState('');
  const [status, setStatus] = useState<LeadStatus>('Novo');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [subject, setSubject] = useState('');
  const [description, setDescription] = useState('');
  const [estimatedValue, setEstimatedValue] = useState('');

  const leadId = lead ? parseInt(lead.id, 10) : null;

  useEffect(() => {
    if (!isOpen || !lead) return;

    setName(lead.name || '');
    setStatus(lead.status || 'Novo');
    setEmail(lead.email || '');
    setPhone(lead.phone || '');
    setSubject(lead.subject || lead.role || '');
    setDescription(lead.description || lead.company || '');
    setEstimatedValue(lead.estimatedValue ? String(lead.estimatedValue) : '');
    setActiveTab('call');
    setIsActivityOpen(true);
    setIsProposalOpen(true);

    const loadData = async () => {
      if (leadId === null) return;
      setIsLoadingData(true);
      try {
        const [acts, props] = await Promise.all([
          activitiesService.getByLeadId(leadId).catch(() => []),
          proposalsService.getByLeadId(leadId).catch(() => []),
        ]);
        setActivities(acts);
        setProposals(props);
      } finally {
        setIsLoadingData(false);
      }
    };

    loadData();
  }, [isOpen, lead, leadId]);

  const handleDiscard = useCallback(() => {
    if (lead) {
      setName(lead.name || '');
      setStatus(lead.status || 'Novo');
      setEmail(lead.email || '');
      setPhone(lead.phone || '');
      setSubject(lead.subject || lead.role || '');
      setDescription(lead.description || lead.company || '');
      setEstimatedValue(lead.estimatedValue ? String(lead.estimatedValue) : '');
    }
    closeModal();
  }, [lead, closeModal]);

  const handleSave = async () => {
    if (leadId === null || !lead) return;
    setIsSaving(true);
    try {
      const payload: LeadUpdatePayload = {
        name,
        email,
        phone: phone || null,
        subject,
        description: description || null,
        estimated_value: estimatedValue ? parseFloat(estimatedValue) : undefined,
        status: statusToApi[status] as LeadUpdatePayload['status'],
      };
      const updated = await leadsService.update(leadId, payload);
      if (onSaved) {
        onSaved({
          ...lead,
          name: updated.name,
          email: updated.email,
          phone: updated.phone || undefined,
          subject: updated.subject,
          description: updated.description || undefined,
          estimatedValue: updated.estimated_value ?? undefined,
          status: apiToStatus[updated.status] || lead.status,
        });
      }
      closeModal();
    } catch (err) {
      console.error('Erro ao salvar lead:', err);
    } finally {
      setIsSaving(false);
    }
  };

  // A aba padrão "Call" mostra todas as atividades; as demais filtram por tipo.
  const displayActivities =
    activeTab === 'call' ? activities : activities.filter((a) => a.activity_type === activeTab);

  if (!isOpen || !lead) return null;

  return (
    <div className={`fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-md ${isClosing ? 'animate-overlay-exit' : 'animate-overlay-fade'}`}>
      <div className={`relative w-full max-w-5xl bg-[#FAF6F0] rounded-[2rem] border border-[#E3DBD0] shadow-[0_25px_60px_-15px_rgba(59,35,23,0.35)] overflow-hidden flex flex-col max-h-[92vh] ${isClosing ? 'animate-modal-exit' : 'animate-modal-enter'} hover:shadow-[0_30px_70px_-15px_rgba(59,35,23,0.45)]`}>
        {/* Header do Modal */}
        <div className="flex items-center justify-between px-8 py-6 border-b border-[#E8E0D4] bg-gradient-to-r from-[#F7F1E8] to-[#EFE8DC]">
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="w-16 h-16 rounded-full bg-[#98AE9D] text-white text-2xl font-bold flex items-center justify-center border-[3px] border-white shadow-lg">
                {lead.name.charAt(0).toUpperCase()}
              </div>
              <span className="absolute bottom-0.5 right-0.5 w-4 h-4 bg-[#7A937D] rounded-full border-2 border-white" />
            </div>
            <div>
              <p className="text-[11px] font-semibold uppercase tracking-widest text-[#BA5827]">
                Detalhes do Lead
              </p>
              <h3 className="text-2xl font-bold text-[#3B2317] tracking-tight leading-tight">
                {lead.name}
              </h3>
            </div>
          </div>
          <button
            onClick={closeModal}
            className="p-2 text-[#7D7068] hover:text-[#3B2317] hover:bg-white hover:shadow-sm rounded-full transition-all cursor-pointer"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Corpo do Modal */}
        <div className="flex flex-col md:flex-row gap-7 p-8 overflow-y-auto">
          {/* Coluna Esquerda - Formulário */}
          <div className="flex-1 space-y-4 min-w-0">
            {/* Nome */}
            <div>
              <label className="block text-xs font-semibold text-[#685A52] mb-1.5 ml-1 uppercase tracking-wide">
                Nome Completo
              </label>
              <div className="relative">
                <User className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#A89C90]" />
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Nome do lead"
                  className="w-full pl-12 pr-4 py-3.5 bg-white border border-[#B8AA9A] rounded-2xl text-base text-[#3B2317] placeholder-[#B3A79B] shadow-sm focus:outline-none focus:ring-2 focus:ring-[#7A937D]/30 focus:border-[#7A937D] transition-all"
                />
              </div>
            </div>

            {/* Status (dropdown) */}
            <div>
              <label className="block text-xs font-semibold text-[#685A52] mb-1.5 ml-1 uppercase tracking-wide">
                Status
              </label>
              <div className="relative">
                <select
                  value={status}
                  onChange={(e) => setStatus(e.target.value as LeadStatus)}
                  className="w-full pl-4 pr-10 py-3.5 bg-white border border-[#B8AA9A] rounded-2xl text-base text-[#3B2317] shadow-sm focus:outline-none focus:ring-2 focus:ring-[#7A937D]/30 focus:border-[#7A937D] appearance-none cursor-pointer transition-all"
                >
                  {allStatuses.map((s) => (
                    <option key={s} value={s}>
                      {s}
                    </option>
                  ))}
                </select>
                <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#5A4B42] pointer-events-none" />
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="block text-xs font-semibold text-[#685A52] mb-1.5 ml-1 uppercase tracking-wide">
                E-mail
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="email@exemplo.com"
                className="w-full px-4 py-3.5 bg-white border border-[#B8AA9A] rounded-2xl text-base text-[#3B2317] placeholder-[#B3A79B] shadow-sm focus:outline-none focus:ring-2 focus:ring-[#7A937D]/30 focus:border-[#7A937D] transition-all"
              />
            </div>

            {/* Telefone */}
            <div>
              <label className="block text-xs font-semibold text-[#685A52] mb-1.5 ml-1 uppercase tracking-wide">
                Telefone
              </label>
              <input
                type="text"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="+55 11 98765-4321"
                className="w-full px-4 py-3.5 bg-white border border-[#B8AA9A] rounded-2xl text-base text-[#3B2317] placeholder-[#B3A79B] shadow-sm focus:outline-none focus:ring-2 focus:ring-[#7A937D]/30 focus:border-[#7A937D] transition-all"
              />
            </div>

            {/* Assunto */}
            <div>
              <label className="block text-xs font-semibold text-[#685A52] mb-1.5 ml-1 uppercase tracking-wide">
                Assunto
              </label>
              <input
                type="text"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                placeholder="Assunto"
                className="w-full px-4 py-3.5 bg-white border border-[#B8AA9A] rounded-2xl text-base text-[#3B2317] placeholder-[#B3A79B] shadow-sm focus:outline-none focus:ring-2 focus:ring-[#7A937D]/30 focus:border-[#7A937D] transition-all"
              />
            </div>

            {/* Descrição */}
            <div>
              <label className="block text-xs font-semibold text-[#685A52] mb-1.5 ml-1 uppercase tracking-wide">
                Descrição
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Descrição"
                rows={5}
                className="w-full px-4 py-3.5 bg-white border border-[#B8AA9A] rounded-2xl text-base text-[#3B2317] placeholder-[#B3A79B] shadow-sm focus:outline-none focus:ring-2 focus:ring-[#7A937D]/30 focus:border-[#7A937D] resize-none transition-all"
              />
            </div>

            {/* Valor Estimado */}
            <div>
              <label className="block text-xs font-semibold text-[#685A52] mb-1.5 ml-1 uppercase tracking-wide">
                Valor Estimado
              </label>
              <div className="relative">
                <IndianRupee className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#A89C90]" />
                <input
                  type="number"
                  value={estimatedValue}
                  onChange={(e) => setEstimatedValue(e.target.value)}
                  placeholder="R$ 15.000"
                  className="w-full pl-12 pr-4 py-3.5 bg-white border border-[#B8AA9A] rounded-2xl text-base text-[#3B2317] placeholder-[#B3A79B] shadow-sm focus:outline-none focus:ring-2 focus:ring-[#7A937D]/30 focus:border-[#7A937D] transition-all"
                />
              </div>
            </div>

            {/* Botões de Ação */}
            <div className="flex items-center gap-4 pt-5">
              <button
                onClick={handleSave}
                disabled={isSaving}
                className="flex-1 px-6 py-3.5 bg-gradient-to-b from-[#C05A2A] to-[#B04E1F] hover:from-[#D0652F] hover:to-[#B75828] text-white text-base font-semibold rounded-2xl shadow-lg shadow-[#B75828]/25 hover:shadow-xl hover:shadow-[#B75828]/30 transition-all cursor-pointer disabled:opacity-50 active:scale-[0.98]"
              >
                {isSaving ? 'Salvando...' : 'Salvar'}
              </button>
              <button
                onClick={handleDiscard}
                className="flex-1 px-6 py-3.5 bg-[#E8E1D6] hover:bg-[#DDD4C6] text-[#5A4B42] text-base font-semibold rounded-2xl shadow-sm hover:shadow-md transition-all cursor-pointer active:scale-[0.98]"
              >
                Descartar
              </button>
            </div>
          </div>

          {/* Coluna Direita - Activity History */}
          <div className="w-full md:w-80 shrink-0 space-y-5">
            {/* Activity History */}
            <div className="bg-white rounded-3xl border border-[#E8E0D4] shadow-sm overflow-hidden">
              <button
                onClick={() => setIsActivityOpen(!isActivityOpen)}
                className="w-full flex items-center justify-between px-5 py-4 text-[#3B2317] font-bold text-base cursor-pointer hover:bg-[#F7F3ED] transition-colors"
              >
                <span className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-[#BA5827]" />
                  Histórico de atividades
                </span>
                {isActivityOpen ? (
                  <ChevronUp className="w-5 h-5" />
                ) : (
                  <ChevronDown className="w-5 h-5" />
                )}
              </button>

              {isActivityOpen && (
                <div className="px-4 pb-4 space-y-4">
                  {/* Tabs */}
                  <div className="grid grid-cols-4 gap-2 bg-[#F1ECE4] rounded-2xl p-1.5">
                    {(['call', 'meeting', 'email', 'whatsapp'] as ActivityTypeApi[]).map(
                      (tab) => {
                        const cfg = activityStatusMap[tab];
                        const isActive = activeTab === tab;
                        return (
                          <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            aria-pressed={isActive}
                            className={`flex flex-col items-center gap-1.5 px-2 py-2.5 rounded-xl text-xs font-semibold transition-colors focus:outline-none cursor-pointer ${
                              isActive
                                ? 'bg-white text-[#3B2317] border border-[#E3DBD0] shadow-md'
                                : 'text-[#8C827A] hover:text-[#3B2317] hover:bg-[#EFE8DC]/70'
                            }`}
                          >
                            <span className={isActive ? 'text-[#BA5827]' : ''}>{cfg.icon}</span>
                            <span>{cfg.label}</span>
                          </button>
                        );
                      }
                    )}
                  </div>

                  {/* Lista de Atividades */}
                  <div className="space-y-2.5">
                    {isLoadingData ? (
                      <p className="text-sm text-[#8C827A] text-center py-6">Carregando...</p>
                    ) : displayActivities.length === 0 ? (
                      <p className="text-sm text-[#8C827A] text-center py-6">
                        Nenhuma atividade registrada.
                      </p>
                    ) : (
                      displayActivities.map((act) => (
                        <div
                          key={act.id}
                          className="group flex items-start gap-3.5 bg-[#F7F3ED] rounded-2xl border border-[#ECE5DA] p-3.5 hover:border-[#D6CCBD] hover:shadow-sm transition-all"
                        >
                          <div className="w-11 text-[11px] font-bold text-[#8C827A] pt-0.5 shrink-0 text-center leading-tight">
                            {formatDay(act.done_at || act.created_at)}
                          </div>
                          <div className="text-sm text-[#3B2317] leading-relaxed">
                            <span className="font-semibold text-[#BA5827]">
                              {activityLabels[act.activity_type] || 'Outro'}
                            </span>
                            <span className="text-[#8C827A]"> - </span>
                            {act.description}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Proposals */}
            <div className="bg-white rounded-3xl border border-[#E8E0D4] shadow-sm overflow-hidden">
              <button
                onClick={() => setIsProposalOpen(!isProposalOpen)}
                className="w-full flex items-center justify-between px-5 py-4 text-[#3B2317] font-bold text-base cursor-pointer hover:bg-[#F7F3ED] transition-colors"
              >
                <span className="flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-[#7A937D]" />
                  Propostas
                  <span className="px-2 py-0.5 bg-[#EFE8DC] rounded-full text-xs font-bold text-[#685A52]">
                    {proposals.length}
                  </span>
                </span>
                {isProposalOpen ? (
                  <ChevronUp className="w-5 h-5" />
                ) : (
                  <ChevronDown className="w-5 h-5" />
                )}
              </button>

              {isProposalOpen && (
                <div className="px-4 pb-4 space-y-2.5">
                  {proposals.length === 0 ? (
                    <p className="text-sm text-[#8C827A] text-center py-4">
                      Nenhuma proposta registrada.
                    </p>
                  ) : (
                    proposals.map((prop) => (
                      <div
                        key={prop.id}
                        className="flex items-center justify-between bg-[#F7F3ED] rounded-2xl border border-[#ECE5DA] p-4 hover:border-[#D6CCBD] hover:shadow-sm transition-all"
                      >
                        <div className="flex items-center gap-2">
                          <span
                            className={`w-2.5 h-2.5 rounded-full ${
                              prop.status === 'accepted'
                                ? 'bg-[#7A937D]'
                                : prop.status === 'rejected'
                                ? 'bg-[#C26B33]'
                                : 'bg-[#B8AFA0]'
                            }`}
                          />
                          <span className="text-sm font-semibold text-[#3B2317] capitalize">
                            {proposalStatusLabels[prop.status] || prop.status}
                          </span>
                        </div>
                        <span className="text-sm font-bold text-[#B75828]">
                          {formatCurrency(prop.value)}
                        </span>
                      </div>
                    ))
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
