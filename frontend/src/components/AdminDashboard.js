import React, { useState } from 'react';
import { 
  Users, 
  Target, 
  TrendingUp, 
  DollarSign, 
  Plus, 
  Upload,
  LogOut,
  Settings,
  BarChart3,
  ExternalLink
} from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';

const AdminDashboard = () => {
  const { user, logout } = useAuth();
  const [stats] = useState({
    total_clients: 3,
    active_campaigns: 5,
    total_budget: 250000,
    total_impressions: 45000000
  });
  const [clients] = useState([
    {
      client_id: 'client_001',
      name: 'TechCorp Brasil',
      company: 'TechCorp',
      contact_email: 'contato@techcorp.com.br',
      status: 'active'
    },
    {
      client_id: 'client_002', 
      name: 'EduSmart',
      company: 'EduSmart Ltda',
      contact_email: 'marketing@edusmart.com.br',
      status: 'active'
    }
  ]);
  const [campaigns] = useState([
    {
      campaign_id: 'camp_001',
      client_id: 'client_001',
      name: 'Campanha Black Friday 2024',
      objective: 'Conversões',
      budget: 50000,
      start_date: '2024-11-01',
      end_date: '2024-11-30',
      status: 'active'
    },
    {
      campaign_id: 'camp_002',
      client_id: 'client_002',
      name: 'Lançamento Curso Online',
      objective: 'Tráfego para o site',
      budget: 25000,
      start_date: '2024-12-01',
      end_date: '2024-12-31',
      status: 'active'
    }
  ]);
  const [loading] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  const handleLogout = () => {
    logout();
    toast.success('Logout realizado com sucesso');
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value || 0);
  };

  const formatNumber = (value) => {
    return new Intl.NumberFormat('pt-BR').format(value || 0);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'text-green-400';
      case 'paused': return 'text-yellow-400';
      case 'completed': return 'text-blue-400';
      default: return 'text-gray-400';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'active': return 'Ativa';
      case 'paused': return 'Pausada';
      case 'completed': return 'Concluída';
      default: return 'Inativa';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="loading-spinner"></div>
        <span className="ml-3">Carregando dashboard...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="container mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <span className="text-lg font-bold text-white">SM</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">South Media IA</h1>
                <p className="text-sm text-gray-300">Dashboard Administrativo</p>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm text-white font-medium">{user?.username || 'Admin'}</p>
                <p className="text-xs text-gray-300">Administrador</p>
              </div>
              <button
                onClick={handleLogout}
                className="btn btn-secondary"
              >
                <LogOut size={16} />
                Sair
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav className="bg-black/10 backdrop-blur-sm border-b border-white/5">
        <div className="container mx-auto px-6">
          <div className="flex space-x-8">
            {[
              { id: 'overview', label: 'Visão Geral', icon: BarChart3 },
              { id: 'clients', label: 'Clientes', icon: Users },
              { id: 'campaigns', label: 'Campanhas', icon: Target }
            ].map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? 'border-purple-400 text-white'
                      : 'border-transparent text-gray-300 hover:text-white'
                  }`}
                >
                  <Icon size={16} />
                  {tab.label}
                </button>
              );
            })}
          </div>
        </div>
      </nav>

      {/* Content */}
      <main className="container mx-auto px-6 py-8">
        {activeTab === 'overview' && (
          <div className="space-y-8">
            {/* Stats Cards */}
            <div className="grid grid-4 gap-6">
              <div className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-300">Total de Clientes</p>
                    <p className="text-2xl font-bold text-white">{stats.total_clients}</p>
                  </div>
                  <Users className="text-blue-400" size={24} />
                </div>
              </div>
              
              <div className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-300">Campanhas Ativas</p>
                    <p className="text-2xl font-bold text-white">{stats.active_campaigns}</p>
                  </div>
                  <Target className="text-green-400" size={24} />
                </div>
              </div>
              
              <div className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-300">Orçamento Total</p>
                    <p className="text-2xl font-bold text-white">{formatCurrency(stats.total_budget)}</p>
                  </div>
                  <DollarSign className="text-yellow-400" size={24} />
                </div>
              </div>
              
              <div className="card">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-300">Total de Impressões</p>
                    <p className="text-2xl font-bold text-white">{formatNumber(stats.total_impressions)}</p>
                  </div>
                  <TrendingUp className="text-purple-400" size={24} />
                </div>
              </div>
            </div>

            {/* Recent Activity */}
            <div className="card">
              <h2 className="text-xl font-semibold text-white mb-6">Atividade Recente</h2>
              <div className="space-y-4">
                {campaigns.slice(0, 5).map((campaign) => (
                  <div key={campaign.campaign_id} className="flex items-center justify-between p-4 bg-white/5 rounded-lg">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 bg-purple-500/20 rounded-lg flex items-center justify-center">
                        <Target size={16} className="text-purple-400" />
                      </div>
                      <div>
                        <p className="text-white font-medium">{campaign.name}</p>
                        <p className="text-sm text-gray-300">
                          {clients.find(c => c.client_id === campaign.client_id)?.name || 'Cliente não encontrado'}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className={`text-sm font-medium ${getStatusColor(campaign.status)}`}>
                        {getStatusText(campaign.status)}
                      </p>
                      <p className="text-sm text-gray-300">{formatCurrency(campaign.budget)}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'clients' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-white">Clientes</h2>
              <button className="btn btn-primary">
                <Plus size={16} />
                Novo Cliente
              </button>
            </div>

            <div className="grid gap-6">
              {clients.map((client) => (
                <div key={client.client_id} className="card">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-12 h-12 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
                        <span className="text-lg font-bold text-white">
                          {client.name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <h3 className="text-lg font-semibold text-white">{client.name}</h3>
                        <p className="text-sm text-gray-300">{client.company || 'Empresa não informada'}</p>
                        <p className="text-sm text-gray-400">{client.contact_email}</p>
                      </div>
                    </div>
                    
                    <div className="flex items-center gap-3">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                        client.status === 'active' 
                          ? 'bg-green-500/20 text-green-400' 
                          : 'bg-gray-500/20 text-gray-400'
                      }`}>
                        {client.status === 'active' ? 'Ativo' : 'Inativo'}
                      </span>
                      
                      <button className="btn btn-secondary">
                        <ExternalLink size={16} />
                        Ver Dashboard
                      </button>
                      
                      <button className="btn btn-secondary">
                        <Settings size={16} />
                        Editar
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'campaigns' && (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold text-white">Campanhas</h2>
              <div className="flex gap-3">
                <button className="btn btn-secondary">
                  <Upload size={16} />
                  Upload CSV
                </button>
                <button className="btn btn-primary">
                  <Plus size={16} />
                  Nova Campanha
                </button>
              </div>
            </div>

            <div className="grid gap-6">
              {campaigns.map((campaign) => {
                const client = clients.find(c => c.client_id === campaign.client_id);
                return (
                  <div key={campaign.campaign_id} className="card">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                          <Target size={20} className="text-white" />
                        </div>
                        <div>
                          <h3 className="text-lg font-semibold text-white">{campaign.name}</h3>
                          <p className="text-sm text-gray-300">{client?.name || 'Cliente não encontrado'}</p>
                          <p className="text-sm text-gray-400">{campaign.objective}</p>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-6">
                        <div className="text-right">
                          <p className="text-sm text-gray-300">Orçamento</p>
                          <p className="text-lg font-semibold text-white">{formatCurrency(campaign.budget)}</p>
                        </div>
                        
                        <div className="text-right">
                          <p className="text-sm text-gray-300">Período</p>
                          <p className="text-sm text-white">
                            {new Date(campaign.start_date).toLocaleDateString('pt-BR')} - {new Date(campaign.end_date).toLocaleDateString('pt-BR')}
                          </p>
                        </div>
                        
                        <div className="flex items-center gap-3">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                            campaign.status === 'active' 
                              ? 'bg-green-500/20 text-green-400' 
                              : campaign.status === 'paused'
                              ? 'bg-yellow-500/20 text-yellow-400'
                              : 'bg-gray-500/20 text-gray-400'
                          }`}>
                            {getStatusText(campaign.status)}
                          </span>
                          
                          <button className="btn btn-secondary">
                            <Settings size={16} />
                            Editar
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AdminDashboard;

