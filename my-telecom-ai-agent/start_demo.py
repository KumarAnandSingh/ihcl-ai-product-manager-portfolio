#!/usr/bin/env python3
"""
Quick Start Script for My Telecom AI Agent Web Demo

This script launches the web-based MVP demo for interview presentations.
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path


def check_dependencies():
    """Check if required packages are installed"""
    venv_path = Path(__file__).parent / "demo_venv"
    
    if not venv_path.exists():
        print("📦 Creating virtual environment...")
        subprocess.check_call([sys.executable, "-m", "venv", str(venv_path)])
        
        # Determine the correct python executable path
        if sys.platform == "win32":
            python_exe = venv_path / "Scripts" / "python.exe"
        else:
            python_exe = venv_path / "bin" / "python"
        
        print("📦 Installing required packages...")
        subprocess.check_call([str(python_exe), "-m", "pip", "install", "fastapi", "uvicorn"])
        print("✅ Virtual environment created and packages installed!")
    
    return venv_path


def start_demo():
    """Start the web demo"""
    print("\n" + "="*80)
    print("🚀 MY TELECOM AI AGENT - WEB DEMO STARTUP")
    print("="*80)
    print("📱 Production-scale customer service AI demonstration")
    print("🎯 Built for IHCL AI Product Manager interview")
    print("🌐 Based on real experience managing systems with millions of users")
    print("="*80)
    
    # Check dependencies and get venv path
    venv_path = check_dependencies()
    
    print("\n📋 Demo Features:")
    print("   ✅ Multi-language support (English, Hindi, Tamil, Telugu)")
    print("   ✅ Real-time tool integration (recharge, billing, support)")
    print("   ✅ Confidence-based decision making with metrics")
    print("   ✅ Production-grade performance monitoring")
    print("   ✅ Interactive web interface for live demonstration")
    
    print("\n🔄 Starting web server...")
    
    try:
        # Start the web application using virtual environment
        current_dir = Path(__file__).parent
        web_app_path = current_dir / "web_app.py"
        
        # Determine the correct python executable path
        if sys.platform == "win32":
            python_exe = venv_path / "Scripts" / "python.exe"
        else:
            python_exe = venv_path / "bin" / "python"
        
        # Launch the app with virtual environment python
        process = subprocess.Popen([
            str(python_exe), str(web_app_path)
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        print("✅ Web server started successfully!")
        print("\n🌐 Demo URL: http://localhost:8000")
        print("\n📋 How to use the demo:")
        print("   1. Open the URL above in your browser")
        print("   2. Try sample queries or type custom requests")
        print("   3. Watch real-time metrics and performance data")
        print("   4. Demonstrate multi-language capabilities")
        print("   5. Show tool integration and business impact")
        
        print("\n💡 Sample queries to demonstrate:")
        print("   • 'I want to recharge my phone for 200 rupees'")
        print("   • 'What is my account balance?'")
        print("   • 'Show me available plans'")
        print("   • 'My internet is not working'")
        print("   • 'Recommend best plan for me'")
        
        # Automatically open browser
        print("\n🔄 Opening browser...")
        time.sleep(2)
        webbrowser.open("http://localhost:8000")
        
        print("\n✅ Demo is ready for presentation!")
        print("⚠️  Press Ctrl+C to stop the demo server")
        
        # Wait for the process
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping demo server...")
            process.terminate()
            print("✅ Demo stopped successfully!")
            
    except Exception as e:
        print(f"❌ Error starting demo: {e}")
        print("💡 Please ensure you're in the correct directory and try again")


if __name__ == "__main__":
    start_demo()