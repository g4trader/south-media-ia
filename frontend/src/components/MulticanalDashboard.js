import React, { useState, useEffect } from 'react';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, PointElement, LineElement } from 'chart.js';
import { Bar, Scatter } from 'react-chartjs-2';
import { getDynamicMockData } from '../data/mockSheetsData';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  PointElement,
  LineElement
);

const MulticanalDashboard = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedChannel, setSelectedChannel] = useState('');
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Usar dados mock realistas baseados nas planilhas

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Tentar buscar dados reais da API
      const apiUrl = process.env.REACT_APP_API_URL || 'https://south-media-ia-backend.vercel.app';
      const response = await fetch(`${apiUrl}/api/dashboard/data`);
      
      if (response.ok) {
        const realData = await response.json();
        setDashboardData(realData);
        console.log('✅ Dados reais carregados do Google Sheets:', realData);
      } else {
        throw new Error(`API retornou status ${response.status}`);
      }
    } catch (error) {
      console.warn('⚠️ Erro ao carregar dados reais, usando dados mock:', error.message);
      setError(error.message);
      // Usar dados mock dinâmicos para simular dados das planilhas
      setDashboardData(getDynamicMockData());
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    
    // Auto-refresh a cada 5 minutos
    const interval = setInterval(fetchDashboardData, 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num?.toString() || '0';
  };

  const formatCurrency = (num) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(num || 0);
  };

  const formatPercentage = (num) => {
    return ((num || 0) * 100).toFixed(1) + '%';
  };

  const renderOverviewTab = () => {
    if (!dashboardData) return null;

    const { CONS, PER } = dashboardData;
    const pacing = CONS["Budget Contratado (R$)"] > 0 
      ? (CONS["Budget Utilizado (R$)"] / CONS["Budget Contratado (R$)"]) * 100 
      : 0;

    // Chart data for spend share
    const spendShareData = {
      labels: PER.map(p => p["Canal"]),
      datasets: [{
        label: 'Budget Utilizado (R$)',
        data: PER.map(p => p["Budget Utilizado (R$)"]),
        backgroundColor: [
          'rgba(139, 92, 246, 0.8)',
          'rgba(59, 130, 246, 0.8)',
          'rgba(16, 185, 129, 0.8)',
          'rgba(245, 158, 11, 0.8)',
          'rgba(239, 68, 68, 0.8)',
          'rgba(139, 69, 19, 0.8)'
        ]
      }]
    };

    // Chart data for results
    const resultsData = {
      labels: PER.map(p => p["Canal"]),
      datasets: [
        {
          label: 'Impressões',
          data: PER.map(p => p["Impressões"]),
          backgroundColor: 'rgba(59, 130, 246, 0.8)',
          yAxisID: 'y'
        },
        {
          label: 'Cliques',
          data: PER.map(p => p["Cliques"]),
          backgroundColor: 'rgba(16, 185, 129, 0.8)',
          yAxisID: 'y1'
        }
      ]
    };

    return (
      <div>
        {/* Top Metrics */}
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-white/5 border border-slate-300/20 rounded-xl p-4">
            <div className="text-slate-400 text-xs uppercase tracking-wide mb-2">Budget Contratado</div>
            <div className="text-2xl font-bold text-white">{formatCurrency(CONS["Budget Contratado (R$)"])}</div>
          </div>
          <div className="bg-white/5 border border-slate-300/20 rounded-xl p-4">
            <div className="text-slate-400 text-xs uppercase tracking-wide mb-2">Budget Utilizado</div>
            <div className="text-2xl font-bold text-white">{formatCurrency(CONS["Budget Utilizado (R$)"])}</div>
          </div>
          <div className="bg-white/5 border border-slate-300/20 rounded-xl p-4">
            <div className="text-slate-400 text-xs uppercase tracking-wide mb-2">Pacing</div>
            <div className="text-2xl font-bold text-white">{pacing.toFixed(1)}%</div>
          </div>
          <div className="bg-white/5 border border-slate-300/20 rounded-xl p-4">
            <div className="text-slate-400 text-xs uppercase tracking-wide mb-2">Impressões</div>
            <div className="text-2xl font-bold text-white">{formatNumber(CONS["Impressões"])}</div>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-2 gap-6 mb-6">
          <div className="bg-white/5 border border-slate-300/20 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Distribuição de Investimento</h3>
            <Bar 
              data={spendShareData} 
              options={{
                responsive: true,
                plugins: {
                  legend: { display: false }
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    ticks: { color: '#94a3b8' },
                    grid: { color: 'rgba(148, 163, 184, 0.1)' }
                  },
                  x: {
                    ticks: { color: '#94a3b8' },
                    grid: { color: 'rgba(148, 163, 184, 0.1)' }
                  }
                }
              }}
            />
          </div>
          <div className="bg-white/5 border border-slate-300/20 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Resultados por Canal</h3>
            <Bar 
              data={resultsData} 
              options={{
                responsive: true,
                plugins: {
                  legend: { position: 'bottom' }
                },
                scales: {
                  y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    ticks: { color: '#94a3b8' },
                    grid: { color: 'rgba(148, 163, 184, 0.1)' }
                  },
                  y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    ticks: { color: '#94a3b8' },
                    grid: { drawOnChartArea: false }
                  },
                  x: {
                    ticks: { color: '#94a3b8' },
                    grid: { color: 'rgba(148, 163, 184, 0.1)' }
                  }
                }
              }}
            />
          </div>
        </div>

        {/* Channels Table */}
        <div className="bg-white/5 border border-slate-300/20 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Resumo por Canal</h3>
          <div className="text-slate-400 text-sm mb-4">Valores contratados vs. realizados.</div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-300/20">
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase tracking-wide">Canal</th>
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase tracking-wide">Budget Contratado</th>
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase tracking-wide">Budget Utilizado</th>
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase tracking-wide">Pacing</th>
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase tracking-wide">Impressões</th>
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase tracking-wide">Cliques</th>
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase tracking-wide">CTR</th>
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase tracking-wide">VC (100%)</th>
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase tracking-wide">VTR (100%)</th>
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase tracking-wide">CPV (R$)</th>
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase tracking-wide">CPM (R$)</th>
                </tr>
              </thead>
              <tbody>
                {PER.map((channel, index) => {
                  const channelPacing = channel["Budget Contratado (R$)"] > 0 
                    ? (channel["Budget Utilizado (R$)"] / channel["Budget Contratado (R$)"]) * 100 
                    : 0;
                  
                  return (
                    <tr key={index} className="border-b border-slate-300/10">
                      <td className="py-3 px-4 text-white font-medium">{channel["Canal"]}</td>
                      <td className="py-3 px-4 text-white">{formatCurrency(channel["Budget Contratado (R$)"])}</td>
                      <td className="py-3 px-4 text-white">{formatCurrency(channel["Budget Utilizado (R$)"])}</td>
                      <td className="py-3 px-4 text-white">{channelPacing.toFixed(1)}%</td>
                      <td className="py-3 px-4 text-white">{formatNumber(channel["Impressões"])}</td>
                      <td className="py-3 px-4 text-white">{formatNumber(channel["Cliques"])}</td>
                      <td className="py-3 px-4 text-white">{formatPercentage(channel["CTR"])}</td>
                      <td className="py-3 px-4 text-white">{formatPercentage(channel["VC (100%)"])}</td>
                      <td className="py-3 px-4 text-white">{formatPercentage(channel["VTR (100%)"])}</td>
                      <td className="py-3 px-4 text-white">{formatCurrency(channel["CPV (R$)"])}</td>
                      <td className="py-3 px-4 text-white">{formatCurrency(channel["CPM (R$)"])}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  };

  const renderChannelsTab = () => {
    if (!dashboardData) return null;

    const { PER, DAILY } = dashboardData;
    const selectedChannelData = PER.find(p => p["Canal"] === selectedChannel);
    const selectedChannelDaily = DAILY.filter(d => d["Canal"] === selectedChannel);

    return (
      <div>
        {/* Channel Selector */}
        <div className="bg-white/5 border border-slate-300/20 rounded-xl p-4 mb-4">
          <div className="flex gap-3 items-center flex-wrap">
            <div className="font-bold text-white">Selecione o canal:</div>
            <select 
              value={selectedChannel}
              onChange={(e) => setSelectedChannel(e.target.value)}
              className="px-3 py-2 rounded-lg border border-slate-300/25 bg-white/6 text-white"
            >
              <option value="">Selecione um canal</option>
              {PER.map((channel, index) => (
                <option key={index} value={channel["Canal"]}>{channel["Canal"]}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Channel Metrics */}
        {selectedChannelData && (
          <div className="grid grid-cols-4 gap-4 mb-6">
            <div className="bg-white/5 border border-slate-300/20 rounded-xl p-4">
              <div className="text-slate-400 text-xs uppercase tracking-wide mb-2">Budget Utilizado</div>
              <div className="text-2xl font-bold text-white">{formatCurrency(selectedChannelData["Budget Utilizado (R$)"])}</div>
            </div>
            <div className="bg-white/5 border border-slate-300/20 rounded-xl p-4">
              <div className="text-slate-400 text-xs uppercase tracking-wide mb-2">Impressões</div>
              <div className="text-2xl font-bold text-white">{formatNumber(selectedChannelData["Impressões"])}</div>
            </div>
            <div className="bg-white/5 border border-slate-300/20 rounded-xl p-4">
              <div className="text-slate-400 text-xs uppercase tracking-wide mb-2">Cliques</div>
              <div className="text-2xl font-bold text-white">{formatNumber(selectedChannelData["Cliques"])}</div>
            </div>
            <div className="bg-white/5 border border-slate-300/20 rounded-xl p-4">
              <div className="text-slate-400 text-xs uppercase tracking-wide mb-2">CTR</div>
              <div className="text-2xl font-bold text-white">{formatPercentage(selectedChannelData["CTR"])}</div>
            </div>
          </div>
        )}

        {/* Daily Delivery Table */}
        <div className="bg-white/5 border border-slate-300/20 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">
            Entrega diária — {selectedChannel || '—'}
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-slate-300/20">
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase tracking-wide">Data</th>
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase tracking-wide">Criativo</th>
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase tracking-wide">Investimento (R$)</th>
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase tracking-wide">Starts</th>
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase tracking-wide">25%</th>
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase tracking-wide">50%</th>
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase tracking-wide">75%</th>
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase tracking-wide">100%</th>
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase tracking-wide">Impressões</th>
                  <th className="text-left py-3 px-4 text-slate-400 text-xs uppercase tracking-wide">Cliques</th>
                </tr>
              </thead>
              <tbody>
                {selectedChannelDaily.map((day, index) => (
                  <tr key={index} className="border-b border-slate-300/10">
                    <td className="py-3 px-4 text-white">{day["Data"]}</td>
                    <td className="py-3 px-4 text-white">{day["Criativo"]}</td>
                    <td className="py-3 px-4 text-white">{formatCurrency(day["Investimento (R$)"])}</td>
                    <td className="py-3 px-4 text-white">{formatNumber(day["Starts"])}</td>
                    <td className="py-3 px-4 text-white">{formatNumber(day["25%"])}</td>
                    <td className="py-3 px-4 text-white">{formatNumber(day["50%"])}</td>
                    <td className="py-3 px-4 text-white">{formatNumber(day["75%"])}</td>
                    <td className="py-3 px-4 text-white">{formatNumber(day["100%"])}</td>
                    <td className="py-3 px-4 text-white">{formatNumber(day["Impressões"])}</td>
                    <td className="py-3 px-4 text-white">{formatNumber(day["Cliques"])}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    );
  };

  const renderInsightsTab = () => {
    if (!dashboardData) return null;

    const { CONS, PER } = dashboardData;
    const videoChannels = PER.filter(p => ["YouTube", "TikTok", "Netflix", "Disney", "CTV"].includes(p["Canal"]));
    
    // Find best CPV and VTR
    const bestCPV = videoChannels.reduce((acc, cur) => {
      const cpv = Number(cur["CPV (R$)"] || Infinity);
      return cpv < (acc.val || Infinity) ? { name: cur["Canal"], val: cpv } : acc;
    }, {});

    const bestVTR = videoChannels.reduce((acc, cur) => {
      const vtr = Number(cur["VTR (100%)"] || 0);
      return vtr > (acc.val || -1) ? { name: cur["Canal"], val: vtr } : acc;
    }, {});

    const pacing = CONS["Budget Contratado (R$)"] > 0 
      ? (CONS["Budget Utilizado (R$)"] / CONS["Budget Contratado (R$)"]) * 100 
      : 0;

    return (
      <div>
        <div className="grid grid-cols-2 gap-6 mb-6">
          {/* Video Efficiency Chart */}
          <div className="bg-white/5 border border-slate-300/20 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Eficiência de Vídeo</h3>
            <Scatter 
              data={{
                labels: videoChannels.map(c => c["Canal"]),
                datasets: [{
                  label: 'Canais de Vídeo',
                  data: videoChannels.map(c => ({
                    x: Number(c["CPV (R$)"] || 0),
                    y: Number(c["VTR (100%)"] || 0) * 100
                  })),
                  backgroundColor: 'rgba(139, 92, 246, 0.8)',
                  pointRadius: 8
                }]
              }}
              options={{
                responsive: true,
                plugins: {
                  legend: { display: false }
                },
                scales: {
                  x: {
                    title: { display: true, text: 'CPV (R$) — menor é melhor' },
                    ticks: { color: '#94a3b8' },
                    grid: { color: 'rgba(148, 163, 184, 0.1)' }
                  },
                  y: {
                    title: { display: true, text: 'VTR100 (%) — maior é melhor' },
                    suggestedMax: 100,
                    ticks: { color: '#94a3b8' },
                    grid: { color: 'rgba(148, 163, 184, 0.1)' }
                  }
                }
              }}
            />
          </div>

          {/* Pacing Chart */}
          <div className="bg-white/5 border border-slate-300/20 rounded-xl p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Pacing da Campanha</h3>
            <Bar 
              data={{
                labels: ['Pacing'],
                datasets: [
                  { 
                    label: 'Contratado', 
                    data: [CONS["Budget Contratado (R$)"]] 
                  },
                  { 
                    label: 'Utilizado', 
                    data: [CONS["Budget Utilizado (R$)"]] 
                  }
                ]
              }}
              options={{
                responsive: true,
                plugins: {
                  legend: { position: 'bottom' }
                },
                scales: {
                  x: { stacked: true },
                  y: { stacked: true }
                }
              }}
            />
          </div>
        </div>

        {/* Insights List */}
        <div className="bg-white/5 border border-slate-300/20 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Insights Principais</h3>
          <ul className="space-y-2 text-slate-300">
            {bestCPV.name && (
              <li>🎥 Melhor CPV em vídeo: <strong className="text-white">{bestCPV.name}</strong> ({formatCurrency(bestCPV.val)}).</li>
            )}
            {bestVTR.name && (
              <li>✅ Maior VTR100: <strong className="text-white">{bestVTR.name}</strong> ({formatPercentage(bestVTR.val)}).</li>
            )}
            <li>⏱️ Pacing da campanha: <strong className="text-white">{pacing.toFixed(1)}%</strong> do contratado já foi utilizado.</li>
          </ul>
        </div>

        {/* Optimizations */}
        <div className="bg-white/5 border border-slate-300/20 rounded-xl p-6 mt-4">
          <h3 className="text-lg font-semibold text-white mb-4">Otimizações Recomendadas</h3>
          <ul className="space-y-2 text-slate-300">
            <li><strong>Footfall Display:</strong> Aumentar número de impressões entregues entre 05 a 07/09 para aumentar o tráfego de FOOTFALL</li>
            <li><strong>CTV:</strong> Visibilidade maior em Samsung TV</li>
            <li><strong>Footfall Display:</strong> Ampliar para mais publishers no Nordeste a entrega de Display em Footfall</li>
            <li><strong>TikTok:</strong> Aumentar a entrega em TIK TOK ads</li>
          </ul>
        </div>
      </div>
    );
  };

  const renderPlanningTab = () => {
    return (
      <div>
        <div className="bg-white/5 border border-slate-300/20 rounded-xl p-6 mb-6">
          <h3 className="text-lg font-semibold text-white mb-4">Objetivo da Campanha</h3>
          <p className="text-slate-300">
            Campanha multicanal integrada para maximizar alcance e conversões através de estratégias 
            coordenadas em vídeo (CTV, YouTube, TikTok, Netflix, Disney) e display (Footfall).
          </p>
        </div>

        <div className="grid grid-cols-2 gap-6 mb-6">
          <div className="bg-white/5 border border-slate-300/20 rounded-xl p-6">
            <h4 className="text-white font-semibold mb-3">AUDIÊNCIA & GEOGRAFIA</h4>
            <p className="text-slate-300 text-sm">Segmentação demográfica e geográfica para otimização de entrega.</p>
          </div>
          <div className="bg-white/5 border border-slate-300/20 rounded-xl p-6">
            <h4 className="text-white font-semibold mb-3">CANAIS & PAPÉIS</h4>
            <p className="text-slate-300 text-sm">Definição de funções específicas para cada canal na jornada do consumidor.</p>
          </div>
          <div className="bg-white/5 border border-slate-300/20 rounded-xl p-6">
            <h4 className="text-white font-semibold mb-3">CRIAÇÃO & FORMATOS</h4>
            <p className="text-slate-300 text-sm">Desenvolvimento de criativos adaptados para cada plataforma.</p>
          </div>
          <div className="bg-white/5 border border-slate-300/20 rounded-xl p-6">
            <h4 className="text-white font-semibold mb-3">FLIGHTING & PACING</h4>
            <p className="text-slate-300 text-sm">Cronograma de entrega e distribuição de budget ao longo do tempo.</p>
          </div>
          <div className="bg-white/5 border border-slate-300/20 rounded-xl p-6">
            <h4 className="text-white font-semibold mb-3">KPIS POR CANAL</h4>
            <p className="text-slate-300 text-sm">Métricas específicas para avaliação de performance por canal.</p>
          </div>
          <div className="bg-white/5 border border-slate-300/20 rounded-xl p-6">
            <h4 className="text-white font-semibold mb-3">OTIMIZAÇÃO</h4>
            <p className="text-slate-300 text-sm">Estratégias de melhoria contínua baseadas em dados.</p>
          </div>
          <div className="bg-white/5 border border-slate-300/20 rounded-xl p-6">
            <h4 className="text-white font-semibold mb-3">GOVERNANÇA</h4>
            <p className="text-slate-300 text-sm">Controles e processos para gestão eficiente da campanha.</p>
          </div>
          <div className="bg-white/5 border border-slate-300/20 rounded-xl p-6">
            <h4 className="text-white font-semibold mb-3">MENSURAÇÃO</h4>
            <p className="text-slate-300 text-sm">Sistema de tracking e análise de resultados.</p>
          </div>
        </div>

        <div className="bg-white/5 border border-slate-300/20 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Próximas Ações</h3>
          <ul className="space-y-2 text-slate-300">
            <li>• Revisão semanal de performance por canal</li>
            <li>• Ajustes de budget baseados em pacing</li>
            <li>• Otimização de criativos com baixa performance</li>
            <li>• Expansão de publishers para Footfall Display</li>
          </ul>
        </div>
      </div>
    );
  };

  const renderFootfallTab = () => {
    return (
      <div>
        <div className="bg-white/5 border border-slate-300/20 rounded-xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Relatório Footfall</h3>
          <p className="text-slate-300">
            Análise detalhada de performance do canal Footfall Display, incluindo métricas de 
            conversão, geolocalização e otimizações recomendadas.
          </p>
          <div className="mt-4 p-4 bg-slate-800/50 rounded-lg">
            <p className="text-slate-400 text-sm">
              📊 Dados de conversão Footfall serão integrados aqui em breve.
            </p>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
          <p className="text-white">Carregando dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="bg-white/5 border border-slate-300/20 rounded-xl p-6 mb-6">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-blue-500 rounded-xl flex items-center justify-center text-white font-bold text-xl">
                SM
              </div>
              <div>
                <div className="text-xl font-bold text-white">South Media</div>
                <div className="text-slate-400">Dashboard Multicanal — Vídeo + Display (Footfall)</div>
                {error && (
                  <div className="text-yellow-400 text-sm mt-1">
                    ⚠️ Usando dados simulados (API indisponível)
                  </div>
                )}
                {!error && dashboardData && (
                  <div className="text-green-400 text-sm mt-1">
                    ✅ Dados atualizados do Google Sheets
                  </div>
                )}
                <div className="text-slate-500 text-xs mt-1">
                  📊 Dados integrados com planilhas: CTV, YouTube, TikTok, Disney, Netflix, Footfall Display
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-lg font-semibold text-white">Campanha Multiplataforma</div>
              <div className="text-slate-400">
                Status: <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/20 border border-green-500/40 text-green-400 font-semibold">
                  EM ANDAMENTO
                </span>
              </div>
              <button
                onClick={fetchDashboardData}
                disabled={loading}
                className="mt-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-800 text-white rounded-lg text-sm font-medium transition-colors"
              >
                {loading ? '🔄 Atualizando...' : '🔄 Atualizar Dados'}
              </button>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="grid grid-cols-5 gap-4 mb-6">
          {[
            { id: 'overview', label: '🎬 Visão Geral' },
            { id: 'channels', label: '🧭 Por Canal' },
            { id: 'insights', label: '📊 Análise & Insights' },
            { id: 'planning', label: '📋 Planejamento' },
            { id: 'footfall', label: '👣 Footfall' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`p-3 rounded-xl text-center font-semibold transition-all ${
                activeTab === tab.id
                  ? 'bg-gradient-to-r from-purple-500 to-blue-500 text-white shadow-lg shadow-purple-500/25'
                  : 'bg-white/5 border border-slate-300/20 text-slate-400 hover:text-white hover:bg-white/10'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div>
          {activeTab === 'overview' && renderOverviewTab()}
          {activeTab === 'channels' && renderChannelsTab()}
          {activeTab === 'insights' && renderInsightsTab()}
          {activeTab === 'planning' && renderPlanningTab()}
          {activeTab === 'footfall' && renderFootfallTab()}
        </div>
      </div>
    </div>
  );
};

export default MulticanalDashboard;
