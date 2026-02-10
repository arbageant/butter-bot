#!/bin/bash
# Setup script for Butter & Crumble Bot

set -e

echo "🔧 Setting up Butter & Crumble Bot..."

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install it first."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Install python3-venv if not available
echo "📦 Installing python3-venv..."
sudo apt update
sudo apt install -y python3.12-venv python3-pip

# Create virtual environment
echo "🌐 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright Chromium browser..."
playwright install chromium

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Activate the virtual environment: source venv/bin/activate"
echo "3. Run the bot: python main.py"
echo "4. Run tests: pytest"
echo ""
