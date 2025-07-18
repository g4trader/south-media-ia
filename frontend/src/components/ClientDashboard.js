import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { 
  TrendingUp, 
  TrendingDown, 
  Eye, 
  MousePointer, 
  DollarSign,
  Calendar,
  Target,
  Smartphone,
  AlertTriangle,
  Info,
  BarChart3
} from 'lucide-react';

const ClientDashboard = () => {
  const { clientId, campaignId } = useParams();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simular carregamento de dados
    setTimeout(() => {
      setDashboardData({
        client: {
          name: 'TechCorp Brasil',
          logo: 'SM'
        },
        campaign: {
          name: 'Campanha de Demonstração',
          period: '01/07/2023 a 31/07/2023',
          objective: 'Tráfego para o site'
        },
        metrics: {
          budget_contracted: 100000,
          budget_used: 100000,
          impressions_contracted: 25000000,
          impressions_delivered: 26500000,
          clicks: 40500,
          cpm: 3.77,
          ctr: 0.15,
          period: '01/07/23 a 31/07/23'
        },
        performance: {
          score: 78,
          efficiency: 1.06,
          benchmark: 'Good',
          dominant_device: 'Mobile'
        },
        alerts: [
          {
            type: 'high',
            title: 'Orçamento quase esgotado (>95%)',
            category: 'Budget',
            description: 'Budget'
          },
          {
            type: 'low',
            title: 'CTR estável nas últimas 48h',
            category: 'Performance',
            description: 'Performance'
          }
        ],
        strategies: [
          {
            name: 'DRG - Retargeting de todo o site',
            type: 'best',
            efficiency_score: 125,
            ctr: 25.00,
            cpc: 2.00,
            volume: 2.0
          },
          {
            name: 'DWL - Sites do Segmento',
            type: 'optimize',
            efficiency_score: 8.8,
            ctr: 14.00,
            cpc: 3.13,
            volume: 4.0
          }
        ],
        recommendations: [
          {
            priority: 'high',
            title: 'Otimização de Orçamento',
            description: 'Campanha está superentregando impressões. Considere renegociar orçamento ou ajustar targeting.',
            tags: ['budget', 'cost reduction']
          },
          {
            priority: 'medium',
            title: 'Otimização de CPC',
            description: '3 estratégias com CPC alto. Revisar targeting e criativos.',
            tags: ['strategy', 'performance improvement']
          },
          {
            priority: 'high',
            title: 'Renovação de Criativos',
            description: 'CTR geral abaixo da média. Implementar testes A/B com novos formatos.',
            tags: ['creative', 'engagement improvement']
          }
        ],
        trends: {
          cpc_trend: 'decreasing',
          ctr_trend: 'stable',
          volume_trend: 'increasing',
          efficiency_trend: 'improving'
        },
        forecasts: {
          projected_spend: 105000,
          projected_impressions: 27500000,
          budget_pace: 'on track'
        },
        device_breakdown: {
          mobile: 80.62,
          desktop: 18.53,
          tablet: 0.84
        },
        strategy_details: [
          {
            strategy: 'DWN - Portais de Notícias',
            budget_used: 20000,
            impressions: 5000000,
            clicks: 7000,
            ctr: 0.14,
            cpm: 4.00,
            cpc: 2.86
          },
          {
            strategy: 'DWL - Sites do Segmento',
            budget_used: 20000,
            impressions: 4000000,
            clicks: 353,
            ctr: 0.14,
            cpm: 5.00,
            cpc: 3.13
          },
          {
            strategy: 'DCS - Conteúdo Semântico - Educação',
            budget_used: 10000,
            impressions: 4000000,
            clicks: 4800,
            ctr: 0.12,
            cpm: 2.50,
            cpc: 2.08
          },
          {
            strategy: 'D3P - Interesse em Educação',
            budget_used: 10000,
            impressions: 4000000,
            clicks: 4800,
            ctr: 0.12,
            cpm: 6.00,
            cpc: 2.08
          },
          {
            strategy: 'D3P - Estilo de Vida - Estudante',
            budget_used: 10000,
            impressions: 2500000,
            clicks: 3500,
            ctr: 0.14,
            cpm: 4.00,
            cpc: 2.86
          },
          {
            strategy: 'D3P - Microssegmento - Jovem Adulto',
            budget_used: 10000,
            impressions: 2500000,
            clicks: 4000,
            ctr: 0.16,
            cpm: 4.00,
            cpc: 2.50
          },
          {
            strategy: 'DRG - Retargeting de todo o site',
            budget_used: 10000,
            impressions: 2000000,
            clicks: 5000,
            ctr: 0.25,
            cpm: 5.00,
            cpc: 2.00
          },
          {
            strategy: 'D2P - Lookalike de Alunos',
            budget_used: 10000,
            impressions: 2500000,
            clicks: 5000,
            ctr: 0.20,
            cpm: 4.00,
            cpc: 2.00
          }
        ]
      });
      setLoading(false);
    }, 1000);
  }, [clientId, campaignId]);

  const formatCurrency = (value) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value || 0);
  };

  const formatNumber = (value) => {
    return new Intl.NumberFormat('pt-BR').format(value || 0);
  };

  const formatPercentage = (value) => {
    return `${(value || 0).toFixed(2)}%`;
  };

  const getTrendIcon = (trend) => {
    switch (trend) {
      case 'increasing':
      case 'improving':
        return <TrendingUp className="text-green-400" size={16} />;
      case 'decreasing':
        return <TrendingDown className="text-red-400" size={16} />;
      case 'stable':
      default:
        return <BarChart3 className="text-blue-400" size={16} />;
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'bg-red-500/20 text-red-400';
      case 'medium': return 'bg-yellow-500/20 text-yellow-400';
      case 'low': return 'bg-blue-500/20 text-blue-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const getPriorityText = (priority) => {
    switch (priority) {
      case 'high': return 'high';
      case 'medium': return 'medium';
      case 'low': return 'low';
      default: return 'low';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900">
        <div className="loading-spinner"></div>
        <span className="ml-3 text-white">Carregando dashboard...</span>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-white mb-4">Dashboard não encontrado</h1>
          <p className="text-gray-300">Verifique se o ID do cliente e campanha estão corretos.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900">
      {/* Header */}
      <header className="bg-black/20 backdrop-blur-sm border-b border-white/10">
        <div className="container mx-auto px-6 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                <span className="text-lg font-bold text-white">{dashboardData.client.logo}</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">{dashboardData.client.name}</h1>
                <p className="text-sm text-gray-300">Dashboard de Campanhas</p>
              </div>
            </div>
            
            <div className="text-right">
              <h2 className="text-lg font-semibold text-white">{dashboardData.campaign.name}</h2>
              <p className="text-sm text-gray-300">{dashboardData.campaign.period}</p>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-black/10 backdrop-blur-sm border-b border-white/5">
        <div className="container mx-auto px-6">
          <div className="flex space-x-8">
            <button className="flex items-center gap-2 px-4 py-3 border-b-2 border-purple-400 text-white">
              <BarChart3 size={16} />
              Visão Geral
            </button>
            <button className="flex items-center gap-2 px-4 py-3 border-b-2 border-transparent text-gray-300 hover:text-white">
              <Target size={16} />
              Análise e Insights
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="container mx-auto px-6 py-8">
        {/* Key Metrics */}
        <div className="grid grid-4 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center gap-3 mb-2">
              <DollarSign className="text-yellow-400" size={20} />
              <span className="text-sm text-gray-300">VERBA CONTRATADA</span>
            </div>
            <p className="text-2xl font-bold text-white">{formatCurrency(dashboardData.metrics.budget_contracted)}</p>
          </div>
          
          <div className="card">
            <div className="flex items-center gap-3 mb-2">
              <Eye className="text-blue-400" size={20} />
              <span className="text-sm text-gray-300">IMPRESSÕES CONTRATADAS</span>
            </div>
            <p className="text-2xl font-bold text-white">{formatNumber(dashboardData.metrics.impressions_contracted)}</p>
          </div>
          
          <div className="card">
            <div className="flex items-center gap-3 mb-2">
              <Calendar className="text-purple-400" size={20} />
              <span className="text-sm text-gray-300">PERÍODO DA CAMPANHA</span>
            </div>
            <p className="text-lg font-semibold text-white">{dashboardData.metrics.period}</p>
          </div>
          
          <div className="card">
            <div className="flex items-center gap-3 mb-2">
              <Target className="text-green-400" size={20} />
              <span className="text-sm text-gray-300">OBJETIVO DA CAMPANHA</span>
            </div>
            <p className="text-lg font-semibold text-white">{dashboardData.campaign.objective}</p>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="grid grid-4 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center gap-3 mb-2">
              <DollarSign className="text-yellow-400" size={20} />
              <span className="text-sm text-gray-300">VERBA UTILIZADA</span>
            </div>
            <p className="text-2xl font-bold text-white">{formatCurrency(dashboardData.metrics.budget_used)}</p>
          </div>
          
          <div className="card">
            <div className="flex items-center gap-3 mb-2">
              <Eye className="text-blue-400" size={20} />
              <span className="text-sm text-gray-300">IMPRESSÕES</span>
            </div>
            <p className="text-2xl font-bold text-white">{formatNumber(dashboardData.metrics.impressions_delivered)}</p>
          </div>
          
          <div className="card">
            <div className="flex items-center gap-3 mb-2">
              <MousePointer className="text-green-400" size={20} />
              <span className="text-sm text-gray-300">CLIQUES</span>
            </div>
            <p className="text-2xl font-bold text-white">{formatNumber(dashboardData.metrics.clicks)}</p>
          </div>
          
          <div className="card">
            <div className="flex items-center gap-3 mb-2">
              <BarChart3 className="text-purple-400" size={20} />
              <span className="text-sm text-gray-300">CPM</span>
            </div>
            <p className="text-2xl font-bold text-white">{formatCurrency(dashboardData.metrics.cpm)}</p>
          </div>
        </div>

        {/* Performance Cards */}
        <div className="grid grid-4 gap-6 mb-8">
          <div className="card">
            <div className="flex items-center gap-3 mb-2">
              <TrendingUp className="text-red-400" size={20} />
              <span className="text-sm text-gray-300">SCORE DE PERFORMANCE</span>
            </div>
            <div className="flex items-center gap-2">
              <p className="text-3xl font-bold text-white">{dashboardData.performance.score}/100</p>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div 
                  className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full" 
                  style={{ width: `${dashboardData.performance.score}%` }}
                ></div>
              </div>
            </div>
          </div>
          
          <div className="card">
            <div className="flex items-center gap-3 mb-2">
              <BarChart3 className="text-green-400" size={20} />
              <span className="text-sm text-gray-300">EFICIÊNCIA DE ORÇAMENTO</span>
            </div>
            <p className="text-2xl font-bold text-green-400">{dashboardData.performance.efficiency}x</p>
            <p className="text-sm text-gray-300">Superentrega</p>
          </div>
          
          <div className="card">
            <div className="flex items-center gap-3 mb-2">
              <Target className="text-yellow-400" size={20} />
              <span className="text-sm text-gray-300">BENCHMARK GERAL</span>
            </div>
            <p className="text-2xl font-bold text-yellow-400">{dashboardData.performance.benchmark}</p>
            <p className="text-sm text-gray-300">vs. mercado</p>
          </div>
          
          <div className="card">
            <div className="flex items-center gap-3 mb-2">
              <Smartphone className="text-blue-400" size={20} />
              <span className="text-sm text-gray-300">DISPOSITIVO DOMINANTE</span>
            </div>
            <p className="text-2xl font-bold text-white">{dashboardData.performance.dominant_device}</p>
            <p className="text-sm text-gray-300">Dominância móvel</p>
          </div>
        </div>

        {/* Charts Section */}
        <div className="grid grid-3 gap-6 mb-8">
          {/* Cost per Objective Chart */}
          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4">CUSTO POR OBJETIVO</h3>
            <div className="text-center">
              <p className="text-sm text-gray-300 mb-2">CPC</p>
              <div className="relative w-32 h-32 mx-auto mb-4">
                <svg className="w-32 h-32 transform -rotate-90" viewBox="0 0 36 36">
                  <path
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="#374151"
                    strokeWidth="3"
                  />
                  <path
                    d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                    fill="none"
                    stroke="#8B5CF6"
                    strokeWidth="3"
                    strokeDasharray="75, 100"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-lg font-bold text-white">3.6</span>
                </div>
              </div>
              <div className="bg-blue-500 text-white px-4 py-2 rounded text-sm font-medium">
                {formatCurrency(2.47)}
              </div>
            </div>
          </div>

          {/* Device Breakdown */}
          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4">IMPRESSÕES POR DISPOSITIVO</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                  <span className="text-sm text-gray-300">Mobile</span>
                </div>
                <span className="text-white font-medium">{formatPercentage(dashboardData.device_breakdown.mobile)}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-purple-500 rounded-full"></div>
                  <span className="text-sm text-gray-300">Desktop</span>
                </div>
                <span className="text-white font-medium">{formatPercentage(dashboardData.device_breakdown.desktop)}</span>
              </div>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-pink-500 rounded-full"></div>
                  <span className="text-sm text-gray-300">Tablets</span>
                </div>
                <span className="text-white font-medium">{formatPercentage(dashboardData.device_breakdown.tablet)}</span>
              </div>
            </div>
          </div>

          {/* Progress Indicators */}
          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4">PROGRESSO</h3>
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-300">CTR: 0.15%</span>
                  <span className="text-white">IMPRESSÕES</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-purple-500/20 rounded-full flex items-center justify-center">
                    <span className="text-xs font-bold text-purple-400">106%</span>
                  </div>
                  <div className="w-8 h-8 bg-purple-500/20 rounded-full flex items-center justify-center">
                    <span className="text-xs font-bold text-purple-400">100%</span>
                  </div>
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-300">VERBA UTILIZADA</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-purple-500/20 rounded-full flex items-center justify-center">
                    <span className="text-xs font-bold text-purple-400">106%</span>
                  </div>
                  <div className="w-8 h-8 bg-purple-500/20 rounded-full flex items-center justify-center">
                    <span className="text-xs font-bold text-purple-400">100%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Performance Alerts */}
        <div className="card mb-8">
          <div className="flex items-center gap-3 mb-6">
            <AlertTriangle className="text-yellow-400" size={24} />
            <h3 className="text-xl font-semibold text-white">Alertas de Performance</h3>
          </div>
          <div className="space-y-4">
            {dashboardData.alerts.map((alert, index) => (
              <div key={index} className={`p-4 rounded-lg border ${
                alert.type === 'high' 
                  ? 'bg-red-500/10 border-red-500/30' 
                  : 'bg-blue-500/10 border-blue-500/30'
              }`}>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {alert.type === 'high' ? (
                      <AlertTriangle className="text-red-400" size={20} />
                    ) : (
                      <Info className="text-blue-400" size={20} />
                    )}
                    <span className="text-white font-medium">{alert.title}</span>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    alert.type === 'high' ? 'bg-red-500/20 text-red-400' : 'bg-blue-500/20 text-blue-400'
                  }`}>
                    {alert.type}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Strategy Performance */}
        <div className="grid grid-2 gap-6 mb-8">
          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4">Melhor Estratégia</h3>
            <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
              <h4 className="text-green-400 font-semibold mb-2">{dashboardData.strategies[0].name}</h4>
              <div className="grid grid-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-300">Score de Eficiência</p>
                  <p className="text-white font-bold">{dashboardData.strategies[0].efficiency_score}</p>
                </div>
                <div>
                  <p className="text-gray-300">CTR</p>
                  <p className="text-white font-bold">{formatPercentage(dashboardData.strategies[0].ctr)}</p>
                </div>
                <div>
                  <p className="text-gray-300">CPC</p>
                  <p className="text-white font-bold">{formatCurrency(dashboardData.strategies[0].cpc)}</p>
                </div>
                <div>
                  <p className="text-gray-300">Volume</p>
                  <p className="text-white font-bold">{dashboardData.strategies[0].volume}M</p>
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <h3 className="text-lg font-semibold text-white mb-4">Estratégia para Otimizar</h3>
            <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-lg">
              <h4 className="text-red-400 font-semibold mb-2">{dashboardData.strategies[1].name}</h4>
              <div className="grid grid-2 gap-4 text-sm">
                <div>
                  <p className="text-gray-300">Score de Eficiência</p>
                  <p className="text-white font-bold">{dashboardData.strategies[1].efficiency_score}</p>
                </div>
                <div>
                  <p className="text-gray-300">CTR</p>
                  <p className="text-white font-bold">{formatPercentage(dashboardData.strategies[1].ctr)}</p>
                </div>
                <div>
                  <p className="text-gray-300">CPC</p>
                  <p className="text-white font-bold">{formatCurrency(dashboardData.strategies[1].cpc)}</p>
                </div>
                <div>
                  <p className="text-gray-300">Volume</p>
                  <p className="text-white font-bold">{dashboardData.strategies[1].volume}M</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Recommendations */}
        <div className="card mb-8">
          <div className="flex items-center gap-3 mb-6">
            <Target className="text-purple-400" size={24} />
            <h3 className="text-xl font-semibold text-white">Recomendações de Otimização</h3>
          </div>
          <div className="space-y-4">
            {dashboardData.recommendations.map((rec, index) => (
              <div key={index} className="p-4 bg-white/5 rounded-lg border border-white/10">
                <div className="flex items-start justify-between mb-3">
                  <h4 className="text-white font-semibold">{rec.title}</h4>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${getPriorityColor(rec.priority)}`}>
                    {getPriorityText(rec.priority)}
                  </span>
                </div>
                <p className="text-gray-300 text-sm mb-3">{rec.description}</p>
                <div className="flex gap-2">
                  {rec.tags.map((tag, tagIndex) => (
                    <span key={tagIndex} className="px-2 py-1 bg-purple-500/20 text-purple-300 text-xs rounded">
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Trends Analysis */}
        <div className="card mb-8">
          <div className="flex items-center gap-3 mb-6">
            <TrendingUp className="text-green-400" size={24} />
            <h3 className="text-xl font-semibold text-white">Análise de Tendências</h3>
          </div>
          <div className="grid grid-4 gap-6">
            <div className="text-center">
              <p className="text-sm text-gray-300 mb-2">Tendências Atuais</p>
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-300">CPC Trend</span>
                  {getTrendIcon(dashboardData.trends.cpc_trend)}
                  <span className="text-green-400 text-sm">Decreasing</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-300">CTR Trend</span>
                  {getTrendIcon(dashboardData.trends.ctr_trend)}
                  <span className="text-blue-400 text-sm">Stable</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-300">Volume Trend</span>
                  {getTrendIcon(dashboardData.trends.volume_trend)}
                  <span className="text-green-400 text-sm">Increasing</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-300">Efficiency Trend</span>
                  {getTrendIcon(dashboardData.trends.efficiency_trend)}
                  <span className="text-green-400 text-sm">Improving</span>
                </div>
              </div>
            </div>

            <div className="text-center">
              <p className="text-sm text-gray-300 mb-2">Previsões</p>
              <div className="space-y-2">
                <div>
                  <p className="text-xs text-gray-400">Gasto Projetado</p>
                  <p className="text-white font-bold">{formatCurrency(dashboardData.forecasts.projected_spend)}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Impressões Projetadas</p>
                  <p className="text-white font-bold">{formatNumber(dashboardData.forecasts.projected_impressions)}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">Ritmo do Orçamento</p>
                  <span className="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded">
                    on track
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Strategy Details Table */}
        <div className="card">
          <h3 className="text-xl font-semibold text-white mb-6">Estratégias</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-3 text-gray-300 font-medium">ESTRATÉGIA</th>
                  <th className="text-right py-3 text-gray-300 font-medium">VERBA UTILIZADA</th>
                  <th className="text-right py-3 text-gray-300 font-medium">IMPRESSÕES</th>
                  <th className="text-right py-3 text-gray-300 font-medium">CLIQUES</th>
                  <th className="text-right py-3 text-gray-300 font-medium">CTR</th>
                  <th className="text-right py-3 text-gray-300 font-medium">CPM</th>
                  <th className="text-right py-3 text-gray-300 font-medium">CPC</th>
                </tr>
              </thead>
              <tbody>
                {dashboardData.strategy_details.map((strategy, index) => (
                  <tr key={index} className="border-b border-white/5 hover:bg-white/5">
                    <td className="py-3 text-white">{strategy.strategy}</td>
                    <td className="py-3 text-right text-white">{formatCurrency(strategy.budget_used)}</td>
                    <td className="py-3 text-right text-white">{formatNumber(strategy.impressions)}</td>
                    <td className="py-3 text-right text-white">{formatNumber(strategy.clicks)}</td>
                    <td className="py-3 text-right text-white">{formatPercentage(strategy.ctr)}</td>
                    <td className="py-3 text-right text-white">{formatCurrency(strategy.cpm)}</td>
                    <td className="py-3 text-right text-white">{formatCurrency(strategy.cpc)}</td>
                  </tr>
                ))}
                <tr className="border-t-2 border-purple-500/30 bg-purple-500/10">
                  <td className="py-3 text-white font-bold">TOTAL</td>
                  <td className="py-3 text-right text-white font-bold">{formatCurrency(dashboardData.metrics.budget_used)}</td>
                  <td className="py-3 text-right text-white font-bold">{formatNumber(dashboardData.metrics.impressions_delivered)}</td>
                  <td className="py-3 text-right text-white font-bold">{formatNumber(dashboardData.metrics.clicks)}</td>
                  <td className="py-3 text-right text-white font-bold">{formatPercentage(dashboardData.metrics.ctr)}</td>
                  <td className="py-3 text-right text-white font-bold">{formatCurrency(dashboardData.metrics.cpm)}</td>
                  <td className="py-3 text-right text-white font-bold">{formatCurrency(2.47)}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  );
};

export default ClientDashboard;

