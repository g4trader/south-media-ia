#!/bin/bash

# South Media IA Frontend Deployment Script
# This script uses the Vercel token to deploy the frontend

echo "🚀 Starting South Media IA Frontend Deployment..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Set Vercel token
export VERCEL_TOKEN="5w8zipRxMJnLEET9OMESteB7"

# Build the project
echo "📦 Building the project..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

# Deploy to Vercel
echo "🌐 Deploying to Vercel..."
vercel --prod --token $VERCEL_TOKEN

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo "🌍 Your app is now live at: https://south-media-ia.vercel.app"
else
    echo "❌ Deployment failed!"
    exit 1
fi
