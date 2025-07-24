import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { fetchDashboardData } from '../services/api';

function AdminDashboard() {
  const { user, logout } = useAuth();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const getData = async () => {
      try {
        const response = await fetchDashboardData(user.token);
        setDashboardData(response);
      } catch (err) {
        setError('Erro ao carregar dados do dashboard');
      } finally {
        setLoading(false);
      }
    };

    getData();
  }, [user]);

  const handleLogout = () => {
    logout();
  };

  if (loading) return <div>Carregando dados...</div>;

  return (
    <div style={{ padding: '2rem' }}>
      <h2>Bem-vindo, {user.username}</h2>
      <button onClick={handleLogout}>Sair</button>

      <h3 style={{ marginTop: '2rem' }}>Resumo da Campanha</h3>
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {dashboardData ? (
        <div style={{ marginTop: '1rem' }}>
          <p><strong>Nome da campanha:</strong> {dashboardData.campaign_name}</p>
          <p><strong>Cliques:</strong> {dashboardData.clicks}</p>
          <p><strong>Impressões:</strong> {dashboardData.impressions}</p>
          <p><strong>CTR:</strong> {dashboardData.ctr}</p>
        </div>
      ) : (
        <p>Nenhum dado encontrado.</p>
      )}
    </div>
  );
}

export default AdminDashboard;
