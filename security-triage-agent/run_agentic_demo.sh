#!/bin/bash
# Launch script for Agentic Security Operations Demo

echo "🤖 IHCL Agentic AI Security Operations Demo"
echo "==========================================="
echo ""
echo "Starting autonomous security incident response demonstration..."
echo ""

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update requirements
echo "Installing dependencies..."
pip install -r requirements.txt

# Set environment variables for demo
export OPENAI_API_KEY="demo-key-for-portfolio-showcase"
export DEMO_MODE="true"

echo ""
echo "🚀 Launching Agentic AI Demo Interface..."
echo "📱 Demo will open at: http://localhost:8501"
echo ""
echo "Features demonstrated:"
echo "✅ Autonomous decision-making and task execution"
echo "✅ Multi-tool integration across hotel systems"  
echo "✅ Real-time API calls and system integrations"
echo "✅ Business impact calculation and ROI tracking"
echo "✅ Human-in-the-loop escalation workflows"
echo ""

# Launch Streamlit demo
streamlit run demo_agentic_live.py --server.port 8501