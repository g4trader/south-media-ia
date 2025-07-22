import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { Line, Doughnut } from 'react-chartjs-2';
import toast from 'react-hot-toast';
import apiService from '../services/api';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement);

const ClientDashboard = () => { campaignId } = location.state || {};
  
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [dashboardData, setDashboardData] = useState(null);

  useEffect(() => {
    if (campaignId) {
      loadDashboardData();
    } else {
      toast.error('ID da campanha não fornecido');
      setLoading(false);
    }
  }, [campaignId, loadDashboardData]);

  const loadDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      const response = await apiService.getCampaignDashboard(campaignId);
      
      if (response.success) {
        setDashboardData(response.data);
      } else {
        toast.error('Erro ao carregar dados da campanha');
      }
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      toast.error('Erro ao carregar dados da campanha');
    } finally {
      setLoading(false);
    }
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

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  // Prepare chart data
  const getCpcChartData = () => {
    if (!dashboardData?.performance_history) return { labels: [], datasets: [] };
    
    const history = dashboardData.performance_history;
    const labels = history.map(item => {
      const date = new Date(item.date);
      return date.toLocaleDateString('pt-BR', { month: 'short', day: 'numeric' });
    });
    
    return {
      labels,
      datasets: [{
        label: 'CPC',
        data: history.map(item => item.cpc),
        borderColor: '#8B5CF6',
        backgroundColor: 'rgba(139, 92, 246, 0.1)',
        tension: 0.4,
        fill: true
      }]
    };
  };

  const getDeviceChartData = () => {
    if (!dashboardData?.device_breakdown) return { labels: [], datasets: [] };
    
    const devices = dashboardData.device_breakdown;
    return {
      labels: devices.map(device => device.device_type),
      datasets: [{
        data: devices.map(device => device.percentage),
        backgroundColor: ['#3B82F6', '#8B5CF6', '#F97316'],
        borderWidth: 0
      }]
    };
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false }
    },
    scales: {
      y: {
        beginAtZero: false,
        grid: { color: 'rgba(255, 255, 255, 0.1)' },
        ticks: { color: '#A1A1AA' }
      },
      x: {
        grid: { color: 'rgba(255, 255, 255, 0.1)' },
        ticks: { color: '#A1A1AA' }
      }
    }
  };

  const doughnutOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false }
    }
  };

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #0F0F23 0%, #16213E 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        fontFamily: 'Inter, sans-serif'
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: '48px',
            height: '48px',
            border: '4px solid rgba(139, 92, 246, 0.3)',
            borderTop: '4px solid #8B5CF6',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 1rem auto'
          }}></div>
          <p>Carregando dashboard da campanha...</p>
        </div>
        <style>
          {`
            @keyframes spin {
              0% { transform: rotate(0deg); }
              100% { transform: rotate(360deg); }
            }
          `}
        </style>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div style={{
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #0F0F23 0%, #16213E 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        fontFamily: 'Inter, sans-serif'
      }}>
        <div style={{ textAlign: 'center' }}>
          <h2>Erro ao carregar dados da campanha</h2>
          <p>Verifique se a campanha existe e tente novamente.</p>
        </div>
      </div>
    );
  }

  const { campaign, strategies, device_breakdown } = dashboardData;

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0F0F23 0%, #16213E 100%)',
      color: '#FFFFFF',
      fontFamily: 'Inter, sans-serif'
    }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '1.5rem' }}>
        {/* Header */}
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '2rem',
          padding: '1.5rem',
          background: '#1A1A2E',
          border: '1px solid rgba(139, 92, 246, 0.2)',
          borderRadius: '12px'
        }}>
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
              <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'white', margin: 0 }}>South Media</h1>
              <p style={{ color: '#A1A1AA', margin: 0 }}>Dashboard de Campanhas</p>
            </div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', color: 'white', margin: 0 }}>
              {campaign.campaign_name}
            </h2>
            <p style={{ color: '#A1A1AA', margin: 0 }}>
              {campaign.date_start} a {campaign.date_end}
            </p>
            <p style={{ color: '#A1A1AA', margin: 0, fontSize: '0.875rem' }}>
              Cliente: {clientName}
            </p>
          </div>
        </div>

        {/* Tabs */}
        <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
          <button
            onClick={() => setActiveTab('overview')}
            style={{
              padding: '0.75rem 1.5rem',
              borderRadius: '8px',
              transition: 'all 0.3s ease',
              background: activeTab === 'overview' ? '#8B5CF6' : 'transparent',
              color: activeTab === 'overview' ? 'white' : '#A1A1AA',
              border: activeTab === 'overview' ? 'none' : '1px solid rgba(139, 92, 246, 0.3)',
              cursor: 'pointer'
            }}
          >
            📊 Visão Geral
          </button>
          <button
            onClick={() => setActiveTab('insights')}
            style={{
              padding: '0.75rem 1.5rem',
              borderRadius: '8px',
              transition: 'all 0.3s ease',
              background: activeTab === 'insights' ? '#8B5CF6' : 'transparent',
              color: activeTab === 'insights' ? 'white' : '#A1A1AA',
              border: activeTab === 'insights' ? 'none' : '1px solid rgba(139, 92, 246, 0.3)',
              cursor: 'pointer'
            }}
          >
            🔍 Análise e Insights
          </button>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div>
            {/* Main Metrics */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
              gap: '1.5rem',
              marginBottom: '2rem'
            }}>
              <div style={{
                background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span style={{ color: '#A1A1AA', fontSize: '0.875rem' }}>VERBA CONTRATADA</span>
                  <span style={{ color: '#8B5CF6', fontSize: '1.25rem' }}>💰</span>
                </div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white' }}>
                  {formatCurrency(campaign.budget_contracted)}
                </div>
              </div>
              
              <div style={{
                background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span style={{ color: '#A1A1AA', fontSize: '0.875rem' }}>IMPRESSÕES CONTRATADAS</span>
                  <span style={{ color: '#8B5CF6', fontSize: '1.25rem' }}>👁️</span>
                </div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white' }}>
                  {formatNumber(campaign.impressions_contracted)}
                </div>
              </div>
              
              <div style={{
                background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span style={{ color: '#A1A1AA', fontSize: '0.875rem' }}>OBJETIVO DA CAMPANHA</span>
                  <span style={{ color: '#8B5CF6', fontSize: '1.25rem' }}>🎯</span>
                </div>
                <div style={{ fontSize: '1.125rem', fontWeight: 'bold', color: 'white' }}>
                  {campaign.objective}
                </div>
              </div>
            </div>

            {/* Performance Metrics */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
              gap: '1.5rem',
              marginBottom: '2rem'
            }}>
              <div style={{
                background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span style={{ color: '#A1A1AA', fontSize: '0.875rem' }}>VERBA UTILIZADA</span>
                  <span style={{ color: '#EF4444', fontSize: '1.25rem' }}>💸</span>
                </div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white' }}>
                  {formatCurrency(campaign.budget_used)}
                </div>
              </div>
              
              <div style={{
                background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span style={{ color: '#A1A1AA', fontSize: '0.875rem' }}>IMPRESSÕES</span>
                  <span style={{ color: '#3B82F6', fontSize: '1.25rem' }}>👁️</span>
                </div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white' }}>
                  {formatNumber(campaign.impressions_delivered)}
                </div>
              </div>
              
              <div style={{
                background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span style={{ color: '#A1A1AA', fontSize: '0.875rem' }}>CLIQUES</span>
                  <span style={{ color: '#22C55E', fontSize: '1.25rem' }}>👆</span>
                </div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white' }}>
                  {formatNumber(campaign.clicks)}
                </div>
              </div>
              
              <div style={{
                background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span style={{ color: '#A1A1AA', fontSize: '0.875rem' }}>CPM</span>
                  <span style={{ color: '#F97316', fontSize: '1.25rem' }}>📊</span>
                </div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white' }}>
                  {formatCurrency(campaign.cpm)}
                </div>
              </div>
            </div>

            {/* Charts and Progress */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: '1.5rem',
              marginBottom: '2rem'
            }}>
              {/* CPC Chart */}
              <div style={{
                background: '#1A1A2E',
                border: '1px solid rgba(139, 92, 246, 0.2)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem', color: 'white' }}>
                  CUSTO POR OBJETIVO
                </h3>
                <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
                  <span style={{ fontSize: '0.875rem', color: '#A1A1AA' }}>CPC</span>
                </div>
                <div style={{ height: '200px' }}>
                  <Line data={getCpcChartData()} options={chartOptions} />
                </div>
                <div style={{ textAlign: 'center', marginTop: '1rem' }}>
                  <div style={{
                    background: '#3B82F6',
                    color: 'white',
                    padding: '0.5rem 1rem',
                    borderRadius: '6px',
                    display: 'inline-block'
                  }}>
                    {formatCurrency(campaign.cpc)}
                  </div>
                </div>
              </div>

              {/* Device Breakdown */}
              <div style={{
                background: '#1A1A2E',
                border: '1px solid rgba(139, 92, 246, 0.2)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem', color: 'white' }}>
                  IMPRESSÕES POR DISPOSITIVO
                </h3>
                <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1rem', height: '200px' }}>
                  <Doughnut data={getDeviceChartData()} options={doughnutOptions} />
                </div>
                <div style={{ fontSize: '0.875rem' }}>
                  {device_breakdown?.map((device, index) => {
                    const colors = ['#3B82F6', '#8B5CF6', '#F97316'];
                    return (
                      <div key={device.device_type} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                        <span style={{ color: colors[index] }}>■ {device.device_type}</span>
                        <span style={{ color: 'white' }}>{device.percentage.toFixed(2)}%</span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Progress Indicators */}
              <div style={{
                background: '#1A1A2E',
                border: '1px solid rgba(139, 92, 246, 0.2)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem', color: 'white' }}>
                  PROGRESSO
                </h3>
                <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
                  <span style={{ fontSize: '0.875rem', color: '#A1A1AA' }}>
                    CTR: {formatPercentage(campaign.ctr)}
                  </span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-around', alignItems: 'center' }}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{
                      width: '80px',
                      height: '80px',
                      borderRadius: '50%',
                      background: `conic-gradient(#8B5CF6 0deg ${Math.min(360, (campaign.impressions_delivered / campaign.impressions_contracted) * 360)}deg, rgba(139, 92, 246, 0.2) ${Math.min(360, (campaign.impressions_delivered / campaign.impressions_contracted) * 360)}deg 360deg)`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      position: 'relative',
                      marginBottom: '0.5rem'
                    }}>
                      <div style={{
                        width: '60px',
                        height: '60px',
                        background: '#1A1A2E',
                        borderRadius: '50%',
                        position: 'absolute'
                      }}></div>
                      <span style={{
                        position: 'relative',
                        zIndex: 1,
                        fontWeight: 'bold',
                        color: '#8B5CF6'
                      }}>
                        {Math.round((campaign.impressions_delivered / campaign.impressions_contracted) * 100)}%
                      </span>
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#A1A1AA' }}>IMPRESSÕES</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{
                      width: '80px',
                      height: '80px',
                      borderRadius: '50%',
                      background: `conic-gradient(#8B5CF6 0deg ${Math.min(360, (campaign.budget_used / campaign.budget_contracted) * 360)}deg, rgba(139, 92, 246, 0.2) ${Math.min(360, (campaign.budget_used / campaign.budget_contracted) * 360)}deg 360deg)`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      position: 'relative',
                      marginBottom: '0.5rem'
                    }}>
                      <div style={{
                        width: '60px',
                        height: '60px',
                        background: '#1A1A2E',
                        borderRadius: '50%',
                        position: 'absolute'
                      }}></div>
                      <span style={{
                        position: 'relative',
                        zIndex: 1,
                        fontWeight: 'bold',
                        color: '#8B5CF6'
                      }}>
                        {Math.round((campaign.budget_used / campaign.budget_contracted) * 100)}%
                      </span>
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#A1A1AA' }}>VERBA UTILIZADA</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Strategies Table */}
            <div style={{
              background: '#1A1A2E',
              border: '1px solid rgba(139, 92, 246, 0.2)',
              borderRadius: '12px',
              padding: '1.5rem'
            }}>
              <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem', color: 'white' }}>
                Estratégias
              </h3>
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', fontSize: '0.875rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid #374151' }}>
                      <th style={{ textAlign: 'left', padding: '0.75rem', color: '#A1A1AA' }}>ESTRATÉGIA</th>
                      <th style={{ textAlign: 'right', padding: '0.75rem', color: '#A1A1AA' }}>VERBA UTILIZADA</th>
                      <th style={{ textAlign: 'right', padding: '0.75rem', color: '#A1A1AA' }}>IMPRESSÕES</th>
                      <th style={{ textAlign: 'right', padding: '0.75rem', color: '#A1A1AA' }}>CLIQUES</th>
                      <th style={{ textAlign: 'right', padding: '0.75rem', color: '#A1A1AA' }}>CTR</th>
                      <th style={{ textAlign: 'right', padding: '0.75rem', color: '#A1A1AA' }}>CPM</th>
                      <th style={{ textAlign: 'right', padding: '0.75rem', color: '#A1A1AA' }}>CPC</th>
                    </tr>
                  </thead>
                  <tbody style={{ color: 'white' }}>
                    {strategies?.map((strategy, index) => (
                      <tr key={index} style={{ borderBottom: '1px solid #374151' }}>
                        <td style={{ padding: '0.75rem' }}>{strategy.strategy_name}</td>
                        <td style={{ textAlign: 'right', padding: '0.75rem' }}>{formatCurrency(strategy.budget_used)}</td>
                        <td style={{ textAlign: 'right', padding: '0.75rem' }}>{formatNumber(strategy.impressions)}</td>
                        <td style={{ textAlign: 'right', padding: '0.75rem' }}>{formatNumber(strategy.clicks)}</td>
                        <td style={{ textAlign: 'right', padding: '0.75rem' }}>{formatPercentage(strategy.ctr)}</td>
                        <td style={{ textAlign: 'right', padding: '0.75rem' }}>{formatCurrency(strategy.cpm)}</td>
                        <td style={{ textAlign: 'right', padding: '0.75rem' }}>{formatCurrency(strategy.cpc)}</td>
                      </tr>
                    ))}
                    <tr style={{ background: '#374151' }}>
                      <td style={{ padding: '0.75rem', fontWeight: 'bold' }}>TOTAL</td>
                      <td style={{ textAlign: 'right', padding: '0.75rem', fontWeight: 'bold' }}>
                        {formatCurrency(campaign.budget_used)}
                      </td>
                      <td style={{ textAlign: 'right', padding: '0.75rem', fontWeight: 'bold' }}>
                        {formatNumber(campaign.impressions_delivered)}
                      </td>
                      <td style={{ textAlign: 'right', padding: '0.75rem', fontWeight: 'bold' }}>
                        {formatNumber(campaign.clicks)}
                      </td>
                      <td style={{ textAlign: 'right', padding: '0.75rem', fontWeight: 'bold' }}>
                        {formatPercentage(campaign.ctr)}
                      </td>
                      <td style={{ textAlign: 'right', padding: '0.75rem', fontWeight: 'bold' }}>
                        {formatCurrency(campaign.cpm)}
                      </td>
                      <td style={{ textAlign: 'right', padding: '0.75rem', fontWeight: 'bold' }}>
                        {formatCurrency(campaign.cpc)}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Insights Tab */}
        {activeTab === 'insights' && (
          <div>
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
              gap: '1.5rem',
              marginBottom: '2rem'
            }}>
              <div style={{
                background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span style={{ color: '#A1A1AA', fontSize: '0.875rem' }}>SCORE DE PERFORMANCE</span>
                  <span style={{ color: '#8B5CF6', fontSize: '1.25rem' }}>🎯</span>
                </div>
                <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'white', marginBottom: '0.5rem' }}>
                  {Math.round((campaign.ctr / 0.002) * 100)}/100
                </div>
                <div style={{ width: '100%', background: '#374151', borderRadius: '9999px', height: '8px' }}>
                  <div style={{ 
                    background: '#8B5CF6', 
                    height: '8px', 
                    borderRadius: '9999px', 
                    width: `${Math.min(100, (campaign.ctr / 0.002) * 100)}%` 
                  }}></div>
                </div>
              </div>
              
              <div style={{
                background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span style={{ color: '#A1A1AA', fontSize: '0.875rem' }}>EFICIÊNCIA DE ORÇAMENTO</span>
                  <span style={{ color: '#F97316', fontSize: '1.25rem' }}>📊</span>
                </div>
                <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'white' }}>
                  {(campaign.impressions_delivered / campaign.impressions_contracted).toFixed(2)}x
                </div>
                <div style={{ fontSize: '0.875rem', color: campaign.impressions_delivered > campaign.impressions_contracted ? '#22C55E' : '#EF4444' }}>
                  {campaign.impressions_delivered > campaign.impressions_contracted ? 'Superentrega' : 'Subentrega'}
                </div>
              </div>
              
              <div style={{
                background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span style={{ color: '#A1A1AA', fontSize: '0.875rem' }}>BENCHMARK GERAL</span>
                  <span style={{ color: '#3B82F6', fontSize: '1.25rem' }}>⚡</span>
                </div>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#3B82F6' }}>
                  {campaign.ctr > 0.002 ? 'Excelente' : campaign.ctr > 0.001 ? 'Bom' : 'Regular'}
                </div>
                <div style={{ fontSize: '0.875rem', color: '#A1A1AA' }}>vs. mercado</div>
              </div>
              
              <div style={{
                background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span style={{ color: '#A1A1AA', fontSize: '0.875rem' }}>DISPOSITIVO DOMINANTE</span>
                  <span style={{ color: '#22C55E', fontSize: '1.25rem' }}>📱</span>
                </div>
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'white' }}>
                  {device_breakdown?.[0]?.device_type || 'N/A'}
                </div>
                <div style={{ fontSize: '0.875rem', color: '#A1A1AA' }}>
                  {device_breakdown?.[0]?.percentage?.toFixed(1)}% do tráfego
                </div>
              </div>
            </div>

            {/* Performance Analysis */}
            <div style={{
              background: '#1A1A2E',
              border: '1px solid rgba(139, 92, 246, 0.2)',
              borderRadius: '12px',
              padding: '1.5rem',
              marginBottom: '2rem'
            }}>
              <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem', color: 'white', display: 'flex', alignItems: 'center' }}>
                📈 Análise de Performance
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
                <div>
                  <h4 style={{ fontWeight: '600', color: 'white', marginBottom: '0.75rem' }}>Métricas Principais</h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span style={{ color: '#A1A1AA' }}>CTR Médio</span>
                      <span style={{ color: 'white', fontWeight: 'bold' }}>{formatPercentage(campaign.ctr)}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span style={{ color: '#A1A1AA' }}>CPC Médio</span>
                      <span style={{ color: 'white', fontWeight: 'bold' }}>{formatCurrency(campaign.cpc)}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span style={{ color: '#A1A1AA' }}>CPM Médio</span>
                      <span style={{ color: 'white', fontWeight: 'bold' }}>{formatCurrency(campaign.cpm)}</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span style={{ color: '#A1A1AA' }}>Eficiência</span>
                      <span style={{
                        background: campaign.impressions_delivered > campaign.impressions_contracted ? '#22C55E' : '#EF4444',
                        color: 'white',
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.75rem'
                      }}>
                        {campaign.impressions_delivered > campaign.impressions_contracted ? 'Alta' : 'Média'}
                      </span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 style={{ fontWeight: '600', color: 'white', marginBottom: '0.75rem' }}>Recomendações</h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    <div style={{
                      padding: '0.75rem',
                      background: 'rgba(59, 130, 246, 0.1)',
                      border: '1px solid rgba(59, 130, 246, 0.3)',
                      borderRadius: '6px'
                    }}>
                      <div style={{ color: 'white', fontWeight: '500', marginBottom: '0.25rem' }}>
                        Otimização de CTR
                      </div>
                      <div style={{ color: '#A1A1AA', fontSize: '0.875rem' }}>
                        Teste novos criativos para melhorar engajamento
                      </div>
                    </div>
                    
                    <div style={{
                      padding: '0.75rem',
                      background: 'rgba(34, 197, 94, 0.1)',
                      border: '1px solid rgba(34, 197, 94, 0.3)',
                      borderRadius: '6px'
                    }}>
                      <div style={{ color: 'white', fontWeight: '500', marginBottom: '0.25rem' }}>
                        Foco em Mobile
                      </div>
                      <div style={{ color: '#A1A1AA', fontSize: '0.875rem' }}>
                        Otimizar criativos para dispositivos móveis
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ClientDashboard;

