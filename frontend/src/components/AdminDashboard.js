import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, Users, BarChart3, Plus, Eye, Edit, Upload } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';

const AdminDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  const [activeTab, setActiveTab] = useState('clients');
  const [showClientModal, setShowClientModal] = useState(false);
  const [showCampaignModal, setShowCampaignModal] = useState(false);
  const [showUploadModal, setShowUploadModal] = useState(false);
  
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
    }
  ]);

  const handleLogout = () => {
    logout();
    toast.success('Logout realizado com sucesso!');
    navigate('/admin/login');
  };

  const handleViewDashboard = (client) => {
    toast.success(`Abrindo dashboard de ${client.name}`);
    navigate('/dashboard', { state: { clientId: client.client_id, clientName: client.name } });
  };

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  const formatNumber = (value) => {
    return new Intl.NumberFormat('pt-BR').format(value);
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0F0F23 0%, #16213E 100%)',
      color: '#FFFFFF',
      fontFamily: 'Inter, sans-serif'
    }}>
      {/* Header */}
      <div style={{
        background: '#1A1A2E',
        border: '1px solid rgba(139, 92, 246, 0.2)',
        borderRadius: '0 0 12px 12px',
        padding: '1.5rem 2rem'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{
              width: '48px',
              height: '48px',
              background: 'linear-gradient(135deg, #8B5CF6 0%, #F97316 100%)',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              <span style={{ color: 'white', fontWeight: 'bold', fontSize: '1.25rem' }}>SM</span>
            </div>
            <div>
              <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'white', margin: 0 }}>
                South Media IA
              </h1>
              <p style={{ color: '#A1A1AA', margin: 0, fontSize: '0.875rem' }}>Dashboard Administrativo</p>
            </div>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{ textAlign: 'right' }}>
              <p style={{ color: 'white', fontWeight: '500', margin: 0 }}>{user?.username}</p>
              <p style={{ color: '#A1A1AA', fontSize: '0.875rem', margin: 0 }}>Administrador</p>
            </div>
            <button
              onClick={handleLogout}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '0.5rem',
                padding: '0.5rem 1rem',
                background: 'rgba(239, 68, 68, 0.1)',
                border: '1px solid rgba(239, 68, 68, 0.3)',
                borderRadius: '8px',
                color: '#EF4444',
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.target.style.background = 'rgba(239, 68, 68, 0.2)';
                e.target.style.borderColor = 'rgba(239, 68, 68, 0.5)';
              }}
              onMouseLeave={(e) => {
                e.target.style.background = 'rgba(239, 68, 68, 0.1)';
                e.target.style.borderColor = 'rgba(239, 68, 68, 0.3)';
              }}
            >
              <LogOut style={{ width: '16px', height: '16px' }} />
              Sair
            </button>
          </div>
        </div>
      </div>

      <div style={{ padding: '2rem' }}>
        {/* Stats Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
          <div style={{
            background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
            border: '1px solid rgba(139, 92, 246, 0.3)',
            borderRadius: '12px',
            padding: '1.5rem'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ color: '#A1A1AA', fontSize: '0.875rem' }}>TOTAL DE CLIENTES</span>
              <Users style={{ width: '20px', height: '20px', color: '#8B5CF6' }} />
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white' }}>{stats.total_clients}</div>
          </div>
          
          <div style={{
            background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
            border: '1px solid rgba(139, 92, 246, 0.3)',
            borderRadius: '12px',
            padding: '1.5rem'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ color: '#A1A1AA', fontSize: '0.875rem' }}>CAMPANHAS ATIVAS</span>
              <BarChart3 style={{ width: '20px', height: '20px', color: '#8B5CF6' }} />
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white' }}>{stats.active_campaigns}</div>
          </div>
          
          <div style={{
            background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
            border: '1px solid rgba(139, 92, 246, 0.3)',
            borderRadius: '12px',
            padding: '1.5rem'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ color: '#A1A1AA', fontSize: '0.875rem' }}>ORÇAMENTO TOTAL</span>
              <span style={{ color: '#F97316', fontSize: '1.25rem' }}>💰</span>
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white' }}>{formatCurrency(stats.total_budget)}</div>
          </div>
          
          <div style={{
            background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
            border: '1px solid rgba(139, 92, 246, 0.3)',
            borderRadius: '12px',
            padding: '1.5rem'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
              <span style={{ color: '#A1A1AA', fontSize: '0.875rem' }}>TOTAL IMPRESSÕES</span>
              <span style={{ color: '#3B82F6', fontSize: '1.25rem' }}>👁️</span>
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white' }}>{formatNumber(stats.total_impressions)}</div>
          </div>
        </div>

        {/* Tabs */}
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '2rem' }}>
          <button
            onClick={() => setActiveTab('clients')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.75rem 1.5rem',
              background: activeTab === 'clients' ? '#8B5CF6' : 'transparent',
              color: activeTab === 'clients' ? 'white' : '#A1A1AA',
              border: activeTab === 'clients' ? 'none' : '1px solid rgba(139, 92, 246, 0.3)',
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            <Users style={{ width: '16px', height: '16px' }} />
            Clientes
          </button>
          <button
            onClick={() => setActiveTab('campaigns')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              padding: '0.75rem 1.5rem',
              background: activeTab === 'campaigns' ? '#8B5CF6' : 'transparent',
              color: activeTab === 'campaigns' ? 'white' : '#A1A1AA',
              border: activeTab === 'campaigns' ? 'none' : '1px solid rgba(139, 92, 246, 0.3)',
              borderRadius: '8px',
              cursor: 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            <BarChart3 style={{ width: '16px', height: '16px' }} />
            Campanhas
          </button>
        </div>

        {/* Content */}
        {activeTab === 'clients' && (
          <div style={{
            background: '#1A1A2E',
            border: '1px solid rgba(139, 92, 246, 0.2)',
            borderRadius: '12px',
            padding: '1.5rem'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'white', margin: 0 }}>Clientes</h2>
              <button
                onClick={() => setShowClientModal(true)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  padding: '0.75rem 1.5rem',
                  background: 'linear-gradient(135deg, #8B5CF6 0%, #A855F7 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  boxShadow: '0 4px 12px rgba(139, 92, 246, 0.3)'
                }}
                onMouseEnter={(e) => {
                  e.target.style.background = 'linear-gradient(135deg, #7C3AED 0%, #9333EA 100%)';
                  e.target.style.transform = 'translateY(-1px)';
                }}
                onMouseLeave={(e) => {
                  e.target.style.background = 'linear-gradient(135deg, #8B5CF6 0%, #A855F7 100%)';
                  e.target.style.transform = 'translateY(0)';
                }}
              >
                <Plus style={{ width: '16px', height: '16px' }} />
                Novo Cliente
              </button>
            </div>

            <div style={{ display: 'grid', gap: '1rem' }}>
              {clients.map((client) => (
                <div key={client.client_id} style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '8px',
                  padding: '1.5rem',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <div>
                    <h3 style={{ fontSize: '1.125rem', fontWeight: 'bold', color: 'white', margin: '0 0 0.25rem 0' }}>
                      {client.name}
                    </h3>
                    <p style={{ color: '#A1A1AA', margin: '0 0 0.25rem 0' }}>{client.company}</p>
                    <p style={{ color: '#A1A1AA', fontSize: '0.875rem', margin: 0 }}>{client.contact_email}</p>
                    <span style={{
                      display: 'inline-block',
                      marginTop: '0.5rem',
                      padding: '0.25rem 0.75rem',
                      background: client.status === 'active' ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                      color: client.status === 'active' ? '#22C55E' : '#EF4444',
                      borderRadius: '12px',
                      fontSize: '0.75rem',
                      fontWeight: '500'
                    }}>
                      {client.status === 'active' ? 'Ativo' : 'Inativo'}
                    </span>
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                      onClick={() => handleViewDashboard(client)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '0.5rem 1rem',
                        background: 'rgba(59, 130, 246, 0.1)',
                        border: '1px solid rgba(59, 130, 246, 0.3)',
                        borderRadius: '6px',
                        color: '#3B82F6',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease'
                      }}
                      onMouseEnter={(e) => {
                        e.target.style.background = 'rgba(59, 130, 246, 0.2)';
                        e.target.style.borderColor = 'rgba(59, 130, 246, 0.5)';
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.background = 'rgba(59, 130, 246, 0.1)';
                        e.target.style.borderColor = 'rgba(59, 130, 246, 0.3)';
                      }}
                    >
                      <Eye style={{ width: '16px', height: '16px' }} />
                      Ver Dashboard
                    </button>
                    <button
                      onClick={() => setShowClientModal(true)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '0.5rem 1rem',
                        background: 'rgba(139, 92, 246, 0.1)',
                        border: '1px solid rgba(139, 92, 246, 0.3)',
                        borderRadius: '6px',
                        color: '#8B5CF6',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease'
                      }}
                      onMouseEnter={(e) => {
                        e.target.style.background = 'rgba(139, 92, 246, 0.2)';
                        e.target.style.borderColor = 'rgba(139, 92, 246, 0.5)';
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.background = 'rgba(139, 92, 246, 0.1)';
                        e.target.style.borderColor = 'rgba(139, 92, 246, 0.3)';
                      }}
                    >
                      <Edit style={{ width: '16px', height: '16px' }} />
                      Editar
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'campaigns' && (
          <div style={{
            background: '#1A1A2E',
            border: '1px solid rgba(139, 92, 246, 0.2)',
            borderRadius: '12px',
            padding: '1.5rem'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'white', margin: 0 }}>Campanhas</h2>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                <button
                  onClick={() => setShowUploadModal(true)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    padding: '0.75rem 1.5rem',
                    background: 'rgba(34, 197, 94, 0.1)',
                    border: '1px solid rgba(34, 197, 94, 0.3)',
                    borderRadius: '8px',
                    color: '#22C55E',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.background = 'rgba(34, 197, 94, 0.2)';
                    e.target.style.borderColor = 'rgba(34, 197, 94, 0.5)';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.background = 'rgba(34, 197, 94, 0.1)';
                    e.target.style.borderColor = 'rgba(34, 197, 94, 0.3)';
                  }}
                >
                  <Upload style={{ width: '16px', height: '16px' }} />
                  Upload CSV
                </button>
                <button
                  onClick={() => setShowCampaignModal(true)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    padding: '0.75rem 1.5rem',
                    background: 'linear-gradient(135deg, #8B5CF6 0%, #A855F7 100%)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    transition: 'all 0.2s ease',
                    boxShadow: '0 4px 12px rgba(139, 92, 246, 0.3)'
                  }}
                  onMouseEnter={(e) => {
                    e.target.style.background = 'linear-gradient(135deg, #7C3AED 0%, #9333EA 100%)';
                    e.target.style.transform = 'translateY(-1px)';
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.background = 'linear-gradient(135deg, #8B5CF6 0%, #A855F7 100%)';
                    e.target.style.transform = 'translateY(0)';
                  }}
                >
                  <Plus style={{ width: '16px', height: '16px' }} />
                  Nova Campanha
                </button>
              </div>
            </div>

            <div style={{ display: 'grid', gap: '1rem' }}>
              {campaigns.map((campaign) => (
                <div key={campaign.campaign_id} style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '8px',
                  padding: '1.5rem',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center'
                }}>
                  <div>
                    <h3 style={{ fontSize: '1.125rem', fontWeight: 'bold', color: 'white', margin: '0 0 0.25rem 0' }}>
                      {campaign.name}
                    </h3>
                    <p style={{ color: '#A1A1AA', margin: '0 0 0.25rem 0' }}>
                      {campaign.start_date} a {campaign.end_date}
                    </p>
                    <p style={{ color: '#A1A1AA', fontSize: '0.875rem', margin: 0 }}>
                      Orçamento: {formatCurrency(campaign.budget)}
                    </p>
                    <span style={{
                      display: 'inline-block',
                      marginTop: '0.5rem',
                      padding: '0.25rem 0.75rem',
                      background: campaign.status === 'active' ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                      color: campaign.status === 'active' ? '#22C55E' : '#EF4444',
                      borderRadius: '12px',
                      fontSize: '0.75rem',
                      fontWeight: '500'
                    }}>
                      {campaign.status === 'active' ? 'Ativa' : 'Inativa'}
                    </span>
                  </div>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <button
                      onClick={() => setShowCampaignModal(true)}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '0.5rem',
                        padding: '0.5rem 1rem',
                        background: 'rgba(139, 92, 246, 0.1)',
                        border: '1px solid rgba(139, 92, 246, 0.3)',
                        borderRadius: '6px',
                        color: '#8B5CF6',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease'
                      }}
                      onMouseEnter={(e) => {
                        e.target.style.background = 'rgba(139, 92, 246, 0.2)';
                        e.target.style.borderColor = 'rgba(139, 92, 246, 0.5)';
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.background = 'rgba(139, 92, 246, 0.1)';
                        e.target.style.borderColor = 'rgba(139, 92, 246, 0.3)';
                      }}
                    >
                      <Edit style={{ width: '16px', height: '16px' }} />
                      Editar
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Modals */}
      {showClientModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.7)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '1rem'
        }} onClick={() => setShowClientModal(false)}>
          <div style={{
            background: 'linear-gradient(135deg, #1A1A2E 0%, #16213E 100%)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '16px',
            padding: '2rem',
            maxWidth: '500px',
            width: '100%',
            maxHeight: '90vh',
            overflowY: 'auto'
          }} onClick={(e) => e.stopPropagation()}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'white', marginBottom: '1.5rem' }}>
              Novo Cliente
            </h3>
            <p style={{ color: '#A1A1AA', marginBottom: '1rem' }}>
              Funcionalidade em desenvolvimento. Modal de criação de cliente será implementado em breve.
            </p>
            <button
              onClick={() => setShowClientModal(false)}
              style={{
                padding: '0.75rem 1.5rem',
                background: 'linear-gradient(135deg, #8B5CF6 0%, #A855F7 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer'
              }}
            >
              Fechar
            </button>
          </div>
        </div>
      )}

      {showCampaignModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.7)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '1rem'
        }} onClick={() => setShowCampaignModal(false)}>
          <div style={{
            background: 'linear-gradient(135deg, #1A1A2E 0%, #16213E 100%)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '16px',
            padding: '2rem',
            maxWidth: '500px',
            width: '100%',
            maxHeight: '90vh',
            overflowY: 'auto'
          }} onClick={(e) => e.stopPropagation()}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'white', marginBottom: '1.5rem' }}>
              Nova Campanha
            </h3>
            <p style={{ color: '#A1A1AA', marginBottom: '1rem' }}>
              Funcionalidade em desenvolvimento. Modal de criação de campanha será implementado em breve.
            </p>
            <button
              onClick={() => setShowCampaignModal(false)}
              style={{
                padding: '0.75rem 1.5rem',
                background: 'linear-gradient(135deg, #8B5CF6 0%, #A855F7 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer'
              }}
            >
              Fechar
            </button>
          </div>
        </div>
      )}

      {showUploadModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0, 0, 0, 0.7)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          zIndex: 1000,
          padding: '1rem'
        }} onClick={() => setShowUploadModal(false)}>
          <div style={{
            background: 'linear-gradient(135deg, #1A1A2E 0%, #16213E 100%)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '16px',
            padding: '2rem',
            maxWidth: '500px',
            width: '100%',
            maxHeight: '90vh',
            overflowY: 'auto'
          }} onClick={(e) => e.stopPropagation()}>
            <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', color: 'white', marginBottom: '1.5rem' }}>
              Upload CSV
            </h3>
            <p style={{ color: '#A1A1AA', marginBottom: '1rem' }}>
              Funcionalidade em desenvolvimento. Upload de dados CSV será implementado em breve.
            </p>
            <button
              onClick={() => setShowUploadModal(false)}
              style={{
                padding: '0.75rem 1.5rem',
                background: 'linear-gradient(135deg, #8B5CF6 0%, #A855F7 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer'
              }}
            >
              Fechar
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;

