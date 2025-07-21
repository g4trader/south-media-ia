import React, { useState } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement } from 'chart.js';
import { Line, Doughnut } from 'react-chartjs-2';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, ArcElement);

const ClientDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');

  // Dados das métricas
  const campaignData = {
    contracted: {
      budget: 100000,
      impressions: 25000000,
      period: '01/07/23 a 31/07/23',
      objective: 'Tráfego para o site'
    },
    performance: {
      budgetUsed: 100000,
      impressions: 26500000,
      clicks: 40500,
      cpm: 3.77
    },
    strategies: [
      { name: 'DWN - Portais de Notícias', budget: 20000, impressions: 5000000, clicks: 7000, ctr: 0.14, cpm: 4.00, cpc: 2.86 },
      { name: 'DWL - Sites do Segmento', budget: 20000, impressions: 4000000, clicks: 353, ctr: 0.14, cpm: 5.00, cpc: 3.13 },
      { name: 'DCS - Conteúdo Semântico - Educação', budget: 10000, impressions: 4000000, clicks: 4800, ctr: 0.12, cpm: 2.50, cpc: 2.08 },
      { name: 'D3P - Interesse em Educação', budget: 10000, impressions: 4000000, clicks: 4800, ctr: 0.12, cpm: 6.00, cpc: 2.08 },
      { name: 'D3P - Estilo de Vida - Estudante', budget: 10000, impressions: 2500000, clicks: 3500, ctr: 0.14, cpm: 4.00, cpc: 2.86 },
      { name: 'D3P - Microsegmento - Jovem Adulto', budget: 10000, impressions: 2500000, clicks: 4000, ctr: 0.16, cpm: 4.00, cpc: 2.50 },
      { name: 'DRG - Retargeting de todo o site', budget: 10000, impressions: 2000000, clicks: 5000, ctr: 0.25, cpm: 5.00, cpc: 2.00 },
      { name: 'D2P - Lookalike de Alunos', budget: 10000, impressions: 2500000, clicks: 5000, ctr: 0.20, cpm: 4.00, cpc: 2.00 }
    ]
  };

  // Configuração do gráfico CPC
  const cpcChartData = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul'],
    datasets: [{
      label: 'CPC',
      data: [3.6, 3.4, 3.2, 3.0, 2.8, 2.6, 2.47],
      borderColor: '#8B5CF6',
      backgroundColor: 'rgba(139, 92, 246, 0.1)',
      tension: 0.4,
      fill: true
    }]
  };

  const cpcChartOptions = {
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

  // Configuração do gráfico de dispositivos
  const deviceChartData = {
    labels: ['Mobile', 'Desktop', 'Tablets'],
    datasets: [{
      data: [80.62, 18.53, 0.84],
      backgroundColor: ['#3B82F6', '#8B5CF6', '#F97316'],
      borderWidth: 0
    }]
  };

  const deviceChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false }
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
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', color: 'white', margin: 0 }}>Campanha de Demonstração</h2>
            <p style={{ color: '#A1A1AA', margin: 0 }}>{campaignData.contracted.period}</p>
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
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white' }}>{formatCurrency(campaignData.contracted.budget)}</div>
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
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white' }}>{formatNumber(campaignData.contracted.impressions)}</div>
              </div>
              
              <div style={{
                background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                  <span style={{ color: '#A1A1AA', fontSize: '0.875rem' }}>PERÍODO DA CAMPANHA</span>
                  <span style={{ color: '#8B5CF6', fontSize: '1.25rem' }}>📅</span>
                </div>
                <div style={{ fontSize: '1.125rem', fontWeight: 'bold', color: 'white' }}>{campaignData.contracted.period}</div>
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
                <div style={{ fontSize: '1.125rem', fontWeight: 'bold', color: 'white' }}>{campaignData.contracted.objective}</div>
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
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white' }}>{formatCurrency(campaignData.performance.budgetUsed)}</div>
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
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white' }}>{formatNumber(campaignData.performance.impressions)}</div>
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
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white' }}>{formatNumber(campaignData.performance.clicks)}</div>
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
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'white' }}>{formatCurrency(campaignData.performance.cpm)}</div>
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
                <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem', color: 'white' }}>CUSTO POR OBJETIVO</h3>
                <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
                  <span style={{ fontSize: '0.875rem', color: '#A1A1AA' }}>CPC</span>
                </div>
                <div style={{ height: '200px' }}>
                  <Line data={cpcChartData} options={cpcChartOptions} />
                </div>
                <div style={{ textAlign: 'center', marginTop: '1rem' }}>
                  <div style={{
                    background: '#3B82F6',
                    color: 'white',
                    padding: '0.5rem 1rem',
                    borderRadius: '6px',
                    display: 'inline-block'
                  }}>
                    R$ 2,47
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
                <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem', color: 'white' }}>IMPRESSÕES POR DISPOSITIVO</h3>
                <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '1rem', height: '200px' }}>
                  <Doughnut data={deviceChartData} options={deviceChartOptions} />
                </div>
                <div style={{ fontSize: '0.875rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <span style={{ color: '#3B82F6' }}>■ Mobile</span>
                    <span style={{ color: 'white' }}>80.62%</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <span style={{ color: '#8B5CF6' }}>■ Desktop</span>
                    <span style={{ color: 'white' }}>18.53%</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <span style={{ color: '#F97316' }}>■ Tablets</span>
                    <span style={{ color: 'white' }}>0.84%</span>
                  </div>
                </div>
              </div>

              {/* Progress Indicators */}
              <div style={{
                background: '#1A1A2E',
                border: '1px solid rgba(139, 92, 246, 0.2)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem', color: 'white' }}>PROGRESSO</h3>
                <div style={{ textAlign: 'center', marginBottom: '1rem' }}>
                  <span style={{ fontSize: '0.875rem', color: '#A1A1AA' }}>CTR: 0.15%</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-around', alignItems: 'center' }}>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{
                      width: '80px',
                      height: '80px',
                      borderRadius: '50%',
                      background: 'conic-gradient(#8B5CF6 0deg 252deg, rgba(139, 92, 246, 0.2) 252deg 360deg)',
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
                      }}>106%</span>
                    </div>
                    <div style={{ fontSize: '0.75rem', color: '#A1A1AA' }}>IMPRESSÕES</div>
                  </div>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{
                      width: '80px',
                      height: '80px',
                      borderRadius: '50%',
                      background: 'conic-gradient(#8B5CF6 0deg 360deg, rgba(139, 92, 246, 0.2) 360deg 360deg)',
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
                      }}>100%</span>
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
              <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem', color: 'white' }}>Estratégias</h3>
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
                    {campaignData.strategies.map((strategy, index) => (
                      <tr key={index} style={{ borderBottom: '1px solid #374151' }}>
                        <td style={{ padding: '0.75rem' }}>{strategy.name}</td>
                        <td style={{ textAlign: 'right', padding: '0.75rem' }}>{formatCurrency(strategy.budget)}</td>
                        <td style={{ textAlign: 'right', padding: '0.75rem' }}>{formatNumber(strategy.impressions)}</td>
                        <td style={{ textAlign: 'right', padding: '0.75rem' }}>{formatNumber(strategy.clicks)}</td>
                        <td style={{ textAlign: 'right', padding: '0.75rem' }}>{(strategy.ctr * 100).toFixed(2)}%</td>
                        <td style={{ textAlign: 'right', padding: '0.75rem' }}>{formatCurrency(strategy.cpm)}</td>
                        <td style={{ textAlign: 'right', padding: '0.75rem' }}>{formatCurrency(strategy.cpc)}</td>
                      </tr>
                    ))}
                    <tr style={{ background: '#374151' }}>
                      <td style={{ padding: '0.75rem', fontWeight: 'bold' }}>TOTAL</td>
                      <td style={{ textAlign: 'right', padding: '0.75rem', fontWeight: 'bold' }}>{formatCurrency(campaignData.performance.budgetUsed)}</td>
                      <td style={{ textAlign: 'right', padding: '0.75rem', fontWeight: 'bold' }}>{formatNumber(campaignData.performance.impressions)}</td>
                      <td style={{ textAlign: 'right', padding: '0.75rem', fontWeight: 'bold' }}>{formatNumber(campaignData.performance.clicks)}</td>
                      <td style={{ textAlign: 'right', padding: '0.75rem', fontWeight: 'bold' }}>0.15%</td>
                      <td style={{ textAlign: 'right', padding: '0.75rem', fontWeight: 'bold' }}>{formatCurrency(campaignData.performance.cpm)}</td>
                      <td style={{ textAlign: 'right', padding: '0.75rem', fontWeight: 'bold' }}>R$ 2,47</td>
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
                <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'white', marginBottom: '0.5rem' }}>78/100</div>
                <div style={{ width: '100%', background: '#374151', borderRadius: '9999px', height: '8px' }}>
                  <div style={{ background: '#8B5CF6', height: '8px', borderRadius: '9999px', width: '78%' }}></div>
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
                <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'white' }}>1.06x</div>
                <div style={{ fontSize: '0.875rem', color: '#22C55E' }}>Superentrega</div>
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
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: '#3B82F6' }}>Good</div>
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
                <div style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'white' }}>Mobile</div>
                <div style={{ fontSize: '0.875rem', color: '#A1A1AA' }}>Dominância móvel</div>
              </div>
            </div>

            {/* Alerts */}
            <div style={{
              background: '#1A1A2E',
              border: '1px solid rgba(139, 92, 246, 0.2)',
              borderRadius: '12px',
              padding: '1.5rem',
              marginBottom: '2rem'
            }}>
              <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem', color: 'white', display: 'flex', alignItems: 'center' }}>
                ⚠️ Alertas de Performance
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0.75rem',
                  background: 'rgba(239, 68, 68, 0.1)',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  borderRadius: '8px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <span style={{ color: '#FBBF24' }}>⚠️</span>
                    <div>
                      <div style={{ color: 'white', fontWeight: '500' }}>Orçamento quase esgotado (&gt;95%)</div>
                      <div style={{ color: '#A1A1AA', fontSize: '0.875rem' }}>Budget</div>
                    </div>
                  </div>
                  <span style={{
                    background: '#EF4444',
                    color: 'white',
                    padding: '0.25rem 0.5rem',
                    borderRadius: '4px',
                    fontSize: '0.75rem'
                  }}>high</span>
                </div>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '0.75rem',
                  background: 'rgba(59, 130, 246, 0.1)',
                  border: '1px solid rgba(59, 130, 246, 0.3)',
                  borderRadius: '8px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                    <span style={{ color: '#3B82F6' }}>ℹ️</span>
                    <div>
                      <div style={{ color: 'white', fontWeight: '500' }}>CTR estável nas últimas 48h</div>
                      <div style={{ color: '#A1A1AA', fontSize: '0.875rem' }}>Performance</div>
                    </div>
                  </div>
                  <span style={{
                    background: '#3B82F6',
                    color: 'white',
                    padding: '0.25rem 0.5rem',
                    borderRadius: '4px',
                    fontSize: '0.75rem'
                  }}>low</span>
                </div>
              </div>
            </div>

            {/* Best and Worst Strategies */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
              gap: '1.5rem',
              marginBottom: '2rem'
            }}>
              <div style={{
                background: '#1A1A2E',
                border: '1px solid rgba(139, 92, 246, 0.2)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem', color: 'white' }}>Melhor Estratégia</h3>
                <div style={{
                  background: 'rgba(34, 197, 94, 0.1)',
                  border: '1px solid rgba(34, 197, 94, 0.3)',
                  borderRadius: '8px',
                  padding: '1rem'
                }}>
                  <h4 style={{ fontWeight: 'bold', color: 'white', marginBottom: '0.75rem' }}>DRG - Retargeting de todo o site</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem', fontSize: '0.875rem' }}>
                    <div>
                      <div style={{ color: '#A1A1AA' }}>Score de Eficiência</div>
                      <div style={{ color: '#22C55E', fontWeight: 'bold', fontSize: '1.25rem' }}>125</div>
                    </div>
                    <div>
                      <div style={{ color: '#A1A1AA' }}>CTR</div>
                      <div style={{ color: 'white', fontWeight: 'bold' }}>25.00%</div>
                    </div>
                    <div>
                      <div style={{ color: '#A1A1AA' }}>CPC</div>
                      <div style={{ color: 'white', fontWeight: 'bold' }}>R$ 2.00</div>
                    </div>
                    <div>
                      <div style={{ color: '#A1A1AA' }}>Volume</div>
                      <div style={{ color: 'white', fontWeight: 'bold' }}>2.0M</div>
                    </div>
                  </div>
                </div>
              </div>

              <div style={{
                background: '#1A1A2E',
                border: '1px solid rgba(139, 92, 246, 0.2)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem', color: 'white' }}>Estratégia para Otimizar</h3>
                <div style={{
                  background: 'rgba(239, 68, 68, 0.1)',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  borderRadius: '8px',
                  padding: '1rem'
                }}>
                  <h4 style={{ fontWeight: 'bold', color: 'white', marginBottom: '0.75rem' }}>DWL - Sites do Segmento</h4>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem', fontSize: '0.875rem' }}>
                    <div>
                      <div style={{ color: '#A1A1AA' }}>Score de Eficiência</div>
                      <div style={{ color: '#EF4444', fontWeight: 'bold', fontSize: '1.25rem' }}>8.8</div>
                    </div>
                    <div>
                      <div style={{ color: '#A1A1AA' }}>CTR</div>
                      <div style={{ color: 'white', fontWeight: 'bold' }}>14.00%</div>
                    </div>
                    <div>
                      <div style={{ color: '#A1A1AA' }}>CPC</div>
                      <div style={{ color: 'white', fontWeight: 'bold' }}>R$ 3.13</div>
                    </div>
                    <div>
                      <div style={{ color: '#A1A1AA' }}>Volume</div>
                      <div style={{ color: 'white', fontWeight: 'bold' }}>4.0M</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Recommendations */}
            <div style={{
              background: '#1A1A2E',
              border: '1px solid rgba(139, 92, 246, 0.2)',
              borderRadius: '12px',
              padding: '1.5rem',
              marginBottom: '2rem'
            }}>
              <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem', color: 'white', display: 'flex', alignItems: 'center' }}>
                🔍 Recomendações de Otimização
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div style={{
                  padding: '1rem',
                  background: 'rgba(239, 68, 68, 0.1)',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  borderRadius: '8px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <h4 style={{ fontWeight: 'bold', color: 'white' }}>Otimização de Orçamento</h4>
                    <span style={{
                      background: '#EF4444',
                      color: 'white',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem'
                    }}>high</span>
                  </div>
                  <p style={{ color: '#D1D5DB', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                    Campanha está superentregando impressões. Considere renegociar orçamento ou ajustar targeting.
                  </p>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <span style={{
                      background: '#374151',
                      color: '#D1D5DB',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem'
                    }}>budget</span>
                    <span style={{
                      background: '#374151',
                      color: '#D1D5DB',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem'
                    }}>cost reduction</span>
                  </div>
                </div>
                
                <div style={{
                  padding: '1rem',
                  background: 'rgba(245, 158, 11, 0.1)',
                  border: '1px solid rgba(245, 158, 11, 0.3)',
                  borderRadius: '8px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <h4 style={{ fontWeight: 'bold', color: 'white' }}>Otimização de CPC</h4>
                    <span style={{
                      background: '#F59E0B',
                      color: 'white',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem'
                    }}>medium</span>
                  </div>
                  <p style={{ color: '#D1D5DB', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                    3 estratégias com CPC alto. Revisar targeting e criativos.
                  </p>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <span style={{
                      background: '#374151',
                      color: '#D1D5DB',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem'
                    }}>strategy</span>
                    <span style={{
                      background: '#374151',
                      color: '#D1D5DB',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem'
                    }}>performance improvement</span>
                  </div>
                </div>
                
                <div style={{
                  padding: '1rem',
                  background: 'rgba(239, 68, 68, 0.1)',
                  border: '1px solid rgba(239, 68, 68, 0.3)',
                  borderRadius: '8px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                    <h4 style={{ fontWeight: 'bold', color: 'white' }}>Renovação de Criativos</h4>
                    <span style={{
                      background: '#EF4444',
                      color: 'white',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem'
                    }}>high</span>
                  </div>
                  <p style={{ color: '#D1D5DB', fontSize: '0.875rem', marginBottom: '0.5rem' }}>
                    CTR geral abaixo da média. Implementar testes A/B com novos formatos.
                  </p>
                  <div style={{ display: 'flex', gap: '0.5rem' }}>
                    <span style={{
                      background: '#374151',
                      color: '#D1D5DB',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem'
                    }}>creative</span>
                    <span style={{
                      background: '#374151',
                      color: '#D1D5DB',
                      padding: '0.25rem 0.5rem',
                      borderRadius: '4px',
                      fontSize: '0.75rem'
                    }}>engagement improvement</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Trends Analysis */}
            <div style={{
              background: '#1A1A2E',
              border: '1px solid rgba(139, 92, 246, 0.2)',
              borderRadius: '12px',
              padding: '1.5rem'
            }}>
              <h3 style={{ fontSize: '1.125rem', fontWeight: '600', marginBottom: '1rem', color: 'white', display: 'flex', alignItems: 'center' }}>
                📈 Análise de Tendências
              </h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
                <div>
                  <h4 style={{ fontWeight: '600', color: 'white', marginBottom: '0.75rem' }}>Tendências Atuais</h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span style={{ color: '#A1A1AA' }}>CPC Trend</span>
                      <span style={{ color: '#22C55E', display: 'flex', alignItems: 'center' }}>📉 Decreasing</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span style={{ color: '#A1A1AA' }}>CTR Trend</span>
                      <span style={{ color: '#3B82F6', display: 'flex', alignItems: 'center' }}>📊 Stable</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span style={{ color: '#A1A1AA' }}>Volume Trend</span>
                      <span style={{ color: '#22C55E', display: 'flex', alignItems: 'center' }}>📈 Increasing</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span style={{ color: '#A1A1AA' }}>Efficiency Trend</span>
                      <span style={{ color: '#22C55E', display: 'flex', alignItems: 'center' }}>📈 Improving</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 style={{ fontWeight: '600', color: 'white', marginBottom: '0.75rem' }}>Previsões</h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span style={{ color: '#A1A1AA' }}>Gasto Projetado</span>
                      <span style={{ color: 'white', fontWeight: 'bold' }}>R$ 105.000</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span style={{ color: '#A1A1AA' }}>Impressões Projetadas</span>
                      <span style={{ color: 'white', fontWeight: 'bold' }}>27.500.000</span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                      <span style={{ color: '#A1A1AA' }}>Ritmo do Orçamento</span>
                      <span style={{
                        background: '#8B5CF6',
                        color: 'white',
                        padding: '0.25rem 0.5rem',
                        borderRadius: '4px',
                        fontSize: '0.75rem'
                      }}>on track</span>
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

