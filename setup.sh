#!/bin/bash

# Setup script for Agent Framework + CopilotKit Demo
# This script sets up both backend and frontend

set -e  # Exit on error

echo "🚀 Setting up Agent Framework + CopilotKit Demo"
echo "=============================================="
echo ""

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
required_version="3.12"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "❌ Python 3.12+ is required. Found: $python_version"
    exit 1
fi
echo "✅ Python $python_version found"
echo ""

# Check Node.js version
echo "📋 Checking Node.js version..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+"
    exit 1
fi
node_version=$(node --version | cut -d. -f1 | sed 's/v//')
if [ "$node_version" -lt 18 ]; then
    echo "❌ Node.js 18+ is required. Found: v$node_version"
    exit 1
fi
echo "✅ Node.js $(node --version) found"
echo ""

# Backend Setup
echo "🐍 Setting up Python backend..."
cd backend

pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env and add your API keys!"
else
    echo ".env file already exists"
fi

cd ..
echo "✅ Backend setup complete!"
echo ""

# Frontend Setup
echo "⚛️  Setting up Next.js frontend..."
cd frontend

echo "Installing Node.js dependencies..."
npm install --force

if [ ! -f ".env.local" ]; then
    echo "Creating .env.local file from template..."
    cp .env.example .env.local
else
    echo ".env.local file already exists"
fi

cd ..
echo "✅ Frontend setup complete!"
echo ""

# Summary
echo "=============================================="
echo "✨ Setup Complete!"
echo "=============================================="
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Configure your API keys:"
echo "   - Edit backend/.env and add OPENAI_API_KEY or Azure credentials"
echo ""
echo "2. Start the backend:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "3. In a new terminal, start the frontend:"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "4. Open your browser:"
echo "   http://localhost:3000"
echo ""
echo "🎉 Happy coding!"
