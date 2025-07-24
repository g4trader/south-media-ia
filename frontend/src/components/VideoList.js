import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import apiService from '../services/api';
import toast from 'react-hot-toast';

const VideoList = () => {
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchVideoCampaigns();
  }, []);

  const fetchVideoCampaigns = async () => {
    try {
      setLoading(true);
      const data = await apiService.getVideoCampaigns();
      setCampaigns(data);
    } catch (error) {
      console.error('Erro ao buscar campanhas de vídeo:', error);
      setError('Erro ao carregar campanhas de vídeo');
      toast.error('Erro ao carregar campanhas de vídeo');
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

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('pt-BR');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="loading-spinner mb-4"></div>
          <p className="text-white">Carregando campanhas de vídeo...</p>
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
            onClick={fetchVideoCampaigns}
            className="btn btn-primary"
          >
            Tentar Novamente
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-white mb-2">
              Campanhas de Vídeo
            </h1>
            <p className="text-gray-300">
              Gerencie e analise suas campanhas de vídeo
            </p>
          </div>
          <div className="flex gap-4">
            <button
              onClick={() => navigate('/admin/dashboard')}
              className="btn btn-secondary"
            >
              Voltar ao Dashboard
            </button>
            <button
              onClick={() => navigate('/video/dashboard')}
              className="btn btn-primary"
            >
              Dashboard de Vídeo
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="glass-card p-6">
            <h3 className="text-sm font-medium text-gray-400 mb-2">
              Total de Campanhas
            </h3>
            <p className="text-2xl font-bold text-white">
              {campaigns.length}
            </p>
          </div>
          <div className="glass-card p-6">
            <h3 className="text-sm font-medium text-gray-400 mb-2">
              Orçamento Total
            </h3>
            <p className="text-2xl font-bold text-white">
              {formatCurrency(
                campaigns.reduce((sum, campaign) => sum + (campaign.budget_contracted || 0), 0)
              )}
            </p>
          </div>
          <div className="glass-card p-6">
            <h3 className="text-sm font-medium text-gray-400 mb-2">
              Total de Criativos
            </h3>
            <p className="text-2xl font-bold text-white">
              {campaigns.reduce((sum, campaign) => sum + (campaign.video_creatives_count || 0), 0)}
            </p>
          </div>
          <div className="glass-card p-6">
            <h3 className="text-sm font-medium text-gray-400 mb-2">
              Campanhas Ativas
            </h3>
            <p className="text-2xl font-bold text-white">
              {campaigns.filter(campaign => {
                const endDate = new Date(campaign.date_end);
                return endDate >= new Date();
              }).length}
            </p>
          </div>
        </div>

        {/* Campaigns Table */}
        <div className="glass-card overflow-hidden">
          <div className="p-6 border-b border-gray-700">
            <h2 className="text-xl font-semibold text-white">
              Lista de Campanhas
            </h2>
          </div>
          
          {campaigns.length === 0 ? (
            <div className="p-8 text-center">
              <p className="text-gray-400">Nenhuma campanha de vídeo encontrada</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-800">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                      Campanha
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                      Período
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                      Objetivo
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                      Orçamento
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                      Criativos
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">
                      Ações
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-700">
                  {campaigns.map((campaign) => (
                    <tr key={campaign.campaign_id} className="hover:bg-gray-800/50">
                      <td className="px-6 py-4">
                        <div>
                          <div className="text-sm font-medium text-white">
                            {campaign.campaign_name}
                          </div>
                          <div className="text-sm text-gray-400">
                            ID: {campaign.campaign_id}
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-300">
                          {formatDate(campaign.date_start)} - {formatDate(campaign.date_end)}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-300">
                          {campaign.objective || 'N/A'}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm text-gray-300">
                          {formatCurrency(campaign.budget_contracted || 0)}
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                          {campaign.video_creatives_count} criativos
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <button
                          onClick={() => navigate(`/video/campaign/${campaign.campaign_id}`)}
                          className="text-purple-400 hover:text-purple-300 text-sm font-medium"
                        >
                          Ver Detalhes
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default VideoList;

