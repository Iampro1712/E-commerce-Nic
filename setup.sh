#!/bin/bash

# E-commerce API Setup Script
echo "🚀 Setting up E-commerce API..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

echo "✅ Python $(python3 --version) found"

# Install pip if not available
if ! python3 -m pip --version &> /dev/null; then
    echo "📦 Installing pip..."
    sudo apt update
    sudo apt install -y python3-pip python3-venv
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "📝 Please edit .env file with your configuration"
fi

# Create uploads directory
mkdir -p uploads

echo "✅ Setup completed!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your database and Adyen configuration"
echo "2. Create MySQL database: CREATE DATABASE ecommerce_db;"
echo "3. Run: source venv/bin/activate"
echo "4. Run: python init_db.py"
echo "5. Run: python app.py"
echo ""
echo "For testing:"
echo "- Run: python run_tests.py"
echo ""
echo "API will be available at: http://localhost:5000"
