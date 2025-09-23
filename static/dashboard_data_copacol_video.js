
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
  "Budget Utilizado (R$)": 0.0,
  "Impress\u00f5es": 1440732,
  "Starts": 531150,
  "Skips": 7936,
  "Complete Views": 6607,
  "CPM (R$)": 8.0,
  "Pacing (%)": 0.0
};

const PER = [
  {
    "Canal": "YouTube",
    "Budget Contratado (R$)": 49009.9,
    "Budget Utilizado (R$)": 0.0,
    "Impress\u00f5es": 1440732,
    "Starts": 531150,
    "Skips": 7936,
    "Complete Views": 6607,
    "CPM (R$)": 8.0,
    "Pacing (%)": 0.0,
    "Criativos \u00danicos": 1
  }
];

// Dados diários
const DAILY = [
  {
    "date": "2025/09/18",
    "creative": "Unknown",
    "spend": 0.0,
    "impressions": 1005138,
    "starts": 228509,
    "skips": 4258,
    "complete": 3175,
    "cpm": 4.0
  },
  {
    "date": "2025/09/19",
    "creative": "Unknown",
    "spend": 0.0,
    "impressions": 435594,
    "starts": 302641,
    "skips": 3678,
    "complete": 3432,
    "cpm": 4.0
  }
];

// Dados brutos do YouTube
const YOUTUBE_RAW = {
  "creative": "Unknown",
  "date": "2025/09/18",
  "starts": 531150,
  "skips": 7936,
  "first_quartile": 31204,
  "midpoint": 11029,
  "third_quartile": 7159,
  "complete_views": 6607,
  "impressions": 1440732,
  "spend": 0.0,
  "cpm": 8.0,
  "cpm_calculated": 0.0,
  "start_rate": 36.866676106312624,
  "completion_rate": 1.2439047350089427,
  "skip_rate": 1.4941165395839218
};
