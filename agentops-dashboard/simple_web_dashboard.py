#!/usr/bin/env python3
"""
Simple Web Dashboard for IHCL AgentOps Demo
Runs a local web server to demonstrate the monitoring interface
"""

import json
import webbrowser
from datetime import datetime, timedelta
from http.server import HTTPServer, SimpleHTTPRequestHandler
import socketserver
import threading
import time

# Demo data for the dashboard
DEMO_DATA = {
    "executive_metrics": {
        "total_incidents": 2847,
        "avg_response_time": "1.8s",
        "success_rate": "87%",
        "cost_per_task": "$0.02",
        "compliance_rate": "98%",
        "monthly_savings": "$12,450"
    },
    "agents": [
        {
            "name": "Security Triage Agent",
            "status": "active",
            "tasks_today": 89,
            "success_rate": 87,
            "latency": 1.8,
            "cost": 0.02
        },
        {
            "name": "Hotel Operations Agent", 
            "status": "active",
            "tasks_today": 156,
            "success_rate": 89,
            "latency": 2.1,
            "cost": 0.03
        },
        {
            "name": "Fraud Detection Agent",
            "status": "active",
            "tasks_today": 34,
            "success_rate": 94,
            "latency": 1.6,
            "cost": 0.02
        }
    ],
    "security_incidents": [
        {"type": "Guest Access Violation", "count": 45, "resolved": 42},
        {"type": "Payment Fraud Alert", "count": 12, "resolved": 12},
        {"type": "PII Data Breach", "count": 3, "resolved": 3},
        {"type": "Operational Security", "count": 28, "resolved": 26}
    ],
    "compliance": {
        "DPDP Act 2023": {"score": 98, "violations": 2},
        "PCI DSS": {"score": 100, "violations": 0},
        "GDPR": {"score": 97, "violations": 3},
        "SOX Compliance": {"score": 99, "violations": 1}
    }
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>IHCL FlexiCore - AgentOps Dashboard</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        .header {
            background: rgba(255,255,255,0.95);
            padding: 1rem 2rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            border-bottom: 3px solid #667eea;
        }
        .header h1 {
            color: #2c3e50;
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        .header .subtitle {
            color: #7f8c8d;
            font-size: 1.1rem;
        }
        .container {
            max-width: 1400px;
            margin: 2rem auto;
            padding: 0 2rem;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }
        .metric-card {
            background: rgba(255,255,255,0.95);
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border-left: 5px solid #27ae60;
            transition: transform 0.3s ease;
        }
        .metric-card:hover {
            transform: translateY(-5px);
        }
        .metric-card h3 {
            color: #2c3e50;
            margin-bottom: 1rem;
            font-size: 1.1rem;
        }
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
            color: #27ae60;
            margin-bottom: 0.5rem;
        }
        .metric-label {
            color: #7f8c8d;
            font-size: 0.9rem;
        }
        .section {
            background: rgba(255,255,255,0.95);
            margin-bottom: 2rem;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .section-header {
            background: #34495e;
            color: white;
            padding: 1rem 2rem;
            font-size: 1.3rem;
            font-weight: 600;
        }
        .section-content {
            padding: 2rem;
        }
        .agent-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
        }
        .agent-card {
            border: 2px solid #ecf0f1;
            border-radius: 8px;
            padding: 1.5rem;
            background: #f8f9fa;
        }
        .agent-status {
            display: flex;
            align-items: center;
            margin-bottom: 1rem;
        }
        .status-dot {
            width: 12px;
            height: 12px;
            background: #27ae60;
            border-radius: 50%;
            margin-right: 0.5rem;
        }
        .incident-list {
            display: grid;
            gap: 1rem;
        }
        .incident-item {
            display: flex;
            justify-content: between;
            align-items: center;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }
        .compliance-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
        }
        .compliance-item {
            text-align: center;
            padding: 1rem;
            background: #f8f9fa;
            border-radius: 8px;
        }
        .compliance-score {
            font-size: 2rem;
            font-weight: bold;
            color: #27ae60;
        }
        .live-indicator {
            display: inline-block;
            width: 10px;
            height: 10px;
            background: #e74c3c;
            border-radius: 50%;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .roi-highlight {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            text-align: center;
            padding: 2rem;
            border-radius: 12px;
            margin: 2rem 0;
        }
        .roi-highlight h2 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏨 IHCL FlexiCore Security Platform</h1>
        <div class="subtitle">
            AgentOps Dashboard - Real-time AI Agent Monitoring & Analytics
            <span class="live-indicator"></span> LIVE
        </div>
    </div>

    <div class="container">
        <!-- Executive Metrics -->
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>📊 Total Incidents</h3>
                <div class="metric-value">2,847</div>
                <div class="metric-label">Processed this month</div>
            </div>
            <div class="metric-card">
                <h3>⚡ Response Time</h3>
                <div class="metric-value">1.8s</div>
                <div class="metric-label">Average (vs 4+ hrs manual)</div>
            </div>
            <div class="metric-card">
                <h3>🎯 Success Rate</h3>
                <div class="metric-value">87%</div>
                <div class="metric-label">Task completion accuracy</div>
            </div>
            <div class="metric-card">
                <h3>💰 Cost Efficiency</h3>
                <div class="metric-value">$0.02</div>
                <div class="metric-label">Per task (vs $50+ manual)</div>
            </div>
            <div class="metric-card">
                <h3>🛡️ Compliance</h3>
                <div class="metric-value">98%</div>
                <div class="metric-label">DPDP, PCI DSS, GDPR</div>
            </div>
            <div class="metric-card">
                <h3>📈 Monthly Savings</h3>
                <div class="metric-value">$12.4K</div>
                <div class="metric-label">vs manual processing</div>
            </div>
        </div>

        <!-- ROI Highlight -->
        <div class="roi-highlight">
            <h2>₹33.2 Crore Projected NPV | 267% ROI</h2>
            <p>18-month payback period with immediate operational benefits</p>
        </div>

        <!-- Agent Performance -->
        <div class="section">
            <div class="section-header">🤖 Agent Performance Monitoring</div>
            <div class="section-content">
                <div class="agent-grid">
                    <div class="agent-card">
                        <div class="agent-status">
                            <div class="status-dot"></div>
                            <strong>Security Triage Agent</strong>
                        </div>
                        <p>Tasks Today: <strong>89</strong></p>
                        <p>Success Rate: <strong>87%</strong></p>
                        <p>Avg Latency: <strong>1.8s</strong></p>
                        <p>Cost/Task: <strong>$0.02</strong></p>
                    </div>
                    <div class="agent-card">
                        <div class="agent-status">
                            <div class="status-dot"></div>
                            <strong>Hotel Operations Agent</strong>
                        </div>
                        <p>Tasks Today: <strong>156</strong></p>
                        <p>Success Rate: <strong>89%</strong></p>
                        <p>Avg Latency: <strong>2.1s</strong></p>
                        <p>Cost/Task: <strong>$0.03</strong></p>
                    </div>
                    <div class="agent-card">
                        <div class="agent-status">
                            <div class="status-dot"></div>
                            <strong>Fraud Detection Agent</strong>
                        </div>
                        <p>Tasks Today: <strong>34</strong></p>
                        <p>Success Rate: <strong>94%</strong></p>
                        <p>Avg Latency: <strong>1.6s</strong></p>
                        <p>Cost/Task: <strong>$0.02</strong></p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Security Incidents -->
        <div class="section">
            <div class="section-header">🛡️ Security Incident Analysis</div>
            <div class="section-content">
                <div class="incident-list">
                    <div class="incident-item">
                        <div>
                            <strong>Guest Access Violations</strong><br>
                            <small>42/45 resolved (93%)</small>
                        </div>
                        <div style="color: #27ae60; font-weight: bold;">✅ 2.3min avg</div>
                    </div>
                    <div class="incident-item">
                        <div>
                            <strong>Payment Fraud Alerts</strong><br>
                            <small>12/12 resolved (100%)</small>
                        </div>
                        <div style="color: #27ae60; font-weight: bold;">✅ 1.8min avg</div>
                    </div>
                    <div class="incident-item">
                        <div>
                            <strong>PII Data Breaches</strong><br>
                            <small>3/3 resolved (100%)</small>
                        </div>
                        <div style="color: #27ae60; font-weight: bold;">✅ 4.2min avg</div>
                    </div>
                    <div class="incident-item">
                        <div>
                            <strong>Operational Security</strong><br>
                            <small>26/28 resolved (93%)</small>
                        </div>
                        <div style="color: #27ae60; font-weight: bold;">✅ 3.1min avg</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Compliance Monitoring -->
        <div class="section">
            <div class="section-header">📋 Compliance Monitoring</div>
            <div class="section-content">
                <div class="compliance-grid">
                    <div class="compliance-item">
                        <div class="compliance-score">98%</div>
                        <strong>DPDP Act 2023</strong><br>
                        <small>2 violations (30 days)</small>
                    </div>
                    <div class="compliance-item">
                        <div class="compliance-score">100%</div>
                        <strong>PCI DSS</strong><br>
                        <small>0 violations (30 days)</small>
                    </div>
                    <div class="compliance-item">
                        <div class="compliance-score">97%</div>
                        <strong>GDPR</strong><br>
                        <small>3 violations (30 days)</small>
                    </div>
                    <div class="compliance-item">
                        <div class="compliance-score">99%</div>
                        <strong>SOX Compliance</strong><br>
                        <small>1 violation (30 days)</small>
                    </div>
                </div>
            </div>
        </div>

        <!-- Business Impact -->
        <div class="section">
            <div class="section-header">📈 Business Impact Summary</div>
            <div class="section-content">
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1rem;">
                    <div>
                        <h4>🚀 Operational Efficiency</h4>
                        <ul style="margin-top: 0.5rem; line-height: 1.6;">
                            <li>78% reduction in incident response time</li>
                            <li>85% automation rate for routine operations</li>
                            <li>15% improvement in guest satisfaction</li>
                        </ul>
                    </div>
                    <div>
                        <h4>💰 Financial Impact</h4>
                        <ul style="margin-top: 0.5rem; line-height: 1.6;">
                            <li>₹33.2 crore projected 3-year NPV</li>
                            <li>267% ROI with 18-month payback</li>
                            <li>$12,450 monthly operational savings</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Add some dynamic updates to simulate real-time data
        setInterval(() => {
            const indicators = document.querySelectorAll('.live-indicator');
            indicators.forEach(indicator => {
                indicator.style.background = indicator.style.background === 'rgb(231, 76, 60)' ? '#27ae60' : '#e74c3c';
            });
        }, 2000);

        // Update timestamp
        setInterval(() => {
            const now = new Date().toLocaleString();
            document.title = `IHCL FlexiCore Dashboard - ${now}`;
        }, 60000);
    </script>
</body>
</html>
"""

class DashboardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/dashboard':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode())
        elif self.path == '/api/data':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(DEMO_DATA).encode())
        else:
            self.send_error(404)

def start_server(port=8080):
    """Start the web server"""
    try:
        with socketserver.TCPServer(("", port), DashboardHandler) as httpd:
            print(f"\n🚀 IHCL AgentOps Dashboard starting...")
            print(f"📊 Dashboard URL: http://localhost:{port}")
            print(f"🌐 Opening browser automatically...")
            print("="*60)
            
            # Open browser automatically
            def open_browser():
                time.sleep(2)  # Wait for server to start
                webbrowser.open(f'http://localhost:{port}')
            
            browser_thread = threading.Thread(target=open_browser)
            browser_thread.daemon = True
            browser_thread.start()
            
            print(f"🔄 Server running on port {port}")
            print("💡 Press Ctrl+C to stop the server")
            print("="*60)
            
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ Port {port} is already in use. Trying port {port+1}...")
            start_server(port+1)
        else:
            print(f"\n❌ Error starting server: {e}")

if __name__ == "__main__":
    start_server()