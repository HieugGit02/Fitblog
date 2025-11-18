#!/bin/bash

# 🚀 Fitblog - Pre-Railway Deployment Setup Script
# Run this before deploying to Railway

set -e  # Exit if any command fails

echo "🔍 Fitblog Pre-Deployment Setup"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if in project directory
if [ ! -f "manage.py" ]; then
    echo -e "${RED}❌ Error: manage.py not found. Please run from project root directory${NC}"
    exit 1
fi

echo -e "${BLUE}📦 Step 1: Check Python Environment${NC}"
echo "---"

# Check Python version
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "Python version: $PYTHON_VERSION"

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${YELLOW}⚠️  Warning: Virtual environment not activated${NC}"
    echo "Run: source venv/bin/activate"
else
    echo -e "${GREEN}✅ Virtual environment active${NC}"
fi
echo ""

echo -e "${BLUE}📋 Step 2: Check Required Files${NC}"
echo "---"

FILES=(
    "manage.py"
    "Procfile"
    "Dockerfile"
    "runtime.txt"
    "requirements.txt"
    ".env.example"
    "fitblog_config/settings.py"
    "fitblog_config/wsgi.py"
)

for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file (MISSING)${NC}"
    fi
done
echo ""

echo -e "${BLUE}📦 Step 3: Check Dependencies${NC}"
echo "---"

# Check pip packages
echo "Checking installed packages..."
pip list | grep -E "Django|djangorestframework|gunicorn|psycopg2" > /dev/null && \
    echo -e "${GREEN}✅ Core packages installed${NC}" || \
    echo -e "${YELLOW}⚠️  Warning: Some packages may be missing${NC}"

# Show installed versions
echo ""
echo "Installed versions:"
python3 -c "import django; print(f'Django: {django.VERSION}')" 2>/dev/null || echo "Django: NOT INSTALLED"
python3 -c "import rest_framework; print(f'DRF: {rest_framework.VERSION}')" 2>/dev/null || echo "DRF: NOT INSTALLED"
python3 -c "import gunicorn; print(f'Gunicorn: {gunicorn.__version__}')" 2>/dev/null || echo "Gunicorn: NOT INSTALLED"

echo ""

echo -e "${BLUE}🗄️  Step 4: Database Status${NC}"
echo "---"

# Show migrations status
echo "Checking migrations..."
python3 manage.py showmigrations --plan 2>/dev/null | grep -E "^\[" | wc -l | xargs echo "Total migrations found:"

# Check for unapplied migrations
UNAPPLIED=$(python3 manage.py showmigrations --plan 2>/dev/null | grep "^\[ \]" | wc -l)
if [ "$UNAPPLIED" -eq 0 ]; then
    echo -e "${GREEN}✅ All migrations applied${NC}"
else
    echo -e "${YELLOW}⚠️  $UNAPPLIED unapplied migrations${NC}"
fi

echo ""

echo -e "${BLUE}🔐 Step 5: Environment Variables${NC}"
echo "---"

if [ -f ".env" ]; then
    echo -e "${GREEN}✅ .env file exists${NC}"
    # Show only non-sensitive vars
    grep "^DEBUG\|^SECRET_KEY\|^ALLOWED_HOSTS" .env 2>/dev/null | head -3 || echo "Check .env file manually"
else
    echo -e "${YELLOW}⚠️  .env file not found (will use .env.example as template)${NC}"
fi

if [ -f ".env.example" ]; then
    echo -e "${GREEN}✅ .env.example exists${NC}"
else
    echo -e "${RED}❌ .env.example not found${NC}"
fi

echo ""

echo -e "${BLUE}📁 Step 6: Static Files${NC}"
echo "---"

if [ -d "staticfiles" ]; then
    FILE_COUNT=$(find staticfiles -type f 2>/dev/null | wc -l)
    echo -e "${GREEN}✅ staticfiles directory exists with $FILE_COUNT files${NC}"
else
    echo -e "${YELLOW}⚠️  staticfiles directory doesn't exist (will be created during deployment)${NC}"
fi

echo ""

echo -e "${BLUE}🚀 Step 7: Pre-Deployment Checks${NC}"
echo "---"

echo "Running Django checks..."
python3 manage.py check --deploy 2>&1 | head -20

echo ""

echo -e "${BLUE}📊 Step 8: GitHub Status${NC}"
echo "---"

if command -v git &> /dev/null; then
    # Check if in git repo
    git rev-parse --git-dir > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        BRANCH=$(git rev-parse --abbrev-ref HEAD)
        STATUS=$(git status --porcelain)
        
        echo "Current branch: $BRANCH"
        
        if [ -z "$STATUS" ]; then
            echo -e "${GREEN}✅ Working directory clean${NC}"
        else
            echo -e "${YELLOW}⚠️  Uncommitted changes:${NC}"
            echo "$STATUS" | head -5
        fi
        
        # Check remote
        if git config --get remote.origin.url > /dev/null; then
            REMOTE=$(git config --get remote.origin.url)
            echo "Remote: $REMOTE"
        fi
    else
        echo -e "${RED}❌ Not a git repository${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  Git not installed${NC}"
fi

echo ""

echo -e "${GREEN}=================================="
echo "✅ Pre-Deployment Check Complete!"
echo "==================================${NC}"

echo ""
echo -e "${BLUE}📝 Next Steps:${NC}"
echo ""
echo "1️⃣  Fix any issues shown above"
echo ""
echo "2️⃣  Apply any pending migrations (if needed):"
echo "   python3 manage.py migrate"
echo ""
echo "3️⃣  Collect static files:"
echo "   python3 manage.py collectstatic --noinput"
echo ""
echo "4️⃣  Commit and push to GitHub:"
echo "   git add ."
echo "   git commit -m 'Prepare for Railway deployment'"
echo "   git push origin main"
echo ""
echo "5️⃣  Visit Railway (https://railway.app) and follow QUICK_START_RAILWAY.md"
echo ""

echo -e "${YELLOW}⚠️  Don't forget to set environment variables on Railway!${NC}"
echo "Required:"
echo "  - SECRET_KEY (generate using: python3 -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\")"
echo "  - DEBUG=False"
echo "  - ALLOWED_HOSTS=*.railway.app"
echo "  - NGROK_LLM_API (if using chatbot)"
echo "  - CORS_ALLOWED_ORIGINS (if using frontend)"
echo ""

