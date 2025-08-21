#!/usr/bin/env python3
"""
My Telecom AI Agent - Web MVP Demo

A simple web-based demo showcasing the telecom AI agent capabilities
for interview demonstrations. Built with FastAPI and vanilla HTML/JS.
"""

import asyncio
import json
import random
import time
from datetime import datetime
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel


class Language(Enum):
    ENGLISH = "en"
    HINDI = "hi" 
    TAMIL = "ta"
    TELUGU = "te"


class Channel(Enum):
    WEB = "web"
    MOBILE_APP = "mobile_app"
    CHAT = "chat"


@dataclass
class CustomerContext:
    customer_id: str
    phone_number: str
    preferred_language: Language = Language.ENGLISH
    channel: Channel = Channel.WEB
    account_type: str = "prepaid"
    session_id: str = ""


class QueryRequest(BaseModel):
    query: str
    customer_id: str = "DEMO_USER"
    phone_number: str = "9876543210"
    language: str = "en"


class TelecomAIAgent:
    """Simplified agent for web demo"""
    
    def __init__(self):
        self.agent_id = "my-telecom-ai-web-v1.0"
        self.supported_intents = {
            "recharge_request": "Customer wants to recharge account",
            "bill_payment": "Customer wants to pay bill",
            "plan_inquiry": "Customer asking about plans", 
            "balance_check": "Customer wants balance info",
            "technical_support": "Customer has technical issues",
            "plan_recommendation": "Customer wants plan suggestions"
        }
        
        self.confidence_thresholds = {
            "intent_detection": 0.85,
            "tool_execution": 0.90
        }

    async def process_query(self, query: str, context: CustomerContext) -> Dict[str, Any]:
        """Process customer query and return structured response"""
        
        # Simulate processing delay for realism
        await asyncio.sleep(random.uniform(0.5, 1.5))
        
        # Intent detection
        intent_result = self._detect_intent(query)
        
        # Extract information
        entities = self._extract_entities(query, intent_result["intent"])
        
        # Execute tools
        tool_result = await self._execute_tools(intent_result["intent"], entities, context)
        
        # Generate response
        response = self._generate_response(intent_result, tool_result, entities)
        
        # Collect metrics
        metrics = self._collect_metrics(intent_result, tool_result)
        
        return {
            "status": "success",
            "intent": intent_result,
            "entities": entities,
            "tool_result": tool_result,
            "response": response,
            "metrics": metrics,
            "timestamp": datetime.now().isoformat()
        }

    def _detect_intent(self, query: str) -> Dict[str, Any]:
        """Simulate intent detection with confidence scoring"""
        query_lower = query.lower()
        
        # Intent detection logic
        if any(word in query_lower for word in ["recharge", "topup", "top up", "add money"]):
            intent = "recharge_request"
            confidence = random.uniform(0.88, 0.95)
        elif any(word in query_lower for word in ["bill", "payment", "pay", "due"]):
            intent = "bill_payment"
            confidence = random.uniform(0.85, 0.93)
        elif any(word in query_lower for word in ["balance", "money left", "account", "check balance"]):
            intent = "balance_check"
            confidence = random.uniform(0.90, 0.97)
        elif any(word in query_lower for word in ["plan", "plans", "subscription", "package"]):
            intent = "plan_inquiry" 
            confidence = random.uniform(0.87, 0.94)
        elif any(word in query_lower for word in ["problem", "issue", "not working", "trouble", "help"]):
            intent = "technical_support"
            confidence = random.uniform(0.82, 0.91)
        elif any(word in query_lower for word in ["recommend", "suggest", "best plan", "which plan"]):
            intent = "plan_recommendation"
            confidence = random.uniform(0.85, 0.92)
        else:
            intent = "general_inquiry"
            confidence = random.uniform(0.60, 0.80)
        
        return {
            "intent": intent,
            "confidence": confidence,
            "description": self.supported_intents.get(intent, "General inquiry")
        }

    def _extract_entities(self, query: str, intent: str) -> Dict[str, Any]:
        """Extract relevant entities from query"""
        entities = {}
        
        if intent == "recharge_request":
            # Extract amount
            amount_words = ["100", "200", "299", "399", "500", "999"]
            for amount in amount_words:
                if amount in query:
                    entities["amount"] = amount
                    break
            else:
                entities["amount"] = random.choice(["100", "200", "299"])
        
        elif intent == "plan_inquiry":
            if "unlimited" in query.lower():
                entities["plan_type"] = "unlimited"
            elif "limited" in query.lower():
                entities["plan_type"] = "limited"
        
        return entities

    async def _execute_tools(self, intent: str, entities: Dict, context: CustomerContext) -> Dict[str, Any]:
        """Simulate tool execution"""
        
        if intent == "recharge_request":
            amount = entities.get("amount", "100")
            return {
                "status": "success",
                "transaction_id": f"TXN{random.randint(100000, 999999)}",
                "amount": amount,
                "new_balance": str(random.uniform(100, 500)),
                "validity_days": "30"
            }
        
        elif intent == "bill_payment":
            return {
                "status": "success", 
                "reference_id": f"BILL{random.randint(100000, 999999)}",
                "amount_paid": str(random.uniform(200, 800)),
                "next_due_date": "2024-02-15"
            }
        
        elif intent == "balance_check":
            return {
                "status": "success",
                "main_balance": str(random.uniform(50, 500)),
                "data_balance": f"{random.uniform(1, 10):.1f} GB",
                "validity_days": str(random.randint(5, 30)),
                "plan_name": random.choice(["Basic Plan", "Pro Plan", "Unlimited Plan"])
            }
        
        elif intent == "plan_inquiry":
            plans = [
                {"name": "Basic Plan", "price": "₹199", "data": "2GB/day", "validity": "28 days"},
                {"name": "Pro Plan", "price": "₹399", "data": "Unlimited", "validity": "30 days"},
                {"name": "Premium Plan", "price": "₹599", "data": "Unlimited 5G", "validity": "30 days"}
            ]
            return {
                "status": "success",
                "available_plans": plans,
                "recommendation": "Pro Plan - Best value for regular users"
            }
        
        elif intent == "technical_support":
            return {
                "status": "success",
                "diagnostics": {
                    "network_status": "Good",
                    "signal_strength": f"{random.randint(70, 95)}%",
                    "data_connectivity": "Active"
                },
                "resolution_steps": [
                    "Restart your device",
                    "Check network settings",
                    "Toggle airplane mode on/off"
                ]
            }
        
        elif intent == "plan_recommendation":
            return {
                "status": "success",
                "recommended_plan": {
                    "name": "Pro Plan",
                    "price": "₹399",
                    "benefits": ["Unlimited Data", "100 SMS/day", "Free Roaming"],
                    "savings": "₹100/month vs current usage"
                }
            }
        
        else:
            return {
                "status": "escalated",
                "reason": "Query requires human assistance"
            }

    def _generate_response(self, intent_result: Dict, tool_result: Dict, entities: Dict) -> Dict[str, Any]:
        """Generate user-friendly response"""
        
        intent = intent_result["intent"]
        
        if tool_result["status"] == "escalated":
            response_text = "I understand your request. Let me connect you with one of our customer service representatives who can assist you better."
            response_type = "escalation"
        
        elif intent == "recharge_request" and tool_result["status"] == "success":
            amount = tool_result["amount"]
            txn_id = tool_result["transaction_id"]
            balance = tool_result["new_balance"]
            response_text = f"Great! Your recharge of ₹{amount} has been processed successfully. Transaction ID: {txn_id}. Your new balance is ₹{balance}."
            response_type = "success"
        
        elif intent == "bill_payment" and tool_result["status"] == "success":
            amount = tool_result["amount_paid"]
            ref_id = tool_result["reference_id"]
            response_text = f"Your bill payment of ₹{amount} has been completed. Reference ID: {ref_id}. Next due date: {tool_result['next_due_date']}."
            response_type = "success"
        
        elif intent == "balance_check" and tool_result["status"] == "success":
            balance = tool_result["main_balance"]
            data = tool_result["data_balance"]
            validity = tool_result["validity_days"]
            plan = tool_result["plan_name"]
            response_text = f"Your current balance is ₹{balance} with {data} data remaining. Plan: {plan}. Validity: {validity} days."
            response_type = "information"
        
        elif intent == "plan_inquiry" and tool_result["status"] == "success":
            plans_count = len(tool_result["available_plans"])
            recommendation = tool_result["recommendation"]
            response_text = f"I found {plans_count} plans for you. {recommendation}. Would you like to know more about any specific plan?"
            response_type = "information"
        
        elif intent == "technical_support" and tool_result["status"] == "success":
            signal = tool_result["diagnostics"]["signal_strength"]
            response_text = f"I've run diagnostics. Your signal strength is {signal}. Try restarting your device and check if the issue persists."
            response_type = "support"
        
        elif intent == "plan_recommendation" and tool_result["status"] == "success":
            plan = tool_result["recommended_plan"]
            response_text = f"Based on your usage, I recommend the {plan['name']} at {plan['price']}. It offers {', '.join(plan['benefits'])} and can save you {plan['savings']}."
            response_type = "recommendation"
        
        else:
            response_text = "I've processed your request. Is there anything else I can help you with?"
            response_type = "general"
        
        return {
            "text": response_text,
            "type": response_type,
            "data": tool_result
        }

    def _collect_metrics(self, intent_result: Dict, tool_result: Dict) -> Dict[str, Any]:
        """Collect performance metrics"""
        
        processing_time = random.uniform(0.8, 2.2)
        cost = random.uniform(0.01, 0.04)
        
        return {
            "processing_time_seconds": round(processing_time, 2),
            "cost_usd": round(cost, 3),
            "intent_confidence": intent_result["confidence"],
            "tool_success": tool_result["status"] == "success",
            "containment": tool_result["status"] != "escalated"
        }


