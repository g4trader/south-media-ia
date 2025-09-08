// Dados mock baseados na estrutura real das planilhas do Google Sheets
export const mockSheetsData = {
  CONS: {
    "Budget Contratado (R$)": 500000,
    "Budget Utilizado (R$)": 125000,
    "Impressões": 25000000,
    "Cliques": 125000,
    "Visitas (Footfall)": 8500
  },
  PER: [
    {
      "Canal": "CTV",
      "Budget Contratado (R$)": 120000,
      "Budget Utilizado (R$)": 30000,
      "Impressões": 6000000,
      "Cliques": 30000,
      "CTR": 0.5,
      "VC (100%)": 0.85,
      "VTR (100%)": 0.83,
      "CPV (R$)": 1.0
    },
    {
      "Canal": "YouTube",
      "Budget Contratado (R$)": 100000,
      "Budget Utilizado (R$)": 25000,
      "Impressões": 5000000,
      "Cliques": 25000,
      "CTR": 0.5,
      "VC (100%)": 0.75,
      "VTR (100%)": 0.65,
      "CPV (R$)": 1.0
    },
    {
      "Canal": "TikTok",
      "Budget Contratado (R$)": 80000,
      "Budget Utilizado (R$)": 20000,
      "Impressões": 4000000,
      "Cliques": 20000,
      "CTR": 0.5,
      "VC (100%)": 0.8,
      "VTR (100%)": 0.7,
      "CPV (R$)": 1.0,
      "CPM (R$)": 5.0
    },
    {
      "Canal": "Disney",
      "Budget Contratado (R$)": 70000,
      "Budget Utilizado (R$)": 17500,
      "Impressões": 3500000,
      "Cliques": 17500,
      "CTR": 0.5,
      "VC (100%)": 0.78,
      "VTR (100%)": 0.68,
      "CPV (R$)": 1.0
    },
    {
      "Canal": "Netflix",
      "Budget Contratado (R$)": 60000,
      "Budget Utilizado (R$)": 15000,
      "Impressões": 3000000,
      "Cliques": 15000,
      "CTR": 0.5,
      "VC (100%)": 0.82,
      "VTR (100%)": 0.72,
      "CPV (R$)": 1.0
    },
    {
      "Canal": "Footfall Display",
      "Budget Contratado (R$)": 70000,
      "Budget Utilizado (R$)": 17500,
      "Impressões": 3500000,
      "Cliques": 17500,
      "CTR": 0.5,
      "CPM (R$)": 5.0
    }
  ],
  DAILY: [
    // CTV
    {
      "Canal": "CTV",
      "Data": "2024-01-15",
      "Criativo": "CTV_001",
      "Investimento (R$)": 1500,
      "Starts": 7500,
      "25%": 6000,
      "50%": 4500,
      "75%": 3000,
      "100%": 1500,
      "Impressões": 150000,
      "Cliques": 750
    },
    {
      "Canal": "CTV",
      "Data": "2024-01-16",
      "Criativo": "CTV_002",
      "Investimento (R$)": 1200,
      "Starts": 6000,
      "25%": 4800,
      "50%": 3600,
      "75%": 2400,
      "100%": 1200,
      "Impressões": 120000,
      "Cliques": 600
    },
    // YouTube
    {
      "Canal": "YouTube",
      "Data": "2024-01-15",
      "Criativo": "YT_001",
      "Investimento (R$)": 1000,
      "Starts": 5000,
      "25%": 4000,
      "50%": 3000,
      "75%": 2000,
      "100%": 1000,
      "Impressões": 100000,
      "Cliques": 500
    },
    {
      "Canal": "YouTube",
      "Data": "2024-01-16",
      "Criativo": "YT_002",
      "Investimento (R$)": 800,
      "Starts": 4000,
      "25%": 3200,
      "50%": 2400,
      "75%": 1600,
      "100%": 800,
      "Impressões": 80000,
      "Cliques": 400
    },
    // TikTok
    {
      "Canal": "TikTok",
      "Data": "2024-01-15",
      "Criativo": "TT_001",
      "Investimento (R$)": 800,
      "Starts": 4000,
      "25%": 3200,
      "50%": 2400,
      "75%": 1600,
      "100%": 800,
      "Impressões": 80000,
      "Cliques": 400
    },
    {
      "Canal": "TikTok",
      "Data": "2024-01-16",
      "Criativo": "TT_002",
      "Investimento (R$)": 600,
      "Starts": 3000,
      "25%": 2400,
      "50%": 1800,
      "75%": 1200,
      "100%": 600,
      "Impressões": 60000,
      "Cliques": 300
    },
    // Disney
    {
      "Canal": "Disney",
      "Data": "2024-01-15",
      "Criativo": "DIS_001",
      "Investimento (R$)": 700,
      "Starts": 3500,
      "25%": 2800,
      "50%": 2100,
      "75%": 1400,
      "100%": 700,
      "Impressões": 70000,
      "Cliques": 350
    },
    // Netflix
    {
      "Canal": "Netflix",
      "Data": "2024-01-15",
      "Criativo": "NF_001",
      "Investimento (R$)": 600,
      "Starts": 3000,
      "25%": 2400,
      "50%": 1800,
      "75%": 1200,
      "100%": 600,
      "Impressões": 60000,
      "Cliques": 300
    },
    // Footfall Display
    {
      "Canal": "Footfall Display",
      "Data": "2024-01-15",
      "Criativo": "FF_001",
      "Investimento (R$)": 700,
      "Impressões": 70000,
      "Cliques": 350
    },
    {
      "Canal": "Footfall Display",
      "Data": "2024-01-16",
      "Criativo": "FF_002",
      "Investimento (R$)": 500,
      "Impressões": 50000,
      "Cliques": 250
    }
  ]
};

// Função para simular dados dinâmicos (variações pequenas)
export const getDynamicMockData = () => {
  const baseData = JSON.parse(JSON.stringify(mockSheetsData));
  
  // Adicionar pequenas variações aleatórias para simular dados em tempo real
  baseData.CONS["Budget Utilizado (R$)"] += Math.floor(Math.random() * 1000);
  baseData.CONS["Impressões"] += Math.floor(Math.random() * 10000);
  baseData.CONS["Cliques"] += Math.floor(Math.random() * 100);
  
  // Variações nos canais
  baseData.PER.forEach(channel => {
    channel["Budget Utilizado (R$)"] += Math.floor(Math.random() * 500);
    channel["Impressões"] += Math.floor(Math.random() * 5000);
    channel["Cliques"] += Math.floor(Math.random() * 50);
  });
  
  return baseData;
};
