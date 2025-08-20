#!/usr/bin/env python3
"""
Quick start script for Hotel Operations Assistant demo.
Provides easy way to run the system for demonstration purposes.
"""

import os
import sys
import asyncio
import subprocess
from pathlib import Path

def check_requirements():
    """Check if required dependencies are available."""
    try:
        import fastapi
        import uvicorn
        import langchain
        import pydantic
        print("✅ All required dependencies found")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def setup_environment():
    """Set up environment variables for demo."""
    env_vars = {
        "ENVIRONMENT": "development",
        "DEBUG": "true",
        "LOG_LEVEL": "INFO",
        "API_HOST": "0.0.0.0",
        "API_PORT": "8000",
        "SECRET_KEY": "demo-secret-key-not-for-production",
        "ENABLE_PII_PROTECTION": "true",
        "ENABLE_AUDIT_LOGGING": "true",
        "HOTEL_TYPE": "luxury",
        "HOTEL_BRAND": "IHCL",
        # Mock database and Redis for demo
        "DATABASE_URL": "sqlite:///./demo.db",
        "REDIS_URL": "redis://localhost:6379/0",
        # Mock API keys for demo
        "OPENAI_API_KEY": "demo-key-replace-for-actual-llm",
        "ANTHROPIC_API_KEY": "demo-key-replace-for-actual-llm"
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
    
    print("✅ Environment configured for demo")

def print_banner():
    """Print welcome banner."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        🏨 Hotel Operations Assistant - IHCL Portfolio        ║
║                                                              ║
║    AI-Powered Hotel Operations Management System             ║
║    Built for FlexiCore Platform Demonstration               ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

🚀 Starting comprehensive hotel operations AI system...

Key Features:
• Guest Service Agent - Room service, amenities, general inquiries
• Complaint Handler - Service recovery and compensation
• Security Agent - Safety incidents and access control  
• Fraud Detection - Payment monitoring and risk assessment
• Compliance Management - DPDP Act 2023, GDPR, PCI DSS
• Real-time Analytics - Performance monitoring and reporting

🔧 System Configuration:
• Environment: Development/Demo Mode
• Hotel Type: Luxury (IHCL Configuration)
• PII Protection: Enabled
• Audit Logging: Enabled
• API Documentation: Available at /docs
"""
    print(banner)

def print_demo_info():
    """Print demo usage information."""
    info = """
📊 Demo Endpoints Available:

🏠 Health & Status:
   GET  http://localhost:8000/health
   GET  http://localhost:8000/

💬 Chat Interface:
   POST http://localhost:8000/chat
   
   Example Request:
   {
     "message": "I need help with room service",
     "guest_id": "DEMO001",
     "room_number": "1205",
     "priority": "medium"
   }

🛡️ Compliance:
   POST http://localhost:8000/compliance/check
   GET  http://localhost:8000/compliance/dashboard

📋 Audit & Analytics:
   GET  http://localhost:8000/audit/events
   GET  http://localhost:8000/audit/statistics

🎭 Demo Scenarios:
   GET  http://localhost:8000/demo/scenarios

📚 Full API Documentation:
   http://localhost:8000/docs (Interactive Swagger UI)
   http://localhost:8000/redoc (ReDoc format)

🧪 Test Scenarios:

1. Guest Service Request:
   "I'd like to order dinner to my room. Do you have vegetarian options?"

2. Complaint Handling:
   "My room hasn't been cleaned and I'm very disappointed with the service."

3. Security Issue:
   "I can't access my room, my key card isn't working."

4. Fraud Detection:
   "Multiple credit cards used by same guest in short timeframe."

💡 Pro Tips:
• Use different guest_id values to simulate different guests
• Set priority to "urgent" or "high" to see escalation behavior
• Include context_data with vip_status: true for VIP guest handling
• Check /health endpoint to monitor system status
"""
    print(info)

async def run_health_check():
    """Run a quick health check to verify system is working."""
    try:
        import httpx
        
        print("🔍 Running system health check...")
        
        async with httpx.AsyncClient() as client:
            # Wait a moment for server to start
            await asyncio.sleep(2)
            
            try:
                response = await client.get("http://localhost:8000/health", timeout=10.0)
                if response.status_code == 200:
                    print("✅ System health check passed")
                    print("✅ All services operational")
                    return True
                else:
                    print(f"⚠️  Health check returned status {response.status_code}")
            except Exception as e:
                print(f"⚠️  Health check failed: {e}")
                print("   System may still be starting up...")
                
    except ImportError:
        print("ℹ️  httpx not available for health check")
    
    return False

def main():
    """Main demo runner."""
    print_banner()
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Print demo information
    print_demo_info()
    
    print("🚀 Starting Hotel Operations Assistant...")
    print("   Press Ctrl+C to stop the server")
    print("   Server will be available at: http://localhost:8000")
    print("   API Documentation at: http://localhost:8000/docs")
    print("\n" + "="*60 + "\n")
    
    try:
        # Start the FastAPI server
        import uvicorn
        from hotel_ops_assistant.api.main import create_app
        
        # Run health check in background
        def run_health_check_sync():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(run_health_check())
            loop.close()
        
        import threading
        health_thread = threading.Thread(target=run_health_check_sync)
        health_thread.daemon = True
        health_thread.start()
        
        # Start the server
        uvicorn.run(
            create_app(),
            host="0.0.0.0",
            port=8000,
            log_level="info",
            access_log=True
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down Hotel Operations Assistant...")
        print("   Thank you for trying the demo!")
    except Exception as e:
        print(f"\n❌ Error starting server: {e}")
        print("   Please check the error message above and try again.")
        sys.exit(1)

if __name__ == "__main__":
    main()