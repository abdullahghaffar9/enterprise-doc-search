#!/usr/bin/env bash
# Quick Setup & Test Script for AI Document Q&A System

set -e

echo "=========================================="
echo "AI Document Q&A System - Setup & Test"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Check Python
echo -e "${YELLOW}[1/5] Checking Python...${NC}"
if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python not found${NC}"
    exit 1
fi
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✅ Python ${PYTHON_VERSION}${NC}"
echo ""

# 2. Check Node.js
echo -e "${YELLOW}[2/5] Checking Node.js...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found${NC}"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✅ Node.js ${NODE_VERSION}${NC}"
echo ""

# 3. Check .env file
echo -e "${YELLOW}[3/5] Checking .env configuration...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo "   Creating .env from template..."
    cp .env.example .env 2>/dev/null || echo "   Please create .env file manually"
    echo -e "${YELLOW}   ⚠️  Update .env with your API keys:${NC}"
    echo "   - PINECONE_API_KEY"
    echo "   - GROQ_API_KEY"
    exit 1
fi

# Check required vars
REQUIRED_VARS=("PINECONE_API_KEY" "PINECONE_INDEX_NAME" "GROQ_API_KEY")
for var in "${REQUIRED_VARS[@]}"; do
    if ! grep -q "^${var}=" .env || grep "^${var}=$" .env > /dev/null; then
        echo -e "${YELLOW}⚠️  ${var} not configured in .env${NC}"
    fi
done
echo -e "${GREEN}✅ .env exists (verify API keys are populated)${NC}"
echo ""

# 4. Check dependencies
echo -e "${YELLOW}[4/5] Checking dependencies...${NC}"
echo "Backend requirements..."
if [ -d "backend" ] && [ -f "backend/requirements.txt" ]; then
    if [ ! -d ".venv" ]; then
        echo "   Creating virtual environment..."
        python -m venv .venv
        source .venv/bin/activate 2>/dev/null || . .venv/Scripts/activate
    fi
    echo "   Installing packages (this may take a minute)..."
    pip install -q -r backend/requirements.txt
    echo -e "${GREEN}   ✅ Backend dependencies ready${NC}"
fi

echo "Frontend dependencies..."
if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
    cd frontend
    if [ ! -d "node_modules" ]; then
        echo "   Installing packages (this may take a minute)..."
        npm install -q
    fi
    echo -e "${GREEN}   ✅ Frontend dependencies ready${NC}"
    cd ..
fi
echo ""

# 5. Show next steps
echo -e "${YELLOW}[5/5] Setup Complete!${NC}"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "1. Update .env with your API keys:"
echo "   - PINECONE_API_KEY: Get from https://pinecone.io/console"
echo "   - GROQ_API_KEY: Get from https://console.groq.com"
echo "   - PINECONE_INDEX_NAME: Your index from Pinecone"
echo ""
echo "2. Start the application:"
echo "   Option A (Combined): python start_app.py"
echo "   Option B (Separate terminals):"
echo "      Backend:  cd backend && python -m uvicorn app.main:app --reload --port 8000"
echo "      Frontend: cd frontend && npm run dev"
echo ""
echo "3. Open http://localhost:5173 in your browser"
echo ""
echo -e "${GREEN}Happy coding!${NC}"
