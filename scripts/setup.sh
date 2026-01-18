#!/bin/bash

# =============================================================================
# Student Study Planner - Monorepo Development Setup Script
# Uses: pnpm (Frontend) + uv (Backend/Django)
# =============================================================================

set -e  # Exit on error

echo "🚀 Setting up Student Study Planner Monorepo..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

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
check_command "pnpm" || {
    echo -e "  ${YELLOW}→${NC} Installing pnpm..."
    npm install -g pnpm
    check_command "pnpm" || MISSING_DEPS=1
}
check_command "python3" || MISSING_DEPS=1
check_command "uv" || {
    echo -e "  ${YELLOW}→${NC} Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    check_command "uv" || MISSING_DEPS=1
}
check_command "docker" || echo -e "  ${YELLOW}⚠${NC} docker not found (optional for local dev)"

if [ $MISSING_DEPS -eq 1 ]; then
    echo ""
    echo -e "${RED}Error: Missing required dependencies. Please install them first.${NC}"
    exit 1
fi

echo ""

# =============================================================================
# 2. Create Monorepo Directory Structure
# =============================================================================

echo "📁 Creating monorepo structure..."

# Create directories
mkdir -p apps/web/src/{app,components,lib,types}
mkdir -p apps/web/src/app/plan
mkdir -p apps/web/public
mkdir -p apps/api/config/settings
mkdir -p apps/api/apps/{planner,feedback}
mkdir -p apps/api/apps/planner/services
mkdir -p apps/api/core/{langchain,langsmith,firebase}
mkdir -p apps/api/tests
mkdir -p packages/shared-types/src
mkdir -p docs
mkdir -p scripts

echo -e "  ${GREEN}✓${NC} Directory structure created"
echo ""

# =============================================================================
# 3. Create pnpm Workspace Config
# =============================================================================

echo "📦 Setting up pnpm workspace..."

if [ ! -f "pnpm-workspace.yaml" ]; then
    cat > pnpm-workspace.yaml << 'EOF'
packages:
  - 'apps/*'
  - 'packages/*'
EOF
    echo -e "  ${GREEN}✓${NC} pnpm-workspace.yaml created"
fi

# Root package.json
if [ ! -f "package.json" ]; then
    cat > package.json << 'EOF'
{
  "name": "student-planner-monorepo",
  "private": true,
  "scripts": {
    "dev": "pnpm -r --parallel run dev",
    "dev:web": "pnpm --filter @student-planner/web dev",
    "dev:api": "cd apps/api && uv run python manage.py runserver",
    "build": "pnpm -r run build",
    "lint": "pnpm -r run lint",
    "clean": "pnpm -r exec rm -rf node_modules .next dist"
  },
  "devDependencies": {
    "turbo": "^2.0.0"
  }
}
EOF
    echo -e "  ${GREEN}✓${NC} Root package.json created"
fi

echo ""

# =============================================================================
# 4. Setup Frontend (Next.js with pnpm)
# =============================================================================

echo -e "${BLUE}🖥️  Setting up Frontend (Next.js + pnpm)...${NC}"

cd apps/web

if [ ! -f "package.json" ]; then
    cat > package.json << 'EOF'
{
  "name": "@student-planner/web",
  "version": "0.1.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "^14.2.0",
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
    echo -e "  ${GREEN}✓${NC} apps/web/package.json created"
fi

# Next.js config with CSP
if [ ! -f "next.config.js" ]; then
    cat > next.config.js << 'EOF'
/** @type {import('next').NextConfig} */
const nextConfig = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Content-Security-Policy',
            value: [
              "default-src 'self'",
              "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com",
              "style-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://fonts.googleapis.com",
              "font-src 'self' https://fonts.gstatic.com",
              "img-src 'self' data: https:",
              "frame-src 'self' blob:",
            ].join('; '),
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
EOF
    echo -e "  ${GREEN}✓${NC} next.config.js created"
fi

# Tailwind config
if [ ! -f "tailwind.config.js" ]; then
    cat > tailwind.config.js << 'EOF'
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOF
    echo -e "  ${GREEN}✓${NC} tailwind.config.js created"
fi

# TypeScript config
if [ ! -f "tsconfig.json" ]; then
    cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "es5",
    "lib": ["dom", "dom.iterable", "esnext"],
    "allowJs": true,
    "skipLibCheck": true,
    "strict": true,
    "noEmit": true,
    "esModuleInterop": true,
    "module": "esnext",
    "moduleResolution": "bundler",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "jsx": "preserve",
    "incremental": true,
    "plugins": [{"name": "next"}],
    "paths": {
      "@/*": ["./src/*"]
    }
  },
  "include": ["next-env.d.ts", "**/*.ts", "**/*.tsx", ".next/types/**/*.ts"],
  "exclude": ["node_modules"]
}
EOF
    echo -e "  ${GREEN}✓${NC} tsconfig.json created"
