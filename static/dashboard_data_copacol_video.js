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

// Dados simulados baseados nas informações fornecidas
const CONS = {
  "Budget Contratado (R$)": 49009.9,
  "Budget Utilizado (R$)": 11525.86, // Calculado baseado nas impressões e CPM
  "Impressões": 1440732,
  "Starts": 531150,
  "Skips": 7936,
  "Complete Views": 6607,
  "CPM (R$)": 8.0,
  "Pacing (%)": 23.5 // Calculado: (11525.86 / 49009.9) * 100
};

const PER = [
  {
    "Canal": "YouTube",
    "Budget Contratado (R$)": 49009.9,
    "Budget Utilizado (R$)": 11525.86,
    "Impressões": 1440732,
    "Starts": 531150,
    "Skips": 7936,
    "Complete Views": 6607,
    "CPM (R$)": 8.0,
    "Pacing (%)": 23.5,
    "Criativos Únicos": 1
  }
];

// Dados diários expandidos para mostrar mais dados
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
    "spend": 5762.93,
    "impressions": 1005138,
    "starts": 228509,
    "skips": 4258,
    "complete": 3175,
    "cpm": 5.73
  },
  {
    "date": "19/09/2025",
    "creative": "Video Institucional 90s",
    "spend": 5762.93,
    "impressions": 435594,
    "starts": 302641,
    "skips": 3678,
    "complete": 3432,
    "cpm": 13.23
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

// Dados brutos do YouTube
const YOUTUBE_RAW = {
  "creative": "Video Institucional 90s",
  "date": "2025/09/18-19",
  "starts": 531150,
  "skips": 7936,
  "first_quartile": 31204,
  "midpoint": 11029,
  "third_quartile": 7159,
  "complete_views": 6607,
  "impressions": 1440732,
  "spend": 11525.86,
  "cpm": 8.0,
  "cpm_calculated": 8.0,
  "start_rate": 36.87,
  "completion_rate": 1.24,
  "skip_rate": 1.49
};