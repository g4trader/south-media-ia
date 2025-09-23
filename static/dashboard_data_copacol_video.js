// Dados da campanha Video Institucional 90s - Copacol
const CAMPAIGN_DATA = {
  "name": "Campanha Institucional de Video de 90s em Youtube",
  "channel": "YouTube",
  "period_start": "08/09/2025",
  "period_end": "05/10/2025",
  "contracted_impressions": 12250000,
  "contracted_budget": 49009.9,
  "cpm": 4.0
};

// Dados consolidados baseados na planilha real
const CONS = {
  "Budget Contratado (R$)": 49009.9,
  "Budget Utilizado (R$)": 5762.93, // R$ 4.020,55 + R$ 1.742,38
  "Impressões": 1440732, // 1.005.138 + 435.594
  "Starts": 531150, // 228.509 + 302.641
  "Skips": 7936, // 4.258 + 3.678
  "Complete Views": 6607, // 3.175 + 3.432
  "CPM (R$)": 4.0,
  "Pacing (%)": 11.8 // (5.762,93 / 49.009,9) * 100
};

const PER = [
  {
    "Canal": "YouTube",
    "Budget Contratado (R$)": 49009.9,
    "Budget Utilizado (R$)": 5762.93,
    "Impressões": 1440732,
    "Starts": 531150,
    "Skips": 7936,
    "Complete Views": 6607,
    "CPM (R$)": 4.0,
    "Pacing (%)": 11.8,
    "Criativos Únicos": 1
  }
];

// Dados diários baseados na planilha real
const DAILY = [
  {
    "date": "08/09/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  },
  {
    "date": "09/09/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  },
  {
    "date": "10/09/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  },
  {
    "date": "11/09/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  },
  {
    "date": "12/09/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  },
  {
    "date": "13/09/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  },
  {
    "date": "14/09/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  },
  {
    "date": "15/09/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  },
  {
    "date": "16/09/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  },
  {
    "date": "17/09/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  },
  {
    "date": "18/09/2025",
    "creative": "Video Institucional 90s",
    "spend": 4020.55, // Dados da planilha
    "impressions": 1005138, // Dados da planilha
    "starts": 228509, // Dados da planilha
    "skips": 4258, // Dados da planilha
    "complete": 3175, // Dados da planilha
    "cpm": 4.0 // Dados da planilha
  },
  {
    "date": "19/09/2025",
    "creative": "Video Institucional 90s",
    "spend": 1742.38, // Dados da planilha
    "impressions": 435594, // Dados da planilha
    "starts": 302641, // Dados da planilha
    "skips": 3678, // Dados da planilha
    "complete": 3432, // Dados da planilha
    "cpm": 4.0 // Dados da planilha
  },
  {
    "date": "20/09/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  },
  {
    "date": "21/09/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  },
  {
    "date": "22/09/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  },
  {
    "date": "23/09/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  },
  {
    "date": "24/09/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  },
  {
    "date": "25/09/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  },
  {
    "date": "26/09/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  },
  {
    "date": "27/09/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  },
  {
    "date": "28/09/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  },
  {
    "date": "29/09/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  },
  {
    "date": "30/09/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  },
  {
    "date": "01/10/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  },
  {
    "date": "02/10/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  },
  {
    "date": "03/10/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  },
  {
    "date": "04/10/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  },
  {
    "date": "05/10/2025",
    "creative": "Video Institucional 90s",
    "spend": 0.0,
    "impressions": 0,
    "starts": 0,
    "skips": 0,
    "complete": 0,
    "cpm": 0.0
  }
];

// Dados brutos do YouTube baseados na planilha
const YOUTUBE_RAW = {
  "creative": "Video Institucional 90s",
  "date": "2025/09/18-19",
  "starts": 531150, // 228509 + 302641
  "skips": 7936, // 4258 + 3678
  "first_quartile": 31204, // 15404 + 15800
  "midpoint": 11029, // 4925 + 6104
  "third_quartile": 7159, // 2833 + 4326
  "complete_views": 6607, // 3175 + 3432
  "impressions": 1440732, // 1005138 + 435594
  "spend": 5762.93, // 4020.55 + 1742.38
  "cpm": 4.0,
  "cpm_calculated": 4.0,
  "start_rate": 36.87, // (531150 / 1440732) * 100
  "completion_rate": 1.24, // (6607 / 531150) * 100
  "skip_rate": 1.49 // (7936 / 531150) * 100
};