fi

cd "$PROJECT_ROOT"
echo ""

# =============================================================================
# 5. Setup Backend (Django with uv)
# =============================================================================

echo -e "${BLUE}🐍 Setting up Backend (Django + uv)...${NC}"

cd apps/api

# Initialize uv project
if [ ! -f "pyproject.toml" ]; then
    cat > pyproject.toml << 'EOF'
[project]
name = "student-planner-api"
version = "0.1.0"
description = "AI-powered Study Planner Backend"
readme = "README.md"
requires-python = ">=3.11"
dependencies = [
    # Django & REST
    "django>=5.0",
    "djangorestframework>=3.14.0",
    "django-cors-headers>=4.3.0",
    
    # LangChain Core
    "langchain>=0.1.0",
    "langchain-core>=0.1.0",
    "langchain-community>=0.0.10",
    
    # LLM Providers
    "langchain-google-genai>=1.0.0",
    "langchain-openai>=0.0.5",
    
    # LangSmith (Tracing + Prompt Hub)
    "langsmith>=0.1.0",
    
    # Firebase
    "firebase-admin>=6.3.0",
    
    # Async & HTTP
    "httpx>=0.26.0",
    "uvicorn>=0.27.0",
    
    # Utilities
    "python-dotenv>=1.0.0",
    "pydantic>=2.5.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.23.0",
    "pytest-django>=4.5.0",
    "black>=24.0.0",
    "ruff>=0.1.0",
]

[tool.uv]
dev-dependencies = [
    "pytest>=7.4.0",
    "pytest-django>=4.5.0",
    "black>=24.0.0",
    "ruff>=0.1.0",
]
EOF
    echo -e "  ${GREEN}✓${NC} pyproject.toml created"
fi

# Django manage.py
if [ ! -f "manage.py" ]; then
    cat > manage.py << 'EOF'
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
EOF
    chmod +x manage.py
    echo -e "  ${GREEN}✓${NC} manage.py created"
fi

# Django settings
if [ ! -f "config/__init__.py" ]; then
    touch config/__init__.py
fi

if [ ! -f "config/settings/__init__.py" ]; then
    touch config/settings/__init__.py
fi

if [ ! -f "config/settings/base.py" ]; then
    cat > config/settings/base.py << 'EOF'
"""
Django base settings for Student Planner API.
"""
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'dev-secret-key-change-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'true').lower() == 'true'

ALLOWED_HOSTS = os.getenv('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'rest_framework',
    'corsheaders',
    # Local apps
    'apps.planner',
    'apps.feedback',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database - Using Firestore, so minimal Django DB
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/minute',
        'generate': '10/minute',
        'regenerate': '5/minute',
    },
}

# CORS
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# LangSmith Settings
LANGCHAIN_TRACING_V2 = os.getenv('LANGCHAIN_TRACING_V2', 'true')
LANGCHAIN_PROJECT = os.getenv('LANGCHAIN_PROJECT', 'student-planner')
LANGSMITH_HUB_OWNER = os.getenv('LANGSMITH_HUB_OWNER', 'maisonhai3')

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = 'static/'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
EOF
    echo -e "  ${GREEN}✓${NC} config/settings/base.py created"
fi

if [ ! -f "config/settings/development.py" ]; then
    cat > config/settings/development.py << 'EOF'
