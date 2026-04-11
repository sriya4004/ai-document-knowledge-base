#!/bin/bash

# ============================================
# AI-Powered Document Knowledge Base - Quick Start
# ============================================

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo -e "${BLUE}========================================"
echo "AI Document Knowledge Base - Setup"
echo "========================================${NC}"
echo ""

# Check Python
echo -e "${BLUE}[1/5] Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi
python3 --version
echo -e "${GREEN}✓ Python installed${NC}"

# Setup backend
echo ""
echo -e "${BLUE}[2/5] Setting up backend virtual environment...${NC}"
cd backend
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

source .venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

echo ""
echo -e "${BLUE}[3/5] Installing backend dependencies...${NC}"
pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt
echo -e "${GREEN}✓ Backend dependencies installed${NC}"

cd ..

# Check Node.js
echo ""
echo -e "${BLUE}[4/5] Checking Node.js installation...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${YELLOW}WARNING: Node.js not found. Frontend setup skipped.${NC}"
    echo -e "${YELLOW}Install Node.js from https://nodejs.org${NC}"
else
    node --version
    echo -e "${GREEN}✓ Node.js installed${NC}"
    
    echo ""
    echo -e "${BLUE}[5/5] Installing frontend dependencies...${NC}"
    cd frontend
    npm install --quiet
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}"
    cd ..
fi

echo ""
echo -e "${GREEN}========================================"
echo "✓ Setup complete!"
echo "========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo ""
echo "  1. Backend (Terminal 1):"
echo "     cd backend"
echo "     source .venv/bin/activate"
echo "     uvicorn app.main:app --reload"
echo ""
echo "  2. Frontend (Terminal 2):"
echo "     cd frontend"
echo "     npm run dev"
echo ""
echo "  3. Open browser and visit: http://localhost:5173"
echo ""
echo "  4. Login with:"
echo "     Email: admin@company.com"
echo "     Password: admin123"
echo ""
echo -e "${BLUE}Documentation: See SETUP_GUIDE.md for detailed instructions${NC}"
echo ""
