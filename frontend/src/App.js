import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import AdminLogin from './components/AdminLogin';
import ClientDashboard from './components/ClientDashboard';
import AdminDashboard from './components/AdminDashboard';

function ProtectedRoute({ children, role }) {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/admin/login" />;
  }

  if (role && user.role !== role) {
    return <Navigate to="/admin/login" />;
  }

  return children;
}

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/admin/login" element={<AdminLogin />} />
          <Route
            path="/admin/dashboard"
            element={
              <ProtectedRoute role="admin">
                <AdminDashboard />
              </ProtectedRoute>
            }
          />
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <ClientDashboard />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/admin/login" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
