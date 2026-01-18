#!/bin/bash

# =============================================================================
# Student Study Planner - Development Setup Script
# =============================================================================

set -e  # Exit on error

echo "🚀 Setting up Student Study Planner development environment..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# =============================================================================
# 1. Check Prerequisites
# =============================================================================

echo "📋 Checking prerequisites..."

check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "  ${GREEN}✓${NC} $1 is installed"
        return 0
    else
        echo -e "  ${RED}✗${NC} $1 is NOT installed"
        return 1
    fi
}

MISSING_DEPS=0

check_command "node" || MISSING_DEPS=1
check_command "npm" || MISSING_DEPS=1
check_command "python3" || MISSING_DEPS=1
check_command "pip3" || MISSING_DEPS=1
check_command "docker" || echo -e "  ${YELLOW}⚠${NC} docker not found (optional for local dev)"

if [ $MISSING_DEPS -eq 1 ]; then
    echo ""
    echo -e "${RED}Error: Missing required dependencies. Please install them first.${NC}"
    exit 1
fi

echo ""

# =============================================================================
# 2. Create Directory Structure
# =============================================================================

echo "📁 Creating directory structure..."

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Create directories
mkdir -p frontend/src/{app,components,lib,types}
mkdir -p frontend/src/app/api
mkdir -p frontend/src/app/plan
mkdir -p frontend/public
mkdir -p backend/app/{routers,chains,prompts,schemas,utils}
mkdir -p backend/tests
mkdir -p docs
mkdir -p scripts

echo -e "  ${GREEN}✓${NC} Directory structure created"
echo ""

# =============================================================================
# 3. Setup Frontend (Next.js)
# =============================================================================

echo "🖥️  Setting up Frontend (Next.js + Tailwind)..."

if [ ! -f "frontend/package.json" ]; then
    cd frontend
    
    # Initialize package.json
    cat > package.json << 'EOF'
{
  "name": "student-planner-frontend",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "autoprefixer": "^10.4.0",
    "eslint": "^8.0.0",
    "eslint-config-next": "^14.0.0",
    "postcss": "^8.4.0",
    "tailwindcss": "^3.4.0",
    "typescript": "^5.0.0"
  }
}
EOF

    echo -e "  ${GREEN}✓${NC} package.json created"
    
    # Install dependencies
    echo "  Installing npm dependencies (this may take a while)..."
    npm install --silent 2>/dev/null || npm install
    
    echo -e "  ${GREEN}✓${NC} npm dependencies installed"
    
    cd ..
else
    echo -e "  ${YELLOW}⚠${NC} Frontend already initialized, skipping..."
fi

echo ""

# =============================================================================
# 4. Setup Backend (Python + FastAPI + LangChain)
# =============================================================================

echo "🐍 Setting up Backend (Python + FastAPI + LangChain)..."

cd backend

if [ ! -f "requirements.txt" ]; then
    cat > requirements.txt << 'EOF'
# Web Framework
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
python-multipart>=0.0.6

# LangChain Core
langchain>=0.1.0
langchain-core>=0.1.0
langchain-community>=0.0.10

# LLM Providers
langchain-google-genai>=0.0.6
langchain-openai>=0.0.5

# Observability
langsmith>=0.0.77

# Database
firebase-admin>=6.3.0
# google-cloud-firestore>=2.14.0

# Utilities
python-dotenv>=1.0.0
pydantic>=2.5.0
httpx>=0.26.0

# Caching (optional)
redis>=5.0.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.23.0
EOF

    echo -e "  ${GREEN}✓${NC} requirements.txt created"
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "  Creating Python virtual environment..."
    python3 -m venv venv
    echo -e "  ${GREEN}✓${NC} Virtual environment created"
fi

# Activate and install
echo "  Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet 2>/dev/null || pip install -r requirements.txt

echo -e "  ${GREEN}✓${NC} Python dependencies installed"

cd ..
echo ""

# =============================================================================
# 5. Create Environment Files
# =============================================================================

echo "🔐 Creating environment files..."

