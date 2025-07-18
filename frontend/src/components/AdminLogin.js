import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogIn, User, Lock, Eye, EyeOff } from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';

const AdminLogin = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  
  const { login, user } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    if (user) {
      navigate('/admin/dashboard');
    }
  }, [user, navigate]);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const result = await login(formData.username, formData.password);
      
      if (result.success) {
        toast.success('Login realizado com sucesso!');
        navigate('/admin/dashboard');
      } else {
        toast.error(result.error);
      }
    } catch (error) {
      toast.error('Erro inesperado. Tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-900 via-purple-900 to-violet-900">
      <div className="w-full max-w-md">
        {/* Logo e Título */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl font-bold text-white">SM</span>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">South Media IA</h1>
          <p className="text-gray-300">Dashboard Administrativo</p>
        </div>

        {/* Formulário de Login */}
        <div className="card">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
              <LogIn size={20} className="text-white" />
            </div>
            <h2 className="text-xl font-semibold text-white">Fazer Login</h2>
          </div>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="form-group">
              <label htmlFor="username" className="label">
                Usuário
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <User className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type="text"
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  className="input pl-10"
                  placeholder="Digite seu usuário"
                  required
                  autoComplete="username"
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="password" className="label">
                Senha
              </label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <Lock className="h-5 w-5 text-gray-400" />
                </div>
                <input
                  type={showPassword ? 'text' : 'password'}
                  id="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="input pl-10 pr-10"
                  placeholder="Digite sua senha"
                  required
                  autoComplete="current-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center"
                >
                  {showPassword ? (
                    <EyeOff className="h-5 w-5 text-gray-400 hover:text-white transition-colors" />
                  ) : (
                    <Eye className="h-5 w-5 text-gray-400 hover:text-white transition-colors" />
                  )}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary w-full"
            >
              {loading ? (
                <>
                  <div className="loading-spinner"></div>
                  Entrando...
                </>
              ) : (
                <>
                  <LogIn size={16} />
                  Entrar
                </>
              )}
            </button>
          </form>

          {/* Credenciais de Demonstração */}
          <div className="mt-6 p-4 bg-blue-900/30 rounded-lg border border-blue-500/30">
            <h3 className="text-sm font-semibold text-blue-300 mb-2">Credenciais de Acesso:</h3>
            <div className="text-xs text-blue-200 space-y-1">
              <p><strong>Usuário:</strong> g4trader</p>
              <p><strong>Senha:</strong> g4trader@M4nu5</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-8">
          <p className="text-sm text-gray-400">
            © 2025 South Media. Todos os direitos reservados.
          </p>
        </div>
      </div>
    </div>
  );
};

export default AdminLogin;

