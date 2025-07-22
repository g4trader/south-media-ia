#!/bin/bash
set -e

echo "🚀 Deploying South Media Backend..."

# Set project
export GOOGLE_APPLICATION_CREDENTIALS="/home/ubuntu/upload/automatizar-452311-b122eb2aa628.json"
export GOOGLE_CLOUD_PROJECT="automatizar-452311"

# Build and deploy using Cloud Build
cd backend
gcloud builds submit --config=cloudbuild.yaml --project=automatizar-452311

echo "✅ Deploy completed!"
