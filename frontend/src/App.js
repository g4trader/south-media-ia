import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import AdminLogin from './components/AdminLogin';
import AdminDashboard from './components/AdminDashboard';
import ClientDashboard from './components/ClientDashboard';
import MulticanalDashboard from './components/MulticanalDashboard';

// Componente para proteger rotas administrativas
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="loading-spinner"></div>
        <span className="ml-3">Carregando...</span>
      </div>
    );
  }
  
  return user ? children : <Navigate to="/admin/login" replace />;
};

// Componente principal da aplicação
function AppContent() {
  const { user } = useAuth();

  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Rota raiz redireciona para login administrativo ou dashboard se já logado */}
          <Route 
            path="/" 
            element={user ? <Navigate to="/admin/dashboard" replace /> : <Navigate to="/admin/login" replace />} 
          />
          
          {/* Rotas administrativas */}
          <Route path="/admin/login" element={<AdminLogin />} />
          <Route 
            path="/admin/dashboard" 
            element={
              <ProtectedRoute>
                <AdminDashboard />
              </ProtectedRoute>
            } 
          />
          
          {/* Rotas públicas para clientes */}
          <Route path="/dashboard" element={<ClientDashboard />} />
          <Route path="/client/:clientId" element={<ClientDashboard />} />
          <Route path="/client/:clientId/campaign/:campaignId" element={<ClientDashboard />} />
          
          {/* Dashboard Multicanal */}
          <Route path="/multicanal" element={<MulticanalDashboard />} />
          <Route path="/dash-sonho" element={<MulticanalDashboard />} />
          
          {/* Rota 404 */}
          <Route 
            path="*" 
            element={
              <div className="min-h-screen flex items-center justify-center">
                <div className="text-center">
                  <h1 className="text-4xl font-bold text-white mb-4">404</h1>
                  <p className="text-gray-300 mb-6">Página não encontrada</p>
                  <a href="/admin/login" className="btn btn-primary">
                    Ir para Login
                  </a>
                </div>
              </div>
            } 
          />
        </Routes>
        
        {/* Notificações Toast */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: 'rgba(26, 26, 46, 0.95)',
              color: '#fff',
              border: '1px solid rgba(139, 92, 246, 0.3)',
              borderRadius: '8px',
              backdropFilter: 'blur(10px)',
            },
            success: {
              iconTheme: {
                primary: '#10B981',
                secondary: '#fff',
              },
            },
            error: {
              iconTheme: {
                primary: '#EF4444',
                secondary: '#fff',
              },
            },
          }}
        />
      </div>
    </Router>
  );
}

// Componente App com Provider de Autenticação
function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App;


