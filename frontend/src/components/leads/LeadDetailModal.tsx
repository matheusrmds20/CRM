import React, { useEffect, useState, useCallback } from 'react';
import { X, Phone, Calendar, Mail, MessageCircle, ChevronUp, ChevronDown } from 'lucide-react';
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
  call: 'Call',
  meeting: 'Meeting',
  email: 'Email',
  whatsapp: 'WhatsApp',
  other: 'Outro',
};

const activityStatusMap: Record<ActivityTypeApi, { label: string; icon: React.ReactNode }> = {
  call: {
    label: 'Call',
    icon: <Phone className="w-4 h-4 text-[#5A4B42]" />,
  },
  meeting: {
    label: 'Meeting',
    icon: <Calendar className="w-4 h-4 text-[#5A4B42]" />,
  },
  email: {
    label: 'Email',
    icon: <Mail className="w-4 h-4 text-[#5A4B42]" />,
  },
  whatsapp: {
    label: 'WhatsApp',
    icon: <MessageCircle className="w-4 h-4 text-[#5A4B42]" />,
  },
  other: {
    label: 'Outro',
    icon: <Phone className="w-4 h-4 text-[#5A4B42]" />,
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

// Traduz o dia para abreviação em pt-BR
function formatDay(dateStr: string): string {
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
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
    onClose();
  }, [lead, onClose]);

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
          phone: updated.phone,
          subject: updated.subject,
          description: updated.description,
          estimatedValue: updated.estimated_value,
          status: apiToStatus[updated.status] || lead.status,
        });
      }
      onClose();
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
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-xs">
      <div className="relative w-full max-w-4xl bg-[#FAF6F0] rounded-3xl border-[2px] border-[#1F1E1C] shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-200 flex flex-col max-h-[92vh]">
        {/* Header do Modal */}
        <div className="flex items-center justify-between px-7 py-5 border-b border-[#E3DBD0] bg-[#EFE8DC]/60">
          <div className="flex items-center gap-4">
            <img
              src={lead.avatar}
              alt={lead.name}
              className="w-12 h-12 rounded-full object-cover border-2 border-white shadow-sm"
            />
            <h3 className="text-xl font-bold text-[#3B2317] tracking-tight">
              Lead Detail: {lead.name}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 text-[#7D7068] hover:text-[#3B2317] hover:bg-black/5 rounded-full transition-colors cursor-pointer"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Corpo do Modal */}
        <div className="flex flex-col md:flex-row gap-6 p-7 overflow-y-auto">
          {/* Coluna Esquerda - Formulário */}
          <div className="flex-1 space-y-3.5 min-w-0">
            {/* Nome */}
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Nome do lead"
              className="w-full px-4 py-2.5 bg-[#EFE8DC] border border-[#DFD6C7] rounded-xl text-sm text-[#3B2317] focus:outline-none focus:ring-2 focus:ring-[#7A937D]/30"
            />

            {/* Status (dropdown) */}
            <div className="relative">
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value as LeadStatus)}
                className="w-full px-4 py-2.5 bg-[#EFE8DC] border border-[#DFD6C7] rounded-xl text-sm text-[#3B2317] focus:outline-none focus:ring-2 focus:ring-[#7A937D]/30 appearance-none cursor-pointer"
              >
                {allStatuses.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
              <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[#5A4B42] pointer-events-none" />
            </div>

            {/* Email */}
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="email@exemplo.com"
              className="w-full px-4 py-2.5 bg-[#EFE8DC] border border-[#DFD6C7] rounded-xl text-sm text-[#3B2317] focus:outline-none focus:ring-2 focus:ring-[#7A937D]/30"
            />

            {/* Telefone */}
            <input
              type="text"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+55 11 98765-4321"
              className="w-full px-4 py-2.5 bg-[#EFE8DC] border border-[#DFD6C7] rounded-xl text-sm text-[#3B2317] focus:outline-none focus:ring-2 focus:ring-[#7A937D]/30"
            />

            {/* Assunto */}
            <input
              type="text"
              value={subject}
              onChange={(e) => setSubject(e.target.value)}
              placeholder="Assunto"
              className="w-full px-4 py-2.5 bg-[#EFE8DC] border border-[#DFD6C7] rounded-xl text-sm text-[#3B2317] focus:outline-none focus:ring-2 focus:ring-[#7A937D]/30"
            />

            {/* Descrição */}
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Descrição"
              rows={5}
              className="w-full px-4 py-2.5 bg-[#EFE8DC] border border-[#DFD6C7] rounded-xl text-sm text-[#3B2317] focus:outline-none focus:ring-2 focus:ring-[#7A937D]/30 resize-none"
            />

            {/* Valor Estimado */}
            <input
              type="number"
              value={estimatedValue}
              onChange={(e) => setEstimatedValue(e.target.value)}
              placeholder="R$ 15.000"
              className="w-full px-4 py-2.5 bg-[#EFE8DC] border border-[#DFD6C7] rounded-xl text-sm text-[#3B2317] focus:outline-none focus:ring-2 focus:ring-[#7A937D]/30"
            />

            {/* Botões de Ação */}
            <div className="flex items-center gap-3 pt-3">
              <button
                onClick={handleSave}
                disabled={isSaving}
                className="flex-1 px-5 py-2.5 bg-[#B75828] hover:bg-[#A14A1E] text-white text-sm font-semibold rounded-xl shadow-md transition-all cursor-pointer disabled:opacity-50"
              >
                {isSaving ? 'Salvando...' : 'Save'}
              </button>
              <button
                onClick={handleDiscard}
                className="flex-1 px-5 py-2.5 bg-[#B0A79C] hover:bg-[#9C9388] text-white text-sm font-semibold rounded-xl shadow-md transition-all cursor-pointer"
              >
                Discard
              </button>
            </div>
          </div>

          {/* Coluna Direita - Activity History */}
          <div className="w-full md:w-80 shrink-0 space-y-4">
            {/* Activity History */}
            <div className="bg-[#EFE8DC] rounded-2xl border border-[#DFD6C7] overflow-hidden">
              <button
                onClick={() => setIsActivityOpen(!isActivityOpen)}
                className="w-full flex items-center justify-between px-4 py-3 bg-[#EFE8DC] text-[#3B2317] font-bold text-sm cursor-pointer"
              >
                <span>Activity History</span>
                {isActivityOpen ? (
                  <ChevronUp className="w-4 h-4" />
                ) : (
                  <ChevronDown className="w-4 h-4" />
                )}
              </button>

              {isActivityOpen && (
                <div className="px-3 pb-3 space-y-3">
                  {/* Tabs */}
                  <div className="flex items-center justify-between gap-1 bg-[#F4F1EA] rounded-2xl p-1.5">
                    {(['call', 'meeting', 'email', 'whatsapp'] as ActivityTypeApi[]).map(
                      (tab) => {
                        const cfg = activityStatusMap[tab];
                        const isActive = activeTab === tab;
                        return (
                          <button
                            key={tab}
                            onClick={() => setActiveTab(tab)}
                            className={`flex flex-col items-center gap-1 px-2 py-1.5 rounded-xl text-[10px] font-semibold transition-all cursor-pointer ${
                              isActive
                                ? 'bg-[#EFE8DC] border border-[#DFD6C7] text-[#3B2317]'
                                : 'text-[#8C827A] hover:text-[#3B2317] hover:bg-[#EFE8DC]/50'
                            }`}
                          >
                            {cfg.icon}
                            <span>{cfg.label}</span>
                          </button>
                        );
                      }
                    )}
                  </div>

                  {/* Lista de Atividades */}
                  <div className="space-y-2">
                    {isLoadingData ? (
                      <p className="text-xs text-[#8C827A] text-center py-4">Carregando...</p>
                    ) : displayActivities.length === 0 ? (
                      <p className="text-xs text-[#8C827A] text-center py-4">
                        Nenhuma atividade registrada.
                      </p>
                    ) : (
                      displayActivities.map((act) => (
                        <div
                          key={act.id}
                          className="flex items-start gap-3 bg-[#F4F1EA] rounded-xl border border-[#E3DBD0] p-2.5"
                        >
                          <div className="w-9 text-[10px] font-bold text-[#8C827A] pt-0.5 shrink-0">
                            {formatDay(act.done_at || act.created_at)}
                          </div>
                          <div className="text-xs text-[#3B2317] leading-relaxed">
                            {activityLabels[act.activity_type] || 'Outro'} - {act.description}
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>
              )}
            </div>

            {/* Proposals */}
            <div className="bg-[#EFE8DC] rounded-2xl border border-[#DFD6C7] overflow-hidden">
              <button
                onClick={() => setIsProposalOpen(!isProposalOpen)}
                className="w-full flex items-center justify-between px-4 py-3 bg-[#EFE8DC] text-[#3B2317] font-bold text-sm cursor-pointer"
              >
                <span>Proposals ({proposals.length})</span>
                {isProposalOpen ? (
                  <ChevronUp className="w-4 h-4" />
                ) : (
                  <ChevronDown className="w-4 h-4" />
                )}
              </button>

              {isProposalOpen && (
                <div className="px-3 pb-3 space-y-2">
                  {proposals.length === 0 ? (
                    <p className="text-xs text-[#8C827A] text-center py-3">
                      Nenhuma proposta registrada.
                    </p>
                  ) : (
                    proposals.map((prop) => (
                      <div
                        key={prop.id}
                        className="flex items-center justify-between bg-[#F4F1EA] rounded-xl border border-[#E3DBD0] p-3"
                      >
                        <span className="text-xs font-semibold text-[#3B2317] capitalize">
                          {prop.status}
                        </span>
                        <span className="text-xs font-bold text-[#B75828]">
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