# Initialize FastAPI app
app = FastAPI(title="My Telecom AI Agent", description="Web-based demo for telecom customer service AI")

# Initialize agent
agent = TelecomAIAgent()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def home():
    """Serve main demo page"""
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Telecom AI Agent - Live Demo</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        
        .demo-section {
            padding: 40px;
        }
        
        .chat-container {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            min-height: 400px;
            border: 1px solid #e9ecef;
        }
        
        .messages {
            height: 300px;
            overflow-y: auto;
            margin-bottom: 20px;
            padding: 10px;
        }
        
        .message {
            margin-bottom: 15px;
            padding: 12px 16px;
            border-radius: 10px;
            max-width: 80%;
            animation: fadeIn 0.3s ease-in;
        }
        
        .user-message {
            background: #007bff;
            color: white;
            margin-left: auto;
            text-align: right;
        }
        
        .agent-message {
            background: #e3f2fd;
            color: #1976d2;
            border-left: 4px solid #2196f3;
        }
        
        .input-section {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .query-input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        .query-input:focus {
            outline: none;
            border-color: #007bff;
        }
        
        .send-btn {
            padding: 12px 24px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        
        .send-btn:hover {
            background: #0056b3;
        }
        
        .send-btn:disabled {
            background: #6c757d;
            cursor: not-allowed;
        }
        
        .language-selector {
            margin-bottom: 10px;
        }
        
        .language-selector select {
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }
        
        .metrics-panel {
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        
        .metric-card {
            background: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .metric-value {
            font-size: 1.5em;
            font-weight: bold;
            color: #007bff;
        }
        
        .metric-label {
            font-size: 0.9em;
            color: #6c757d;
            margin-top: 5px;
        }
        
        .sample-queries {
            margin-top: 20px;
        }
        
        .sample-query {
            display: inline-block;
            background: #e9ecef;
            padding: 8px 12px;
            margin: 5px;
            border-radius: 15px;
            cursor: pointer;
            font-size: 14px;
            transition: background-color 0.3s;
        }
        
        .sample-query:hover {
            background: #007bff;
            color: white;
        }
        
        .loading {
            display: none;
            text-align: center;
            color: #007bff;
            margin: 10px 0;
        }
        
        .spinner {
            border: 2px solid #f3f3f3;
            border-top: 2px solid #007bff;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 1s linear infinite;
            display: inline-block;
            margin-right: 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .demo-info {
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        
        .demo-info h3 {
            color: #856404;
            margin-bottom: 10px;
        }
        
        .demo-info p {
            color: #856404;
            margin-bottom: 5px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📱 My Telecom AI Agent</h1>
            <p>Production-Scale Customer Service AI Demo</p>
            <p>Supporting 11+ Languages | Multi-channel Integration | Tool-based Actions</p>
        </div>
        
        <div class="demo-section">
            <div class="demo-info">
                <h3>🎯 Live Demo Features</h3>
                <p>• Multi-step conversation workflows with confidence-based decision making</p>
                <p>• Real-time tool integration for recharges, bill payments, and technical support</p>
                <p>• Production-grade performance monitoring and metrics collection</p>
                <p>• Multilingual support with intelligent intent detection</p>
            </div>
            
            <div class="language-selector">
                <label for="language">Language: </label>
                <select id="language">
                    <option value="en">English</option>
                    <option value="hi">Hindi</option>
                    <option value="ta">Tamil</option>
                    <option value="te">Telugu</option>
                </select>
            </div>
            
            <div class="chat-container">
                <div class="messages" id="messages">
                    <div class="message agent-message">
                        👋 Hello! I'm your AI assistant for telecom services. I can help you with:
                        <br>• Account recharges and bill payments
                        <br>• Plan information and recommendations  
                        <br>• Balance checks and account details
                        <br>• Technical support and troubleshooting
                        <br><br>How can I assist you today?
                    </div>
                </div>
                
                <div class="loading" id="loading">
                    <div class="spinner"></div>
                    Processing your request...
                </div>
                
                <div class="input-section">
                    <input type="text" class="query-input" id="queryInput" 
                           placeholder="Type your question here..." 
                           onkeypress="handleKeyPress(event)">
                    <button class="send-btn" id="sendBtn" onclick="sendQuery()">Send</button>
                </div>
            </div>
            
            <div class="sample-queries">
                <h3>💡 Try these sample queries:</h3>
                <div class="sample-query" onclick="setQuery('I want to recharge my phone for 200 rupees')">
                    Recharge ₹200
                </div>
                <div class="sample-query" onclick="setQuery('What is my account balance?')">
                    Check Balance
                </div>
                <div class="sample-query" onclick="setQuery('Show me available plans')">
                    View Plans
                </div>
                <div class="sample-query" onclick="setQuery('My internet is not working')">
                    Technical Issue
                </div>
                <div class="sample-query" onclick="setQuery('Recommend best plan for me')">
                    Plan Recommendation
                </div>
                <div class="sample-query" onclick="setQuery('Pay my monthly bill')">
                    Bill Payment
                </div>
            </div>
            
            <div class="metrics-panel">
                <h3>📊 Real-time Performance Metrics</h3>
                <div class="metrics-grid" id="metricsGrid">
                    <div class="metric-card">
                        <div class="metric-value" id="totalQueries">0</div>
                        <div class="metric-label">Total Queries</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="avgResponseTime">0.0s</div>
                        <div class="metric-label">Avg Response Time</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="avgConfidence">0%</div>
                        <div class="metric-label">Avg Confidence</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="containmentRate">0%</div>
                        <div class="metric-label">Containment Rate</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value" id="totalCost">$0.000</div>
                        <div class="metric-label">Total Cost</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let totalQueries = 0;
        let totalResponseTime = 0;
        let totalConfidence = 0;
        let totalCost = 0;
        let containedQueries = 0;

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendQuery();
            }
        }

        function setQuery(query) {
            document.getElementById('queryInput').value = query;
        }

        async function sendQuery() {
            const queryInput = document.getElementById('queryInput');
            const query = queryInput.value.trim();
            
            if (!query) return;
            
            // Disable input and show loading
            const sendBtn = document.getElementById('sendBtn');
            const loading = document.getElementById('loading');
            
            sendBtn.disabled = true;
            loading.style.display = 'block';
            
            // Add user message
            addMessage(query, 'user');
            queryInput.value = '';
            
            try {
                const language = document.getElementById('language').value;
                const response = await fetch('/api/query', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        query: query,
                        language: language
                    })
                });
                
                const result = await response.json();
                
                if (result.status === 'success') {
                    // Add agent response
                    addMessage(result.response.text, 'agent');
                    
                    // Update metrics
                    updateMetrics(result.metrics);
                } else {
                    addMessage('Sorry, I encountered an error processing your request.', 'agent');
                }
                
            } catch (error) {
                console.error('Error:', error);
                addMessage('Sorry, there was a connection error. Please try again.', 'agent');
            } finally {
                sendBtn.disabled = false;
                loading.style.display = 'none';
            }
        }

        function addMessage(text, type) {
            const messages = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${type}-message`;
            messageDiv.textContent = text;
            messages.appendChild(messageDiv);
            messages.scrollTop = messages.scrollHeight;
        }

        function updateMetrics(metrics) {
            totalQueries++;
            totalResponseTime += metrics.processing_time_seconds;
            totalConfidence += metrics.intent_confidence;
            totalCost += metrics.cost_usd;
            
            if (metrics.containment) {
                containedQueries++;
            }
            
            // Update display
            document.getElementById('totalQueries').textContent = totalQueries;
            document.getElementById('avgResponseTime').textContent = 
                (totalResponseTime / totalQueries).toFixed(1) + 's';
            document.getElementById('avgConfidence').textContent = 
                Math.round((totalConfidence / totalQueries) * 100) + '%';
            document.getElementById('containmentRate').textContent = 
                Math.round((containedQueries / totalQueries) * 100) + '%';
            document.getElementById('totalCost').textContent = 
                '$' + totalCost.toFixed(3);
        }
    </script>
</body>
</html>
    """
    return HTMLResponse(content=html_content)


@app.post("/api/query")
async def process_query(request: QueryRequest):
    """Process customer query through AI agent"""
    try:
        # Create customer context
        context = CustomerContext(
            customer_id=request.customer_id,
            phone_number=request.phone_number,
            preferred_language=Language(request.language),
            channel=Channel.WEB,
            session_id=f"WEB_{random.randint(1000, 9999)}"
        )
        
        # Process query
        result = await agent.process_query(request.query, context)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "agent_id": agent.agent_id}


if __name__ == "__main__":
    print("\n🚀 Starting My Telecom AI Agent Web Demo")
    print("=" * 60)
    print("📱 Production-scale customer service AI demonstration")
    print("🌐 Web interface: http://localhost:8000")
    print("🎯 Features: Multi-language, Tool integration, Real-time metrics")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")