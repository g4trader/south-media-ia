#!/bin/bash

# Script para build e deploy no Cloud Run
# Execute este script no Cloud Shell

echo "🚀 Iniciando build e deploy..."

# Build da imagem
echo "📦 Fazendo build da imagem..."
gcloud builds submit --tag gcr.io/automatizar-452311/dashboard-builder:latest

# Deploy no Cloud Run
echo "🚀 Fazendo deploy no Cloud Run..."
gcloud run deploy dashboard-builder \
  --image gcr.io/automatizar-452311/dashboard-builder:latest \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated

echo "✅ Deploy concluído!"
