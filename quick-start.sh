#!/bin/bash

# South Media IA Quick Start Script
# This script will install Node.js if missing and set up the project

echo "🚀 South Media IA Quick Start"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Homebrew is installed
check_homebrew() {
    if ! command -v brew &> /dev/null; then
        print_warning "Homebrew not found. Installing..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH for M1 Macs
        if [[ $(uname -m) == 'arm64' ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
    else
        print_status "Homebrew found"
    fi
}

# Check and install Node.js
check_nodejs() {
    if ! command -v node &> /dev/null; then
        print_warning "Node.js not found. Installing..."
        brew install node
        
        # Verify installation
        if command -v node &> /dev/null; then
            print_status "Node.js installed successfully"
            echo "Node.js version: $(node --version)"
            echo "npm version: $(npm --version)"
        else
            print_error "Failed to install Node.js"
            exit 1
        fi
    else
        print_status "Node.js found: $(node --version)"
    fi
}

# Check Python
check_python() {
    if command -v python3 &> /dev/null; then
        print_status "Python found: $(python3 --version)"
    else
        print_error "Python 3 not found. Please install Python 3.9+ first."
        exit 1
    fi
}

# Check Git
check_git() {
    if command -v git &> /dev/null; then
        print_status "Git found: $(git --version)"
    else
        print_warning "Git not found. Installing..."
        brew install git
    fi
}

# Main execution
echo "🔍 Checking prerequisites..."

check_homebrew
check_nodejs
check_python
check_git

print_status "All prerequisites are ready!"

# Ask user if they want to run the setup
echo ""
read -p "Do you want to run the project setup now? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Running project setup..."
    ./setup-project.sh
else
    print_info "You can run the setup later with: ./setup-project.sh"
fi

echo ""
print_status "Quick start completed!"
echo ""
echo "Next steps:"
echo "1. Run: ./setup-project.sh (if not done already)"
echo "2. Start frontend: cd frontend && npm start"
echo "3. Start backend: cd backend && source venv/bin/activate && uvicorn src.main:app --reload"
echo ""
echo "For more information, see:"
echo "- SETUP.md - Complete setup guide"
echo "- INSTALLATION.md - Installation instructions"
echo "- SECURITY.md - Security best practices"
