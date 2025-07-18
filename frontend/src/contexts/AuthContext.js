import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth deve ser usado dentro de um AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        // Simular usuário logado em modo demo
        setUser({
          id: 1,
          username: 'g4trader',
          email: 'admin@southmedia.com.br',
          role: 'admin'
        });
      }
    } catch (error) {
      localStorage.removeItem('token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      // Simular autenticação em modo demo
      if (username === 'g4trader' && password === 'g4trader@M4nu5') {
        const mockToken = 'demo_token_' + Date.now();
        const userData = {
          id: 1,
          username: 'g4trader',
          email: 'admin@southmedia.com.br',
          role: 'admin'
        };
        
        localStorage.setItem('token', mockToken);
        setUser(userData);
        
        return { success: true };
      } else {
        return { 
          success: false, 
          error: 'Credenciais inválidas. Use: g4trader / g4trader@M4nu5' 
        };
      }
    } catch (error) {
      return { 
        success: false, 
        error: 'Erro ao fazer login' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  const value = {
    user,
    loading,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

