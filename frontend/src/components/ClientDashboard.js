import React, { useContext, useEffect, useState, useCallback } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  CircularProgress,
  Grid,
  Paper,
} from '@mui/material';
import { AuthContext } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';

const ClientDashboard = () => {
  const navigate = useNavigate();
  const { isAuthenticated, logout, userRole } = useContext(AuthContext);
  const [summaryData, setSummaryData] = useState(null);
  const [campaignData, setCampaignData] = useState(null);
  const [loadingSummary, setLoadingSummary] = useState(true);
  const [loadingCampaign, setLoadingCampaign] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAuthenticated || userRole !== 'admin') {
      navigate('/admin/login');
    }
  }, [isAuthenticated, userRole, navigate]);

  const loadDashboardData = useCallback(async () => {
    try {
      setLoadingSummary(true);
      const response = await api.get('/dashboard/resumo');
      setSummaryData(response.data);
    } catch (err) {
      setError('Erro ao carregar dados do resumo.');
    } finally {
      setLoadingSummary(false);
    }
  }, []);

  const loadCampaignData = useCallback(async () => {
    try {
      setLoadingCampaign(true);
      const response = await api.get('/dashboard/campanha');
      setCampaignData(response.data);
    } catch (err) {
      setError('Erro ao carregar dados da campanha.');
    } finally {
      setLoadingCampaign(false);
    }
  }, []);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  const handleLogout = () => {
    logout();
    navigate('/admin/login');
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4">Dashboard do Cliente</Typography>
        <Button variant="outlined" color="secondary" onClick={handleLogout}>
          Sair
        </Button>
      </Box>

      {error && (
        <Typography color="error" mb={2}>
          {error}
        </Typography>
      )}

      {loadingSummary ? (
        <CircularProgress />
      ) : summaryData ? (
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 2 }}>
              <Typography variant="h6">Total de Impressões</Typography>
              <Typography variant="h4">{summaryData.total_impressions}</Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 2 }}>
              <Typography variant="h6">Total de Cliques</Typography>
              <Typography variant="h4">{summaryData.total_clicks}</Typography>
            </Paper>
          </Grid>
        </Grid>
      ) : (
        <Typography>Nenhum dado de resumo disponível.</Typography>
      )}

      <Box mt={4}>
        <Button
          variant="contained"
          color="primary"
          onClick={loadCampaignData}
          disabled={loadingCampaign}
        >
          {loadingCampaign ? <CircularProgress size={24} /> : 'Ver Dashboard'}
        </Button>
      </Box>

      {campaignData && (
        <Box mt={4}>
          <Typography variant="h5" gutterBottom>
            Dados da Campanha
          </Typography>
          <Grid container spacing={2}>
            {campaignData.map((item, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Paper elevation={2} sx={{ p: 2 }}>
                  <Typography variant="subtitle1">Campanha: {item.campaign}</Typography>
                  <Typography>Impressões: {item.impressions}</Typography>
                  <Typography>Cliques: {item.clicks}</Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>
        </Box>
      )}
    </Container>
  );
};

export default ClientDashboard;
