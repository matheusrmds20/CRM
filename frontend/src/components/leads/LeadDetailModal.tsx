import React, { useEffect, useState, useCallback, useRef } from 'react';
import { X, Phone, Calendar, Mail, MessageCircle, ChevronUp, ChevronDown, User, IndianRupee, Plus, FileText, Clock, Send, Pencil, Trash2 } from 'lucide-react';
import { type LeadItem, type LeadStatus } from '../../schemas/lead.schema';
import {
  activitiesService,
  type ActivityApiResponse,
  type ActivityTypeApi,
} from '../../services/activities.service';
import { proposalsService, type ProposalApiResponse, type ProposalStatusApi } from '../../services/proposals.service';
import { leadsService, type LeadUpdatePayload } from '../../services/leads.service';

interface LeadDetailModalProps {
  lead: LeadItem | null;
  isOpen: boolean;
  onClose: () => void;
  onSaved?: (updated: LeadItem) => void;
  onDeleted?: (id: string) => void;
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
  onDeleted,
}) => {
  const [activities, setActivities] = useState<ActivityApiResponse[]>([]);
  const [proposals, setProposals] = useState<ProposalApiResponse[]>([]);
  const [isActivityOpen, setIsActivityOpen] = useState(true);
  const [isProposalOpen, setIsProposalOpen] = useState(true);
  const [activeTab, setActiveTab] = useState<ActivityTypeApi>('call');
  const [isLoadingData, setIsLoadingData] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [sideForm, setSideForm] = useState<'activity' | 'proposal' | null>(null);
  const [activityType, setActivityType] = useState<ActivityTypeApi>('call');
  const [activityDescription, setActivityDescription] = useState('');
  const [activityDoneAt, setActivityDoneAt] = useState('');
  const [proposalStatus, setProposalStatus] = useState<ProposalStatusApi>('pending');
  const [proposalValue, setProposalValue] = useState('');
  const [proposalSentAt, setProposalSentAt] = useState('');
  const [isSavingSideForm, setIsSavingSideForm] = useState(false);
  const [editingActivityId, setEditingActivityId] = useState<number | null>(null);
  const [editingProposalId, setEditingProposalId] = useState<number | null>(null);
  const [isDeletingLead, setIsDeletingLead] = useState(false);
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
    setSideForm(null);
    setActivityType('call');
    setActivityDescription('');
    setActivityDoneAt('');
    setProposalStatus('pending');
    setProposalValue('');
    setProposalSentAt('');
    setEditingActivityId(null);
    setEditingProposalId(null);

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

  const toIsoDate = (value: string) => (value ? new Date(value).toISOString() : null);
  const toLocalDateTime = (value: string | null) => (value ? new Date(value).toISOString().slice(0, 16) : '');

  const handleCreateActivity = async () => {
    if (leadId === null || activityDescription.trim().length < 3) return;
    setIsSavingSideForm(true);
    try {
      const payload = { activity_type: activityType, description: activityDescription.trim(), done_at: toIsoDate(activityDoneAt) };
      if (editingActivityId !== null) {
        const updated = await activitiesService.update(editingActivityId, payload);
        setActivities((current) => current.map((item) => item.id === updated.id ? updated : item));
      } else {
        const created = await activitiesService.create({ lead_id: leadId, ...payload });
        setActivities((current) => [created, ...current]);
      }
      setActivityDescription('');
      setActivityDoneAt('');
      setEditingActivityId(null);
      setSideForm(null);
    } catch (err) {
      console.error('Erro ao criar atividade:', err);
    } finally {
      setIsSavingSideForm(false);
    }
  };

  const handleCreateProposal = async () => {
    const value = Number(proposalValue);
    if (leadId === null || !proposalValue || Number.isNaN(value) || value < 0) return;
    setIsSavingSideForm(true);
    try {
      const payload = { status: proposalStatus, value, sent_at: toIsoDate(proposalSentAt) };
      if (editingProposalId !== null) {
        const updated = await proposalsService.update(editingProposalId, payload);
        setProposals((current) => current.map((item) => item.id === updated.id ? updated : item));
      } else {
        const created = await proposalsService.create({ lead_id: leadId, ...payload });
        setProposals((current) => [created, ...current]);
      }
      setProposalValue('');
      setProposalSentAt('');
      setEditingProposalId(null);
      setSideForm(null);
    } catch (err) {
      console.error('Erro ao criar proposta:', err);
    } finally {
      setIsSavingSideForm(false);
    }
  };

  const openActivityEdit = (activity: ActivityApiResponse) => {
    setEditingProposalId(null);
    setEditingActivityId(activity.id);
    setActivityType(activity.activity_type);
    setActivityDescription(activity.description);
    setActivityDoneAt(toLocalDateTime(activity.done_at));
    setSideForm('activity');
  };

  const openProposalEdit = (proposal: ProposalApiResponse) => {
    setEditingActivityId(null);
    setEditingProposalId(proposal.id);
    setProposalStatus(proposal.status);
    setProposalValue(String(proposal.value));
    setProposalSentAt(toLocalDateTime(proposal.sent_at));
    setSideForm('proposal');
  };

  const handleDeleteActivity = async (id: number) => {
    if (!window.confirm('Excluir esta atividade?')) return;
    try {
      await activitiesService.delete(id);
      setActivities((current) => current.filter((activity) => activity.id !== id));
    } catch (err) { console.error('Erro ao excluir atividade:', err); }
  };

  const handleDeleteProposal = async (id: number) => {
    if (!window.confirm('Excluir esta proposta?')) return;
    try {
      await proposalsService.delete(id);
      setProposals((current) => current.filter((proposal) => proposal.id !== id));
    } catch (err) { console.error('Erro ao excluir proposta:', err); }
  };

  const handleDeleteLead = async () => {
    if (leadId === null || !lead) return;
    if (!window.confirm(`Excluir o lead ${lead.name}? Esta ação não pode ser desfeita.`)) return;
    setIsDeletingLead(true);
    try {
      await leadsService.delete(leadId);
      onDeleted?.(lead.id);
      closeModal();
    } catch (err) { console.error('Erro ao excluir lead:', err); }
    finally { setIsDeletingLead(false); }
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
          <div className="flex items-center gap-3">
            <button onClick={handleDeleteLead} disabled={isDeletingLead} className="flex items-center gap-2 rounded-xl border border-[#87533C] px-4 py-2 text-sm font-semibold text-[#683720] transition-colors hover:bg-[#FFF8F3] disabled:opacity-50 cursor-pointer">
              <Trash2 className="w-4 h-4" /> {isDeletingLead ? 'Excluindo...' : 'Excluir lead'}
            </button>
            <button onClick={closeModal} className="p-2 text-[#7D7068] hover:text-[#3B2317] hover:bg-white hover:shadow-sm rounded-full transition-all cursor-pointer"><X className="w-6 h-6" /></button>
          </div>
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
            {/* Ações laterais */}
            <div className="bg-[#EDE1CA] border border-[#D8C6A9] rounded-3xl p-3 shadow-[0_12px_25px_-16px_rgba(59,35,23,0.7)]">
              <div className="grid grid-cols-2 gap-2">
                <button onClick={() => { setEditingActivityId(null); setActivityDescription(''); setActivityDoneAt(''); setSideForm(sideForm === 'activity' ? null : 'activity'); }} className={`flex flex-col items-center gap-1.5 rounded-2xl px-3 py-3 text-sm font-semibold transition-all cursor-pointer ${sideForm === 'activity' ? 'bg-[#BA5827] text-white shadow-md' : 'bg-[#FFFDF9] text-[#5A4B42] hover:bg-white'}`}>
                  <Plus className="w-5 h-5" /> Nova atividade
                </button>
                <button onClick={() => { setEditingProposalId(null); setProposalValue(''); setProposalSentAt(''); setSideForm(sideForm === 'proposal' ? null : 'proposal'); }} className={`flex flex-col items-center gap-1.5 rounded-2xl px-3 py-3 text-sm font-semibold transition-all cursor-pointer ${sideForm === 'proposal' ? 'bg-[#7A937D] text-white shadow-md' : 'bg-[#FFFDF9] text-[#5A4B42] hover:bg-white'}`}>
                  <FileText className="w-5 h-5" /> Nova proposta
                </button>
              </div>

              {sideForm === 'activity' && (
                <div className="mt-3 rounded-2xl bg-[#FFFDF9] p-4 space-y-3 animate-modal-enter">
                  <h4 className="text-base font-bold text-[#3B2317]">{editingActivityId ? 'Editar atividade' : 'Nova atividade'}</h4>
                  <select value={activityType} onChange={(e) => setActivityType(e.target.value as ActivityTypeApi)} className="w-full rounded-xl border border-[#CFC1AE] bg-white px-3 py-2.5 text-sm text-[#3B2317] focus:outline-none focus:ring-2 focus:ring-[#7A937D]/30">
                    {Object.entries(activityLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                  </select>
                  <textarea value={activityDescription} onChange={(e) => setActivityDescription(e.target.value)} rows={3} placeholder="Descrição da atividade" className="w-full resize-none rounded-xl border border-[#CFC1AE] bg-white px-3 py-2.5 text-sm text-[#3B2317] placeholder-[#A89C90] focus:outline-none focus:ring-2 focus:ring-[#7A937D]/30" />
                  <label className="block text-xs font-semibold text-[#685A52]">Realizada em
                    <span className="relative mt-1 block"><Clock className="absolute left-3 top-1/2 w-4 h-4 -translate-y-1/2 text-[#8C827A]" /><input type="datetime-local" value={activityDoneAt} onChange={(e) => setActivityDoneAt(e.target.value)} className="w-full rounded-xl border border-[#CFC1AE] bg-white py-2.5 pl-9 pr-2 text-sm text-[#3B2317] focus:outline-none" /></span>
                  </label>
                  <button onClick={handleCreateActivity} disabled={isSavingSideForm || activityDescription.trim().length < 3} className="w-full rounded-xl bg-[#BA5827] py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#A94C20] disabled:cursor-not-allowed disabled:opacity-50">{isSavingSideForm ? 'Salvando...' : editingActivityId ? 'Atualizar atividade' : 'Salvar atividade'}</button>
                </div>
              )}

              {sideForm === 'proposal' && (
                <div className="mt-3 rounded-2xl bg-[#FFFDF9] p-4 space-y-3 animate-modal-enter">
                  <h4 className="text-base font-bold text-[#3B2317]">{editingProposalId ? 'Editar proposta' : 'Nova proposta'}</h4>
                  <label className="block text-xs font-semibold text-[#685A52]">Valor
                    <input type="number" min="0" step="0.01" value={proposalValue} onChange={(e) => setProposalValue(e.target.value)} placeholder="0,00" className="mt-1 w-full rounded-xl border border-[#CFC1AE] bg-white px-3 py-2.5 text-sm text-[#3B2317] focus:outline-none focus:ring-2 focus:ring-[#7A937D]/30" />
                  </label>
                  <label className="block text-xs font-semibold text-[#685A52]">Status
                    <select value={proposalStatus} onChange={(e) => setProposalStatus(e.target.value as ProposalStatusApi)} className="mt-1 w-full rounded-xl border border-[#CFC1AE] bg-white px-3 py-2.5 text-sm text-[#3B2317] focus:outline-none focus:ring-2 focus:ring-[#7A937D]/30"><option value="pending">Pendente</option><option value="accepted">Aceita</option><option value="rejected">Recusada</option></select>
                  </label>
                  <label className="block text-xs font-semibold text-[#685A52]">Enviada em
                    <span className="relative mt-1 block"><Send className="absolute left-3 top-1/2 w-4 h-4 -translate-y-1/2 text-[#8C827A]" /><input type="datetime-local" value={proposalSentAt} onChange={(e) => setProposalSentAt(e.target.value)} className="w-full rounded-xl border border-[#CFC1AE] bg-white py-2.5 pl-9 pr-2 text-sm text-[#3B2317] focus:outline-none" /></span>
                  </label>
                  <button onClick={handleCreateProposal} disabled={isSavingSideForm || !proposalValue} className="w-full rounded-xl bg-[#7A937D] py-2.5 text-sm font-semibold text-white transition-colors hover:bg-[#66806A] disabled:cursor-not-allowed disabled:opacity-50">{isSavingSideForm ? 'Salvando...' : editingProposalId ? 'Atualizar proposta' : 'Salvar proposta'}</button>
                </div>
              )}
            </div>

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
                          <div className="min-w-0 flex-1 text-sm text-[#3B2317] leading-relaxed">
                            <span className="font-semibold text-[#BA5827]">
                              {activityLabels[act.activity_type] || 'Outro'}
                            </span>
                            <span className="text-[#8C827A]"> - </span>
                            {act.description}
                          </div>
                          <div className="flex gap-1 text-[#835033]">
                            <button onClick={() => openActivityEdit(act)} aria-label="Editar atividade" className="rounded-lg p-1.5 hover:bg-white cursor-pointer"><Pencil className="w-4 h-4" /></button>
                            <button onClick={() => handleDeleteActivity(act.id)} aria-label="Excluir atividade" className="rounded-lg p-1.5 hover:bg-white text-[#A64F2A] cursor-pointer"><Trash2 className="w-4 h-4" /></button>
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
                        <div className="flex items-center gap-1">
                          <span className="text-sm font-bold text-[#B75828]">{formatCurrency(prop.value)}</span>
                          <button onClick={() => openProposalEdit(prop)} aria-label="Editar proposta" className="rounded-lg p-1.5 text-[#835033] hover:bg-white cursor-pointer"><Pencil className="w-4 h-4" /></button>
                          <button onClick={() => handleDeleteProposal(prop.id)} aria-label="Excluir proposta" className="rounded-lg p-1.5 text-[#A64F2A] hover:bg-white cursor-pointer"><Trash2 className="w-4 h-4" /></button>
                        </div>
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