# Frontend .env.local
if [ ! -f "frontend/.env.local" ]; then
    cat > frontend/.env.local << 'EOF'
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Firebase (fill these in)
NEXT_PUBLIC_FIREBASE_API_KEY=
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=
NEXT_PUBLIC_FIREBASE_PROJECT_ID=
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=
NEXT_PUBLIC_FIREBASE_APP_ID=
EOF
    echo -e "  ${GREEN}✓${NC} frontend/.env.local created"
else
    echo -e "  ${YELLOW}⚠${NC} frontend/.env.local already exists, skipping..."
fi

# Backend .env
if [ ! -f "backend/.env" ]; then
    cat > backend/.env << 'EOF'
# =============================================================================
# API Keys - FILL THESE IN
# =============================================================================

# Google Gemini (get from https://aistudio.google.com/app/apikey)
GOOGLE_API_KEY=

# OpenAI (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=

# =============================================================================
# LangSmith (Optional but recommended)
# =============================================================================
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=student-planner-dev
LANGSMITH_API_KEY=

# =============================================================================
# Firebase
# =============================================================================
FIREBASE_PROJECT_ID=
GOOGLE_APPLICATION_CREDENTIALS=./firebase-credentials.json

# =============================================================================
# Server Config
# =============================================================================
HOST=0.0.0.0
PORT=8000
DEBUG=true
CORS_ORIGINS=http://localhost:3000

# =============================================================================
# Redis (Optional - for caching)
# =============================================================================
REDIS_URL=redis://localhost:6379
EOF
    echo -e "  ${GREEN}✓${NC} backend/.env created"
else
    echo -e "  ${YELLOW}⚠${NC} backend/.env already exists, skipping..."
fi

echo ""

# =============================================================================
# 6. Create Docker Compose (Optional)
# =============================================================================

echo "🐳 Creating Docker Compose configuration..."

if [ ! -f "docker-compose.yml" ]; then
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
      - /app/.next

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    volumes:
      - ./backend:/app
    depends_on:
      - redis

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  redis_data:
EOF
    echo -e "  ${GREEN}✓${NC} docker-compose.yml created"
else
    echo -e "  ${YELLOW}⚠${NC} docker-compose.yml already exists, skipping..."
fi

echo ""

# =============================================================================
# 7. Create .gitignore
# =============================================================================

echo "📝 Creating .gitignore..."

if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'EOF'
# Dependencies
node_modules/
venv/
__pycache__/
*.pyc

# Environment files
.env
.env.local
.env*.local
firebase-credentials.json
*.pem

# Build outputs
.next/
dist/
build/
*.egg-info/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Testing
.coverage
htmlcov/
.pytest_cache/

# Misc
*.bak
*.tmp
EOF
    echo -e "  ${GREEN}✓${NC} .gitignore created"
else
    echo -e "  ${YELLOW}⚠${NC} .gitignore already exists, skipping..."
fi

echo ""

# =============================================================================
# 8. Summary
# =============================================================================

echo "============================================================================="
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "============================================================================="
echo ""
echo "📁 Project Structure:"
echo "   frontend/    - Next.js application"
echo "   backend/     - Python FastAPI + LangChain"
echo "   docs/        - Documentation"
echo ""
echo "🔑 Next Steps:"
echo ""
echo "   1. Fill in API keys in:"
echo "      - backend/.env (GOOGLE_API_KEY, OPENAI_API_KEY)"
echo "      - frontend/.env.local (Firebase config)"
echo ""
echo "   2. Start development servers:"
echo ""
echo "      # Terminal 1 - Backend"
echo "      cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
echo ""
echo "      # Terminal 2 - Frontend"
echo "      cd frontend && npm run dev"
echo ""
echo "   3. Or use Docker:"
echo "      docker-compose up"
echo ""
echo "   4. Open http://localhost:3000 in your browser"
echo ""
echo "============================================================================="
echo "📚 Documentation: docs/IMPLEMENTATION_PLAN.md"
echo "============================================================================="
