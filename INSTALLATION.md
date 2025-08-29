# Installation Guide - South Media IA

Este guia irá ajudá-lo a instalar todos os pré-requisitos necessários para executar o projeto South Media IA.

## 🖥️ Sistema Operacional

Este guia é específico para **macOS**. Para outros sistemas operacionais, consulte as instruções oficiais.

## 📋 Pré-requisitos

### 1. Node.js 18+ e npm

#### Opção A: Usando Homebrew (Recomendado)
```bash
# Instalar Homebrew (se não tiver)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Node.js
brew install node

# Verificar instalação
node --version
npm --version
```

#### Opção B: Usando nvm (Node Version Manager)
```bash
# Instalar nvm
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# Recarregar terminal ou executar
source ~/.zshrc

# Instalar Node.js 18
nvm install 18
nvm use 18

# Verificar instalação
node --version
npm --version
```

#### Opção C: Download Direto
1. Acesse: https://nodejs.org/
2. Baixe a versão LTS (18.x ou superior)
3. Execute o instalador

### 2. Python 3.9+

#### Verificar se já está instalado
```bash
python3 --version
```

#### Instalar via Homebrew (se necessário)
```bash
brew install python@3.9
```

### 3. Git

#### Verificar se já está instalado
```bash
git --version
```

#### Instalar via Homebrew (se necessário)
```bash
brew install git
```

## 🚀 Instalação Rápida

### 1. Instalar Homebrew (se não tiver)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Instalar todos os pré-requisitos
```bash
# Instalar Node.js, Python e Git
brew install node python@3.9 git

# Verificar instalações
echo "Node.js: $(node --version)"
echo "npm: $(npm --version)"
echo "Python: $(python3 --version)"
echo "Git: $(git --version)"
```

### 3. Executar setup do projeto
```bash
# Clonar o repositório (se ainda não fez)
git clone https://github.com/seu-usuario/south-media-ia.git
cd south-media-ia

# Executar setup automático
./setup-project.sh
```

## 🔧 Configuração Manual

Se preferir configurar manualmente:

### Frontend
```bash
cd frontend
npm install
```

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 🐛 Troubleshooting

### Problema: "command not found: node"
**Solução**: Node.js não está instalado ou não está no PATH
```bash
# Instalar Node.js
brew install node

# Verificar PATH
echo $PATH
```

### Problema: "permission denied"
**Solução**: Problemas de permissão
```bash
# Dar permissão de execução aos scripts
chmod +x setup-project.sh
chmod +x frontend/deploy.sh
```

### Problema: "port already in use"
**Solução**: Porta já está sendo usada
```bash
# Verificar processos na porta
lsof -i :3000  # Frontend
lsof -i :8080  # Backend

# Matar processo se necessário
kill -9 <PID>
```

### Problema: "EACCES: permission denied" no npm
**Solução**: Problemas de permissão do npm
```bash
# Configurar npm para não usar sudo
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.zshrc
source ~/.zshrc
```

## 📞 Suporte

Se encontrar problemas durante a instalação:

1. Verifique se todas as versões estão corretas
2. Consulte a documentação oficial dos projetos
3. Entre em contato com a equipe South Media IA

## ✅ Checklist de Instalação

- [ ] Node.js 18+ instalado
- [ ] npm instalado
- [ ] Python 3.9+ instalado
- [ ] Git instalado
- [ ] Homebrew instalado (opcional, mas recomendado)
- [ ] Script de setup executado com sucesso
- [ ] Frontend rodando em http://localhost:3000
- [ ] Backend rodando em http://localhost:8080

---

**Pronto para começar!** 🚀
