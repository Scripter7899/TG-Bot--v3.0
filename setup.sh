#!/bin/bash

echo "========================================"
echo "FULL-TG v3.0 - Quick Setup Script"
echo "========================================"
echo ""

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.13.3 from https://www.python.org/"
    exit 1
fi

echo "[1/4] Python found"
python3 --version

echo ""
echo "[2/4] Installing dependencies..."
pip3 install -r requirements.txt

echo ""
echo "[3/4] Setting up configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from template"
    echo ""
    echo "IMPORTANT: Please edit .env file and add your Telegram API credentials"
    echo "Get them from: https://my.telegram.org"
else
    echo ".env file already exists"
fi

echo ""
echo "[4/4] Creating directories..."
mkdir -p sessions logs data/exports data/backups

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file and add your API_ID and API_HASH"
echo "2. Run: python3 main.py"
echo ""
echo "For help, check README.md"
echo ""
