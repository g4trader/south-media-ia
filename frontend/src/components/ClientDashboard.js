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
    <div className="min-h-screen" style={{ 
      background: 'linear-gradient(135deg, #0F0F23 0%, #16213E 100%)',
      color: '#FFFFFF',
      fontFamily: 'Inter, sans-serif'
    }}>
      <div className="container mx-auto px-4 py-6">
        {/* Header */}
        <div className="flex justify-between items-center mb-8 p-6" style={{
          background: '#1A1A2E',
          border: '1px solid rgba(139, 92, 246, 0.2)',
          borderRadius: '12px'
        }}>
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-orange-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">SM</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-white">South Media</h1>
              <p className="text-gray-400">Dashboard de Campanhas</p>
            </div>
          </div>
          <div className="text-right">
            <h2 className="text-xl font-semibold text-white">Campanha de Demonstração</h2>
            <p className="text-gray-400">{campaignData.contracted.period}</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex space-x-2 mb-6">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-6 py-3 rounded-lg transition-all duration-300 ${
              activeTab === 'overview'
                ? 'bg-purple-600 text-white'
                : 'bg-transparent text-gray-400 border border-purple-600/30'
            }`}
          >
            📊 Visão Geral
          </button>
          <button
            onClick={() => setActiveTab('insights')}
            className={`px-6 py-3 rounded-lg transition-all duration-300 ${
              activeTab === 'insights'
                ? 'bg-purple-600 text-white'
                : 'bg-transparent text-gray-400 border border-purple-600/30'
            }`}
          >
            🔍 Análise e Insights
          </button>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div>
            {/* Main Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="metric-card" style={{
                background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-sm">VERBA CONTRATADA</span>
                  <span className="text-purple-400">💰</span>
                </div>
                <div className="text-2xl font-bold text-white">{formatCurrency(campaignData.contracted.budget)}</div>
              </div>
              
              <div className="metric-card" style={{
                background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-sm">IMPRESSÕES CONTRATADAS</span>
                  <span className="text-purple-400">👁️</span>
                </div>
                <div className="text-2xl font-bold text-white">{formatNumber(campaignData.contracted.impressions)}</div>
              </div>
              
              <div className="metric-card" style={{
                background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-sm">PERÍODO DA CAMPANHA</span>
                  <span className="text-purple-400">📅</span>
                </div>
                <div className="text-lg font-bold text-white">{campaignData.contracted.period}</div>
              </div>
              
              <div className="metric-card" style={{
                background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-sm">OBJETIVO DA CAMPANHA</span>
                  <span className="text-purple-400">🎯</span>
                </div>
                <div className="text-lg font-bold text-white">{campaignData.contracted.objective}</div>
              </div>
            </div>

            {/* Performance Metrics */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="metric-card" style={{
                background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-sm">VERBA UTILIZADA</span>
                  <span className="text-red-400">💸</span>
                </div>
                <div className="text-2xl font-bold text-white">{formatCurrency(campaignData.performance.budgetUsed)}</div>
              </div>
              
              <div className="metric-card" style={{
                background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-sm">IMPRESSÕES</span>
                  <span className="text-blue-400">👁️</span>
                </div>
                <div className="text-2xl font-bold text-white">{formatNumber(campaignData.performance.impressions)}</div>
              </div>
              
              <div className="metric-card" style={{
                background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-sm">CLIQUES</span>
                  <span className="text-green-400">👆</span>
                </div>
                <div className="text-2xl font-bold text-white">{formatNumber(campaignData.performance.clicks)}</div>
              </div>
              
              <div className="metric-card" style={{
                background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-sm">CPM</span>
                  <span className="text-orange-400">📊</span>
                </div>
                <div className="text-2xl font-bold text-white">{formatCurrency(campaignData.performance.cpm)}</div>
              </div>
            </div>

            {/* Charts and Progress */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
              {/* CPC Chart */}
              <div style={{
                background: '#1A1A2E',
                border: '1px solid rgba(139, 92, 246, 0.2)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <h3 className="text-lg font-semibold mb-4 text-white">CUSTO POR OBJETIVO</h3>
                <div className="text-center mb-4">
                  <span className="text-sm text-gray-400">CPC</span>
                </div>
                <div style={{ height: '200px' }}>
                  <Line data={cpcChartData} options={cpcChartOptions} />
                </div>
                <div className="text-center mt-4">
                  <div className="bg-blue-500 text-white px-4 py-2 rounded">R$ 2,47</div>
                </div>
              </div>

              {/* Device Breakdown */}
              <div style={{
                background: '#1A1A2E',
                border: '1px solid rgba(139, 92, 246, 0.2)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <h3 className="text-lg font-semibold mb-4 text-white">IMPRESSÕES POR DISPOSITIVO</h3>
                <div className="flex justify-center mb-4" style={{ height: '200px' }}>
                  <Doughnut data={deviceChartData} options={deviceChartOptions} />
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-blue-400">■ Mobile</span>
                    <span className="text-white">80.62%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-purple-400">■ Desktop</span>
                    <span className="text-white">18.53%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-orange-400">■ Tablets</span>
                    <span className="text-white">0.84%</span>
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
                <h3 className="text-lg font-semibold mb-4 text-white">PROGRESSO</h3>
                <div className="text-center mb-4">
                  <span className="text-sm text-gray-400">CTR: 0.15%</span>
                </div>
                <div className="flex justify-around items-center">
                  <div className="text-center">
                    <div className="progress-circle mb-2" style={{
                      width: '80px',
                      height: '80px',
                      borderRadius: '50%',
                      background: 'conic-gradient(#8B5CF6 0deg 252deg, rgba(139, 92, 246, 0.2) 252deg 360deg)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      position: 'relative'
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
                    <div className="text-xs text-gray-400">IMPRESSÕES</div>
                  </div>
                  <div className="text-center">
                    <div className="progress-circle mb-2" style={{
                      width: '80px',
                      height: '80px',
                      borderRadius: '50%',
                      background: 'conic-gradient(#8B5CF6 0deg 360deg, rgba(139, 92, 246, 0.2) 360deg 360deg)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      position: 'relative'
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
                    <div className="text-xs text-gray-400">VERBA UTILIZADA</div>
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
              <h3 className="text-lg font-semibold mb-4 text-white">Estratégias</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-600">
                      <th className="text-left py-3 text-gray-400">ESTRATÉGIA</th>
                      <th className="text-right py-3 text-gray-400">VERBA UTILIZADA</th>
                      <th className="text-right py-3 text-gray-400">IMPRESSÕES</th>
                      <th className="text-right py-3 text-gray-400">CLIQUES</th>
                      <th className="text-right py-3 text-gray-400">CTR</th>
                      <th className="text-right py-3 text-gray-400">CPM</th>
                      <th className="text-right py-3 text-gray-400">CPC</th>
                    </tr>
                  </thead>
                  <tbody className="text-white">
                    {campaignData.strategies.map((strategy, index) => (
                      <tr key={index} className="border-b border-gray-700">
                        <td className="py-3">{strategy.name}</td>
                        <td className="text-right">{formatCurrency(strategy.budget)}</td>
                        <td className="text-right">{formatNumber(strategy.impressions)}</td>
                        <td className="text-right">{formatNumber(strategy.clicks)}</td>
                        <td className="text-right">{(strategy.ctr * 100).toFixed(2)}%</td>
                        <td className="text-right">{formatCurrency(strategy.cpm)}</td>
                        <td className="text-right">{formatCurrency(strategy.cpc)}</td>
                      </tr>
                    ))}
                    <tr className="bg-gray-800">
                      <td className="py-3 font-bold">TOTAL</td>
                      <td className="text-right font-bold">{formatCurrency(campaignData.performance.budgetUsed)}</td>
                      <td className="text-right font-bold">{formatNumber(campaignData.performance.impressions)}</td>
                      <td className="text-right font-bold">{formatNumber(campaignData.performance.clicks)}</td>
                      <td className="text-right font-bold">0.15%</td>
                      <td className="text-right font-bold">{formatCurrency(campaignData.performance.cpm)}</td>
                      <td className="text-right font-bold">R$ 2,47</td>
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
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
              <div className="metric-card" style={{
                background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-sm">SCORE DE PERFORMANCE</span>
                  <span className="text-purple-400">🎯</span>
                </div>
                <div className="text-3xl font-bold text-white mb-2">78/100</div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div className="bg-purple-500 h-2 rounded-full" style={{ width: '78%' }}></div>
                </div>
              </div>
              
              <div className="metric-card" style={{
                background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-sm">EFICIÊNCIA DE ORÇAMENTO</span>
                  <span className="text-orange-400">📊</span>
                </div>
                <div className="text-3xl font-bold text-white">1.06x</div>
                <div className="text-sm text-green-400">Superentrega</div>
              </div>
              
              <div className="metric-card" style={{
                background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-sm">BENCHMARK GERAL</span>
                  <span className="text-blue-400">⚡</span>
                </div>
                <div className="text-2xl font-bold text-blue-400">Good</div>
                <div className="text-sm text-gray-400">vs. mercado</div>
              </div>
              
              <div className="metric-card" style={{
                background: 'linear-gradient(135deg, #1A1A2E 0%, rgba(139, 92, 246, 0.1) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.3)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-gray-400 text-sm">DISPOSITIVO DOMINANTE</span>
                  <span className="text-green-400">📱</span>
                </div>
                <div className="text-2xl font-bold text-white">Mobile</div>
                <div className="text-sm text-gray-400">Dominância móvel</div>
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
              <h3 className="text-lg font-semibold mb-4 text-white flex items-center">
                ⚠️ Alertas de Performance
              </h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-3 bg-red-900/30 border border-red-500/30 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <span className="text-yellow-400">⚠️</span>
                    <div>
                      <div className="text-white font-medium">Orçamento quase esgotado (&gt;95%)</div>
                      <div className="text-gray-400 text-sm">Budget</div>
                    </div>
                  </div>
                  <span className="bg-red-500 text-white px-2 py-1 rounded text-xs">high</span>
                </div>
                <div className="flex items-center justify-between p-3 bg-blue-900/30 border border-blue-500/30 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <span className="text-blue-400">ℹ️</span>
                    <div>
                      <div className="text-white font-medium">CTR estável nas últimas 48h</div>
                      <div className="text-gray-400 text-sm">Performance</div>
                    </div>
                  </div>
                  <span className="bg-blue-500 text-white px-2 py-1 rounded text-xs">low</span>
                </div>
              </div>
            </div>

            {/* Best and Worst Strategies */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
              <div style={{
                background: '#1A1A2E',
                border: '1px solid rgba(139, 92, 246, 0.2)',
                borderRadius: '12px',
                padding: '1.5rem'
              }}>
                <h3 className="text-lg font-semibold mb-4 text-white">Melhor Estratégia</h3>
                <div className="bg-green-900/30 border border-green-500/30 rounded-lg p-4">
                  <h4 className="font-bold text-white mb-3">DRG - Retargeting de todo o site</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="text-gray-400">Score de Eficiência</div>
                      <div className="text-green-400 font-bold text-xl">125</div>
                    </div>
                    <div>
                      <div className="text-gray-400">CTR</div>
                      <div className="text-white font-bold">25.00%</div>
                    </div>
                    <div>
                      <div className="text-gray-400">CPC</div>
                      <div className="text-white font-bold">R$ 2.00</div>
                    </div>
                    <div>
                      <div className="text-gray-400">Volume</div>
                      <div className="text-white font-bold">2.0M</div>
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
                <h3 className="text-lg font-semibold mb-4 text-white">Estratégia para Otimizar</h3>
                <div className="bg-red-900/30 border border-red-500/30 rounded-lg p-4">
                  <h4 className="font-bold text-white mb-3">DWL - Sites do Segmento</h4>
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="text-gray-400">Score de Eficiência</div>
                      <div className="text-red-400 font-bold text-xl">8.8</div>
                    </div>
                    <div>
                      <div className="text-gray-400">CTR</div>
                      <div className="text-white font-bold">14.00%</div>
                    </div>
                    <div>
                      <div className="text-gray-400">CPC</div>
                      <div className="text-white font-bold">R$ 3.13</div>
                    </div>
                    <div>
                      <div className="text-gray-400">Volume</div>
                      <div className="text-white font-bold">4.0M</div>
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
              <h3 className="text-lg font-semibold mb-4 text-white flex items-center">
                🔍 Recomendações de Otimização
              </h3>
              <div className="space-y-4">
                <div className="p-4 bg-red-900/30 border border-red-500/30 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-bold text-white">Otimização de Orçamento</h4>
                    <span className="bg-red-500 text-white px-2 py-1 rounded text-xs">high</span>
                  </div>
                  <p className="text-gray-300 text-sm mb-2">Campanha está superentregando impressões. Considere renegociar orçamento ou ajustar targeting.</p>
                  <div className="flex space-x-2">
                    <span className="bg-gray-700 text-gray-300 px-2 py-1 rounded text-xs">budget</span>
                    <span className="bg-gray-700 text-gray-300 px-2 py-1 rounded text-xs">cost reduction</span>
                  </div>
                </div>
                
                <div className="p-4 bg-yellow-900/30 border border-yellow-500/30 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-bold text-white">Otimização de CPC</h4>
                    <span className="bg-yellow-500 text-white px-2 py-1 rounded text-xs">medium</span>
                  </div>
                  <p className="text-gray-300 text-sm mb-2">3 estratégias com CPC alto. Revisar targeting e criativos.</p>
                  <div className="flex space-x-2">
                    <span className="bg-gray-700 text-gray-300 px-2 py-1 rounded text-xs">strategy</span>
                    <span className="bg-gray-700 text-gray-300 px-2 py-1 rounded text-xs">performance improvement</span>
                  </div>
                </div>
                
                <div className="p-4 bg-red-900/30 border border-red-500/30 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-bold text-white">Renovação de Criativos</h4>
                    <span className="bg-red-500 text-white px-2 py-1 rounded text-xs">high</span>
                  </div>
                  <p className="text-gray-300 text-sm mb-2">CTR geral abaixo da média. Implementar testes A/B com novos formatos.</p>
                  <div className="flex space-x-2">
                    <span className="bg-gray-700 text-gray-300 px-2 py-1 rounded text-xs">creative</span>
                    <span className="bg-gray-700 text-gray-300 px-2 py-1 rounded text-xs">engagement improvement</span>
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
              <h3 className="text-lg font-semibold mb-4 text-white flex items-center">
                📈 Análise de Tendências
              </h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-white mb-3">Tendências Atuais</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">CPC Trend</span>
                      <span className="text-green-400 flex items-center">📉 Decreasing</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">CTR Trend</span>
                      <span className="text-blue-400 flex items-center">📊 Stable</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Volume Trend</span>
                      <span className="text-green-400 flex items-center">📈 Increasing</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Efficiency Trend</span>
                      <span className="text-green-400 flex items-center">📈 Improving</span>
                    </div>
                  </div>
                </div>
                
                <div>
                  <h4 className="font-semibold text-white mb-3">Previsões</h4>
                  <div className="space-y-3">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Gasto Projetado</span>
                      <span className="text-white font-bold">R$ 105.000</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Impressões Projetadas</span>
                      <span className="text-white font-bold">27.500.000</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Ritmo do Orçamento</span>
                      <span className="bg-purple-500 text-white px-2 py-1 rounded text-xs">on track</span>
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

