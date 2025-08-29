#!/bin/bash

# South Media IA Project Setup Script
# This script sets up the project with the provided credentials

echo "🚀 Setting up South Media IA Project..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm first."
    exit 1
fi

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.9+ first."
    exit 1
fi

print_status "Prerequisites check passed"

# Setup Frontend
echo "📦 Setting up Frontend..."
cd frontend

# Install dependencies
print_status "Installing frontend dependencies..."
npm install

if [ $? -ne 0 ]; then
    print_error "Failed to install frontend dependencies"
    exit 1
fi

# Setup Backend
echo "🐍 Setting up Backend..."
cd ../backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies
print_status "Installing backend dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    print_error "Failed to install backend dependencies"
    exit 1
fi

# Create environment file for backend
print_status "Creating backend environment configuration..."
cat > .env << EOF
# Backend Environment Variables
SECRET_KEY=south-media-secret-key-2024
GOOGLE_CLOUD_PROJECT=automatizar-452311
BIGQUERY_DATASET=south_media_dashboard
FLASK_ENV=development
PORT=8080
EOF

# Setup GitHub repository secrets (instructions)
echo ""
print_warning "To complete the setup, you need to add the following secrets to your GitHub repository:"
echo ""
echo "1. Go to your GitHub repository settings"
echo "2. Navigate to Secrets and variables > Actions"
echo "3. Add the following secrets:"
echo ""
echo "   VERCEL_TOKEN: 5w8zipRxMJnLEET9OMESteB7"
echo "   VERCEL_ORG_ID: (Get this from your Vercel dashboard)"
echo "   VERCEL_PROJECT_ID: (Get this from your Vercel dashboard)"
echo "   GITHUB_TOKEN: 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"
echo ""

# Instructions for running the project
echo "🎯 Project Setup Complete!"
echo ""
echo "To run the project:"
echo ""
echo "Frontend (in one terminal):"
echo "  cd frontend"
echo "  npm start"
echo ""
echo "Backend (in another terminal):"
echo "  cd backend"
echo "  source venv/bin/activate"
echo "  uvicorn src.main:app --reload"
echo ""
echo "To deploy to Vercel:"
echo "  cd frontend"
echo "  ./deploy.sh"
echo ""
print_status "Setup completed successfully!"