"""Development settings."""
from .base import *

DEBUG = True

# Load .env file
from dotenv import load_dotenv
load_dotenv()
EOF
    echo -e "  ${GREEN}✓${NC} config/settings/development.py created"
fi

if [ ! -f "config/urls.py" ]; then
    cat > config/urls.py << 'EOF'
"""URL configuration for Student Planner API."""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('apps.planner.urls')),
    path('api/v1/', include('apps.feedback.urls')),
]
EOF
    echo -e "  ${GREEN}✓${NC} config/urls.py created"
fi

if [ ! -f "config/wsgi.py" ]; then
    cat > config/wsgi.py << 'EOF'
"""WSGI config for Student Planner API."""
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
application = get_wsgi_application()
EOF
    echo -e "  ${GREEN}✓${NC} config/wsgi.py created"
fi

# Create Django apps __init__.py files
touch apps/__init__.py
touch apps/planner/__init__.py
touch apps/planner/services/__init__.py
touch apps/feedback/__init__.py
touch core/__init__.py
touch core/langchain/__init__.py
touch core/langsmith/__init__.py
touch core/firebase/__init__.py

# Planner URLs
if [ ! -f "apps/planner/urls.py" ]; then
    cat > apps/planner/urls.py << 'EOF'
from django.urls import path
from .views import GeneratePlanView, PlanDetailView, HealthCheckView

urlpatterns = [
    path('generate/', GeneratePlanView.as_view(), name='generate-plan'),
    path('plans/<str:plan_id>/', PlanDetailView.as_view(), name='plan-detail'),
    path('health/', HealthCheckView.as_view(), name='health-check'),
]
EOF
    echo -e "  ${GREEN}✓${NC} apps/planner/urls.py created"
fi

# Placeholder views
if [ ! -f "apps/planner/views.py" ]; then
    cat > apps/planner/views.py << 'EOF'
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class GeneratePlanView(APIView):
    def post(self, request):
        # TODO: Implement with LangChain
        return Response({
            'success': True,
            'data': {
                'plan_id': 'placeholder',
                'message': 'Generation endpoint - To be implemented'
            }
        })

class PlanDetailView(APIView):
    def get(self, request, plan_id):
        return Response({
            'success': True,
            'data': {'plan_id': plan_id, 'message': 'Plan detail endpoint'}
        })

class HealthCheckView(APIView):
    def get(self, request):
        return Response({
            'status': 'healthy',
            'version': '2.0.0',
            'framework': 'Django REST Framework'
        })
EOF
    echo -e "  ${GREEN}✓${NC} apps/planner/views.py created"
fi

# Feedback URLs
if [ ! -f "apps/feedback/urls.py" ]; then
    cat > apps/feedback/urls.py << 'EOF'
from django.urls import path
from .views import FeedbackView

urlpatterns = [
    path('feedback/', FeedbackView.as_view(), name='feedback'),
]
EOF
fi

if [ ! -f "apps/feedback/views.py" ]; then
    cat > apps/feedback/views.py << 'EOF'
from rest_framework.views import APIView
from rest_framework.response import Response

class FeedbackView(APIView):
    def post(self, request):
        # TODO: Implement feedback tracking
        return Response({
            'success': True,
            'message': 'Feedback recorded'
        })
EOF
fi

# Install dependencies with uv
echo "  Installing Python dependencies with uv..."
uv sync --quiet 2>/dev/null || uv sync

echo -e "  ${GREEN}✓${NC} Python dependencies installed"

cd "$PROJECT_ROOT"
echo ""

# =============================================================================
# 6. Create Environment Files
# =============================================================================

echo "🔐 Creating environment files..."

# Frontend .env.local
if [ ! -f "apps/web/.env.local" ]; then
    cat > apps/web/.env.local << 'EOF'
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Firebase (fill these in)
NEXT_PUBLIC_FIREBASE_API_KEY=
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=
NEXT_PUBLIC_FIREBASE_PROJECT_ID=
EOF
    echo -e "  ${GREEN}✓${NC} apps/web/.env.local created"
fi

