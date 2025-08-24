#!/bin/bash

# IHCL AI Product Manager Portfolio - Launch Script
# Professional deployment for interview demonstrations

echo "🚀 IHCL AI Product Manager Portfolio - Professional Launch"
echo "================================================================="

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to check if port is in use
check_port() {
    if lsof -ti:$1 > /dev/null; then
        echo -e "${YELLOW}Port $1 is already in use${NC}"
        return 1
    else
        return 0
    fi
}

echo -e "\n${BLUE}📋 Pre-flight Checks${NC}"
echo "=================================="

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js: ${NODE_VERSION}${NC}"
else
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ Python: ${PYTHON_VERSION}${NC}"
else
    echo -e "${RED}❌ Python3 not found. Please install Python 3.10+${NC}"
    exit 1
fi

# Check required ports
echo -e "\n${BLUE}🔍 Checking Port Availability${NC}"
echo "=================================="
PORTS=(3004 3005 3006 8000)
for PORT in "${PORTS[@]}"; do
    if check_port $PORT; then
        echo -e "${GREEN}✅ Port $PORT available${NC}"
    else
        echo -e "${YELLOW}⚠️  Port $PORT in use - existing service will be used${NC}"
    fi
done

echo -e "\n${BLUE}🏗️  Installing Dependencies${NC}"
echo "=================================="

# VirtualAgent Platform
if [ -d "virtualagent-platform-dashboard" ]; then
    echo -e "${BLUE}📦 VirtualAgent Platform dependencies...${NC}"
    cd virtualagent-platform-dashboard
    npm install --silent
    cd ..
    echo -e "${GREEN}✅ VirtualAgent Platform ready${NC}"
fi

# TelecomAssist Platform
if [ -d "telecom-ai-nextjs" ]; then
    echo -e "${BLUE}📦 TelecomAssist Platform dependencies...${NC}"
    cd telecom-ai-nextjs
    npm install --silent
    cd ..
    echo -e "${GREEN}✅ TelecomAssist Platform ready${NC}"
fi

# Security Operations Platform
if [ -d "security-operations-nextjs" ]; then
    echo -e "${BLUE}📦 Security Operations dependencies...${NC}"
    cd security-operations-nextjs
    npm install --silent
    cd ..
    echo -e "${GREEN}✅ Security Operations Platform ready${NC}"
fi

# Python Backend
if [ -d "my-telecom-ai-agent" ]; then
    echo -e "${BLUE}🐍 Python Backend dependencies...${NC}"
    cd my-telecom-ai-agent
    if [ ! -d "demo_venv" ]; then
        python3 -m venv demo_venv
    fi
    source demo_venv/bin/activate
    pip install -r requirements.txt --quiet
    deactivate
    cd ..
    echo -e "${GREEN}✅ Python Backend ready${NC}"
fi

echo -e "\n${BLUE}🚀 Launching All Platforms${NC}"
echo "=================================="

# Launch VirtualAgent Platform (Port 3004)
if [ -d "virtualagent-platform-dashboard" ]; then
    echo -e "${BLUE}🌟 Starting VirtualAgent Platform on http://localhost:3004${NC}"
    cd virtualagent-platform-dashboard
    npm run dev > /dev/null 2>&1 &
    VIRTUALAGENT_PID=$!
    cd ..
    sleep 3
fi

# Launch TelecomAssist Platform (Port 3005)
if [ -d "telecom-ai-nextjs" ]; then
    echo -e "${BLUE}📱 Starting TelecomAssist Platform on http://localhost:3005${NC}"
    cd telecom-ai-nextjs
    npm run dev -- --port 3005 > /dev/null 2>&1 &
    TELECOM_PID=$!
    cd ..
    sleep 3
fi

# Launch Security Operations (Port 3006)
if [ -d "security-operations-nextjs" ]; then
    echo -e "${BLUE}🛡️  Starting Security Operations on http://localhost:3006${NC}"
    cd security-operations-nextjs
    npm run dev -- --port 3006 > /dev/null 2>&1 &
    SECURITY_PID=$!
    cd ..
    sleep 3
fi

# Launch Python Backend (Port 8000)
if [ -d "my-telecom-ai-agent" ]; then
    echo -e "${BLUE}🔧 Starting Python Backend on http://localhost:8000${NC}"
    cd my-telecom-ai-agent
    source demo_venv/bin/activate
    python web_app.py > /dev/null 2>&1 &
    PYTHON_PID=$!
    deactivate
    cd ..
    sleep 5
fi

echo -e "\n${GREEN}🎉 IHCL AI Portfolio Successfully Launched!${NC}"
echo "================================================================="
echo -e "${BLUE}📊 Live Platform Access:${NC}"
echo ""
echo -e "${GREEN}🌟 VirtualAgent Dashboard:${NC}    http://localhost:3004"
echo -e "   ${YELLOW}→ Enterprise AI orchestration, Command Palette (⌘K)${NC}"
echo ""
echo -e "${GREEN}📱 TelecomAssist Platform:${NC}     http://localhost:3005"
echo -e "   ${YELLOW}→ 55+ language voice processing, Advanced UI${NC}"
echo ""
echo -e "${GREEN}🛡️  Security Operations:${NC}      http://localhost:3006"
echo -e "   ${YELLOW}→ Autonomous incident response, Real-time tracking${NC}"
echo ""
echo -e "${GREEN}🔧 Python Backend Services:${NC}   http://localhost:8000"
echo -e "   ${YELLOW}→ FastAPI, Multi-system integration${NC}"
echo ""
echo "================================================================="
echo -e "${BLUE}💼 Portfolio Status:${NC} ✅ Production Ready for Demonstrations"
echo -e "${BLUE}🎯 Focus:${NC} AI Product Management & Agentic System Architecture"
echo -e "${BLUE}📧 Contact:${NC} singhanand779@gmail.com"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Keep script running
trap 'echo -e "\n${YELLOW}🛑 Stopping all services...${NC}"; kill $VIRTUALAGENT_PID $TELECOM_PID $SECURITY_PID $PYTHON_PID 2>/dev/null; exit' INT

# Wait for user input
while true; do
    sleep 1
done