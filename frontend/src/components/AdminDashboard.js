import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, Users, BarChart3, Plus, Eye, Edit, Upload } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';

const AdminDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
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
      start_date: '2024-11-01',
      end_date: '2024-11-30',
      budget: 50000,
      status: 'active'
    },
    {
      campaign_id: 'camp_002',
      client_id: 'client_001',
      name: 'Campanha Natal 2024',
      start_date: '2024-12-01',
      end_date: '2024-12-25',
      budget: 75000,
      status: 'active'
    },
    {
      campaign_id: 'camp_003',
      client_id: 'client_002',
      name: 'Volta às Aulas 2025',
      start_date: '2025-01-15',
      end_date: '2025-02-28',
      budget: 30000,
      status: 'planning'
    }
  ]);

  const [activeTab, setActiveTab] = useState('clients');
  const [showClientModal, setShowClientModal] = useState(false);
  const [showCampaignModal, setShowCampaignModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [editingClient, setEditingClient] = useState(null);
  const [editingCampaign, setEditingCampaign] = useState(null);

  const handleLogout = () => {
    logout();
    toast.success('Logout realizado com sucesso');
  };

  // Client handlers
  const handleNewClient = () => {
    setEditingClient(null);
    setShowClientModal(true);
  };

  const handleEditClient = (client) => {
    setEditingClient(client);
    setShowClientModal(true);
  };

  const handleViewDashboard = (client) => {
    // Navegar para o dashboard do cliente
    navigate('/dashboard', { 
      state: { 
        clientId: client.client_id, 
        clientName: client.name 
      } 
    });
    toast.success(`Abrindo dashboard de ${client.name}`);
  };

  // Campaign handlers
  const handleNewCampaign = () => {
    setEditingCampaign(null);
    setShowCampaignModal(true);
  };

  const handleEditCampaign = (campaign) => {
    setEditingCampaign(campaign);
    setShowCampaignModal(true);
  };

  const handleUploadCSV = () => {
    setShowUploadModal(true);
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="bg-slate-800/50 backdrop-blur-sm border-b border-purple-500/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">SM</span>
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white">South Media IA</h1>
                <p className="text-gray-300 text-sm">Dashboard Administrativo</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-white font-medium">{user?.username}</p>
                <p className="text-gray-300 text-sm">Administrador</p>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors"
              >
                <LogOut className="w-4 h-4" />
                <span>Sair</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">Total de Clientes</p>
                <p className="text-3xl font-bold text-white">{stats.total_clients}</p>
              </div>
              <Users className="w-8 h-8 text-purple-400" />
            </div>
          </div>
          
          <div className="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">Campanhas Ativas</p>
                <p className="text-3xl font-bold text-white">{stats.active_campaigns}</p>
              </div>
              <BarChart3 className="w-8 h-8 text-green-400" />
            </div>
          </div>
          
          <div className="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">Orçamento Total</p>
                <p className="text-3xl font-bold text-white">{formatCurrency(stats.total_budget)}</p>
              </div>
              <div className="text-2xl">💰</div>
            </div>
          </div>
          
          <div className="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-300 text-sm">Total Impressões</p>
                <p className="text-3xl font-bold text-white">{formatNumber(stats.total_impressions)}</p>
              </div>
              <div className="text-2xl">👁️</div>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="mb-8">
          <div className="flex space-x-1 bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-lg p-1">
            <button
              onClick={() => setActiveTab('clients')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
                activeTab === 'clients'
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-300 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              <Users className="w-4 h-4" />
              <span>Clientes</span>
            </button>
            <button
              onClick={() => setActiveTab('campaigns')}
              className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
                activeTab === 'campaigns'
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-300 hover:text-white hover:bg-slate-700/50'
              }`}
            >
              <BarChart3 className="w-4 h-4" />
              <span>Campanhas</span>
            </button>
          </div>
        </div>

        {/* Content */}
        {activeTab === 'clients' && (
          <div className="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-white">Clientes</h2>
              <button
                onClick={handleNewClient}
                className="flex items-center space-x-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
              >
                <Plus className="w-4 h-4" />
                <span>Novo Cliente</span>
              </button>
            </div>
            
            <div className="space-y-4">
              {clients.map((client) => (
                <div key={client.client_id} className="bg-slate-700/50 border border-purple-500/10 rounded-lg p-4">
                  <div className="flex justify-between items-start">
                    <div>
                      <h3 className="text-lg font-semibold text-white">{client.name}</h3>
                      <p className="text-gray-300">{client.company}</p>
                      <p className="text-gray-400 text-sm">{client.contact_email}</p>
                      <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium mt-2 ${
                        client.status === 'active' 
                          ? 'bg-green-500/20 text-green-400' 
                          : 'bg-gray-500/20 text-gray-400'
                      }`}>
                        {client.status === 'active' ? 'Ativo' : 'Inativo'}
                      </span>
                    </div>
                    
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleViewDashboard(client)}
                        className="flex items-center space-x-1 px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-sm transition-colors"
                      >
                        <Eye className="w-4 h-4" />
                        <span>Ver Dashboard</span>
                      </button>
                      <button
                        onClick={() => handleEditClient(client)}
                        className="flex items-center space-x-1 px-3 py-1 bg-gray-600 hover:bg-gray-700 text-white rounded text-sm transition-colors"
                      >
                        <Edit className="w-4 h-4" />
                        <span>Editar</span>
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'campaigns' && (
          <div className="bg-slate-800/50 backdrop-blur-sm border border-purple-500/20 rounded-xl p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-white">Campanhas</h2>
              <div className="flex space-x-2">
                <button
                  onClick={handleUploadCSV}
                  className="flex items-center space-x-2 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
                >
                  <Upload className="w-4 h-4" />
                  <span>Upload CSV</span>
                </button>
                <button
                  onClick={handleNewCampaign}
                  className="flex items-center space-x-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
                >
                  <Plus className="w-4 h-4" />
                  <span>Nova Campanha</span>
                </button>
              </div>
            </div>
            
            <div className="space-y-4">
              {campaigns.map((campaign) => {
                const client = clients.find(c => c.client_id === campaign.client_id);
                return (
                  <div key={campaign.campaign_id} className="bg-slate-700/50 border border-purple-500/10 rounded-lg p-4">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="text-lg font-semibold text-white">{campaign.name}</h3>
                        <p className="text-gray-300">{client?.name}</p>
                        <p className="text-gray-400 text-sm">
                          {new Date(campaign.start_date).toLocaleDateString('pt-BR')} - {new Date(campaign.end_date).toLocaleDateString('pt-BR')}
                        </p>
                        <p className="text-gray-400 text-sm">Orçamento: {formatCurrency(campaign.budget)}</p>
                        <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium mt-2 ${
                          campaign.status === 'active' 
                            ? 'bg-green-500/20 text-green-400' 
                            : campaign.status === 'planning'
                            ? 'bg-yellow-500/20 text-yellow-400'
                            : 'bg-gray-500/20 text-gray-400'
                        }`}>
                          {campaign.status === 'active' ? 'Ativa' : campaign.status === 'planning' ? 'Planejamento' : 'Inativa'}
                        </span>
                      </div>
                      
                      <div className="flex space-x-2">
                        <button
                          onClick={() => handleEditCampaign(campaign)}
                          className="flex items-center space-x-1 px-3 py-1 bg-gray-600 hover:bg-gray-700 text-white rounded text-sm transition-colors"
                        >
                          <Edit className="w-4 h-4" />
                          <span>Editar</span>
                        </button>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </main>

      {/* Modals */}
      {showClientModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-slate-800 border border-purple-500/20 rounded-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-bold text-white mb-4">
              {editingClient ? 'Editar Cliente' : 'Novo Cliente'}
            </h3>
            <div className="space-y-4">
              <input
                type="text"
                placeholder="Nome do cliente"
                className="w-full px-3 py-2 bg-slate-700 border border-purple-500/20 rounded-lg text-white placeholder-gray-400"
                defaultValue={editingClient?.name || ''}
              />
              <input
                type="text"
                placeholder="Empresa"
                className="w-full px-3 py-2 bg-slate-700 border border-purple-500/20 rounded-lg text-white placeholder-gray-400"
                defaultValue={editingClient?.company || ''}
              />
              <input
                type="email"
                placeholder="Email de contato"
                className="w-full px-3 py-2 bg-slate-700 border border-purple-500/20 rounded-lg text-white placeholder-gray-400"
                defaultValue={editingClient?.contact_email || ''}
              />
            </div>
            <div className="flex justify-end space-x-2 mt-6">
              <button
                onClick={() => setShowClientModal(false)}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={() => {
                  toast.success(editingClient ? 'Cliente atualizado!' : 'Cliente criado!');
                  setShowClientModal(false);
                }}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
              >
                {editingClient ? 'Atualizar' : 'Criar'}
              </button>
            </div>
          </div>
        </div>
      )}

      {showCampaignModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-slate-800 border border-purple-500/20 rounded-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-bold text-white mb-4">
              {editingCampaign ? 'Editar Campanha' : 'Nova Campanha'}
            </h3>
            <div className="space-y-4">
              <input
                type="text"
                placeholder="Nome da campanha"
                className="w-full px-3 py-2 bg-slate-700 border border-purple-500/20 rounded-lg text-white placeholder-gray-400"
                defaultValue={editingCampaign?.name || ''}
              />
              <select className="w-full px-3 py-2 bg-slate-700 border border-purple-500/20 rounded-lg text-white">
                <option value="">Selecionar cliente</option>
                {clients.map(client => (
                  <option key={client.client_id} value={client.client_id}>
                    {client.name}
                  </option>
                ))}
              </select>
              <input
                type="date"
                placeholder="Data de início"
                className="w-full px-3 py-2 bg-slate-700 border border-purple-500/20 rounded-lg text-white"
                defaultValue={editingCampaign?.start_date || ''}
              />
              <input
                type="date"
                placeholder="Data de fim"
                className="w-full px-3 py-2 bg-slate-700 border border-purple-500/20 rounded-lg text-white"
                defaultValue={editingCampaign?.end_date || ''}
              />
              <input
                type="number"
                placeholder="Orçamento"
                className="w-full px-3 py-2 bg-slate-700 border border-purple-500/20 rounded-lg text-white placeholder-gray-400"
                defaultValue={editingCampaign?.budget || ''}
              />
            </div>
            <div className="flex justify-end space-x-2 mt-6">
              <button
                onClick={() => setShowCampaignModal(false)}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={() => {
                  toast.success(editingCampaign ? 'Campanha atualizada!' : 'Campanha criada!');
                  setShowCampaignModal(false);
                }}
                className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
              >
                {editingCampaign ? 'Atualizar' : 'Criar'}
              </button>
            </div>
          </div>
        </div>
      )}

      {showUploadModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-slate-800 border border-purple-500/20 rounded-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-bold text-white mb-4">Upload CSV</h3>
            <div className="space-y-4">
              <div className="border-2 border-dashed border-purple-500/20 rounded-lg p-8 text-center">
                <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                <p className="text-gray-300 mb-2">Arraste o arquivo CSV aqui</p>
                <p className="text-gray-400 text-sm">ou clique para selecionar</p>
                <input type="file" accept=".csv" className="hidden" />
              </div>
            </div>
            <div className="flex justify-end space-x-2 mt-6">
              <button
                onClick={() => setShowUploadModal(false)}
                className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={() => {
                  toast.success('Arquivo CSV processado com sucesso!');
                  setShowUploadModal(false);
                }}
                className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg transition-colors"
              >
                Upload
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;