# Backend .env
if [ ! -f "apps/api/.env" ]; then
    cat > apps/api/.env << 'EOF'
# =============================================================================
# Django Settings
# =============================================================================
DJANGO_SECRET_KEY=your-secret-key-here-change-in-production
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# =============================================================================
# AI API Keys - FILL THESE IN
# =============================================================================

# Google Gemini (get from https://aistudio.google.com/app/apikey)
GOOGLE_API_KEY=

# OpenAI (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=

# =============================================================================
# LangSmith (Tracing + Prompt Hub)
# =============================================================================
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=student-planner
LANGSMITH_API_KEY=
LANGSMITH_HUB_OWNER=maisonhai3

# =============================================================================
# Firebase
# =============================================================================
FIREBASE_PROJECT_ID=
GOOGLE_APPLICATION_CREDENTIALS=./firebase-credentials.json

# =============================================================================
# Redis (Optional - for caching)
# =============================================================================
REDIS_URL=redis://localhost:6379
EOF
    echo -e "  ${GREEN}✓${NC} apps/api/.env created"
fi

echo ""

# =============================================================================
# 7. Create Docker Compose
# =============================================================================

echo "🐳 Creating Docker Compose configuration..."

if [ ! -f "docker-compose.yml" ]; then
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  web:
    build:
      context: ./apps/web
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://api:8000
    depends_on:
      - api
    volumes:
      - ./apps/web:/app
      - /app/node_modules
      - /app/.next

  api:
    build:
      context: ./apps/api
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file:
      - ./apps/api/.env
    volumes:
      - ./apps/api:/app
    depends_on:
      - redis
    command: uv run python manage.py runserver 0.0.0.0:8000

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
fi

echo ""

# =============================================================================
# 8. Create .gitignore
# =============================================================================

echo "📝 Updating .gitignore..."

cat > .gitignore << 'EOF'
# Dependencies
node_modules/
.pnpm-store/
__pycache__/
*.pyc
.venv/

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

# Django
db.sqlite3
staticfiles/

# uv
.uv/

# Misc
*.bak
*.tmp
EOF

echo -e "  ${GREEN}✓${NC} .gitignore updated"
echo ""

# =============================================================================
# 9. Install Frontend Dependencies
# =============================================================================

echo "📦 Installing frontend dependencies with pnpm..."

cd "$PROJECT_ROOT"
pnpm install --filter @student-planner/web 2>/dev/null || pnpm install

echo -e "  ${GREEN}✓${NC} Frontend dependencies installed"
echo ""

# =============================================================================
# 10. Summary
# =============================================================================

echo "============================================================================="
echo -e "${GREEN}✅ Monorepo Setup Complete!${NC}"
echo "============================================================================="
echo ""
echo "📁 Project Structure:"
echo "   apps/web/     - Next.js frontend (pnpm)"
echo "   apps/api/     - Django REST backend (uv)"
echo "   packages/     - Shared packages"
echo "   docs/         - Documentation"
echo ""
echo "🔑 Next Steps:"
echo ""
echo "   1. Fill in API keys in:"
echo "      - apps/api/.env (GOOGLE_API_KEY, OPENAI_API_KEY, LANGSMITH_API_KEY)"
echo "      - apps/web/.env.local (Firebase config)"
echo ""
echo "   2. Start development servers:"
echo ""
echo "      ${BLUE}# Terminal 1 - Backend (Django)${NC}"
echo "      cd apps/api && uv run python manage.py runserver"
echo ""
echo "      ${BLUE}# Terminal 2 - Frontend (Next.js)${NC}"
echo "      cd apps/web && pnpm dev"
echo ""
echo "   3. Or start both with:"
echo "      pnpm dev"
echo ""
echo "   4. Or use Docker:"
echo "      docker-compose up"
echo ""
echo "   5. Open http://localhost:3000 in your browser"
echo ""
echo "============================================================================="
echo "📚 Documentation: docs/IMPLEMENTATION_PLAN.md"
echo "🔗 LangSmith Hub: https://smith.langchain.com/hub/maisonhai3"
echo "============================================================================="
