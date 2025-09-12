# South Media Dashboard - Static

Dashboard estático para South Media hospedado no Vercel.

## 📊 Dashboard

- **URL**: https://south-media-dashboard-static.vercel.app/
- **Framework**: HTML/CSS/JavaScript puro
- **Gráficos**: Chart.js
- **Dados**: Google Sheets (atualização automática)

## 🔧 Configuração

- **Build**: Arquivos estáticos (sem build necessário)
- **Deploy**: Automático via Vercel
- **Atualização**: Automática via Cloud Run (a cada 3h)

## 📁 Estrutura

```
vercel-static/
├── index.html          # Dashboard principal
├── static/             # Arquivos estáticos
│   ├── dash_sonho.html # Dashboard original
│   └── tsv/           # Dados TSV
├── package.json        # Configuração do projeto
├── vercel.json         # Configuração do Vercel
└── .vercelignore      # Arquivos ignorados
```

## 🚀 Deploy

1. Conecte o repositório ao Vercel
2. Configure:
   - Framework Preset: `Other`
   - Build Command: `echo "Static site"`
   - Output Directory: `.`
3. Deploy automático
