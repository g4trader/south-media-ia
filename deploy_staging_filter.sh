#!/bin/bash
# Deploy para staging com filtro de dashboards de teste

echo "🚀 Deploy para STAGING - Filtro de dashboards de teste"
echo ""

gcloud run deploy stg-gen-dashboard-ia \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars ENVIRONMENT=staging

echo ""
echo "✅ Deploy concluído!"
echo "🔗 URL: https://stg-gen-dashboard-ia-6f3ckz7c7q-uc.a.run.app/dashboards-list"
