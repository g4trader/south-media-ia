import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import apiService from '../services/api';
import toast from 'react-hot-toast';

// Registrar componentes do Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const VideoDashboard = () => {
  const [campaignData, setCampaignData] = useState(null);
  const [formatsComparison, setFormatsComparison] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const { campaignId } = useParams();

  useEffect(() => {
    if (campaignId) {
      fetchCampaignData();
    } else {
      fetchFormatsComparison();
    }
  }, [campaignId]);

  const fetchCampaignData = async () => {
    try {
      setLoading(true);
      const data = await apiService.getVideoCampaignDashboard(campaignId);
      setCampaignData(data);
    } catch (error) {
      console.error('Erro ao buscar dados da campanha:', error);
      setError('Erro ao carregar dados da campanha');
      toast.error('Erro ao carregar dados da campanha');
    } finally {
      setLoading(false);
    }
  };

  const fetchFormatsComparison = async () => {
    try {
      setLoading(true);
      const data = await apiService.getVideoFormatsComparison();
      setFormatsComparison(data);
    } catch (error) {
      console.error('Erro ao buscar comparação de formatos:', error);
      setError('Erro ao carregar comparação de formatos');
      toast.error('Erro ao carregar comparação de formatos');
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

  const formatPercentage = (value) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  const formatNumber = (value) => {
    return new Intl.NumberFormat('pt-BR').format(value);
  };

  // Configurações dos gráficos
  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#ffffff',
        },
      },
      title: {
        display: true,
        color: '#ffffff',
      },
    },
    scales: {
      x: {
        ticks: {
          color: '#ffffff',
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
      },
      y: {
        ticks: {
          color: '#ffffff',
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)',
        },
      },
    },
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mb-4"></div>
          <p className="text-white">Carregando dashboard de vídeo...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 mb-4">{error}</p>
          <button 
            onClick={() => navigate('/video')}
            className="btn btn-primary"
          >
            Voltar à Lista
          </button>
        </div>
      </div>
    );
  }

  // Renderizar dashboard específico da campanha
  if (campaignId && campaignData) {
    const { campaign, video_kpis, format_breakdown, daily_performance, top_creatives } = campaignData;

    // Dados para gráfico de performance diária
    const dailyChartData = {
      labels: daily_performance.map(d => new Date(d.date).toLocaleDateString('pt-BR')),
      datasets: [
        {
          label: 'Video Starts',
          data: daily_performance.map(d => d.daily_video_starts),
          borderColor: 'rgb(139, 92, 246)',
          backgroundColor: 'rgba(139, 92, 246, 0.2)',
          tension: 0.1,
        },
        {
          label: 'Taxa de Conclusão (%)',
          data: daily_performance.map(d => d.daily_completion_rate * 100),
          borderColor: 'rgb(34, 197, 94)',
          backgroundColor: 'rgba(34, 197, 94, 0.2)',
          tension: 0.1,
          yAxisID: 'y1',
        },
      ],
    };

    // Dados para gráfico de breakdown por formato
    const formatChartData = {
      labels: format_breakdown.map(f => f.video_format),
      datasets: [
        {
          label: 'Video Starts',
          data: format_breakdown.map(f => f.video_starts),
          backgroundColor: [
            'rgba(139, 92, 246, 0.8)',
            'rgba(34, 197, 94, 0.8)',
            'rgba(251, 191, 36, 0.8)',
            'rgba(239, 68, 68, 0.8)',
            'rgba(59, 130, 246, 0.8)',
          ],
        },
      ],
    };

    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                {campaign.campaign_name}
              </h1>
              <p className="text-gray-300">
                Dashboard de Performance de Vídeo
              </p>
            </div>
            <button
              onClick={() => navigate('/video')}
              className="btn btn-secondary"
            >
              Voltar à Lista
            </button>
          </div>

          {/* KPIs Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="glass-card p-6">
              <h3 className="text-sm font-medium text-gray-400 mb-2">
                Total Video Starts
              </h3>
              <p className="text-2xl font-bold text-white">
                {formatNumber(video_kpis.total_video_starts)}
              </p>
            </div>
            <div className="glass-card p-6">
              <h3 className="text-sm font-medium text-gray-400 mb-2">
                Taxa de Conclusão Média
              </h3>
              <p className="text-2xl font-bold text-green-400">
                {formatPercentage(video_kpis.avg_completion_rate)}
              </p>
            </div>
            <div className="glass-card p-6">
              <h3 className="text-sm font-medium text-gray-400 mb-2">
                Taxa de Skip Média
              </h3>
              <p className="text-2xl font-bold text-red-400">
                {formatPercentage(video_kpis.avg_skip_rate)}
              </p>
            </div>
            <div className="glass-card p-6">
              <h3 className="text-sm font-medium text-gray-400 mb-2">
                Investimento Total
              </h3>
              <p className="text-2xl font-bold text-white">
                {formatCurrency(video_kpis.total_video_investment)}
              </p>
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold text-white mb-4">
                Performance Diária
              </h3>
              <Line data={dailyChartData} options={chartOptions} />
            </div>
            <div className="glass-card p-6">
              <h3 className="text-lg font-semibold text-white mb-4">
                Breakdown por Formato
              </h3>
              <Doughnut data={formatChartData} options={chartOptions} />
            </div>
          </div>

          {/* Top Creatives */}
          <div className="glass-card">
            <div className="p-6 border-b border-gray-700">
              <h2 className="text-xl font-semibold text-white">
                Top Criativos
              </h2>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-800">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                      Criativo
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                      Formato
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                      Video Starts
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                      Taxa de Conclusão
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                      Investimento
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {top_creatives.map((creative, index) => (
                    <tr key={index} className="hover:bg-gray-800/50">
                      <td className="px-6 py-4 text-sm text-white">
                        {creative.creative_name}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-300">
                        {creative.video_format}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-300">
                        {formatNumber(creative.video_starts)}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-300">
                        {formatPercentage(creative.completion_rate)}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-300">
                        {formatCurrency(creative.investment)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Renderizar dashboard geral de comparação de formatos
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">
              Dashboard de Vídeo
            </h1>
            <p className="text-gray-300">
              Comparação de Performance entre Formatos
            </p>
          </div>
          <button
            onClick={() => navigate('/video')}
            className="btn btn-secondary"
          >
            Ver Campanhas
          </button>
        </div>

        {/* Formats Comparison */}
        <div className="glass-card">
          <div className="p-6 border-b border-gray-700">
            <h2 className="text-xl font-semibold text-white">
              Comparação de Formatos de Vídeo
            </h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-800">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Formato
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Campanhas
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Total Starts
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Taxa de Conclusão Média
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Taxa de Skip Média
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                    Investimento Total
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {formatsComparison.map((format, index) => (
                  <tr key={index} className="hover:bg-gray-800/50">
                    <td className="px-6 py-4 text-sm font-medium text-white">
                      {format.video_format}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-300">
                      {format.campaigns_count}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-300">
                      {formatNumber(format.total_starts)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-300">
                      {formatPercentage(format.avg_completion_rate)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-300">
                      {formatPercentage(format.avg_skip_rate)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-300">
                      {formatCurrency(format.total_investment)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoDashboard;

