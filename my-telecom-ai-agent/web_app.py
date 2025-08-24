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
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel
import os
import io
import tempfile
import edge_tts
from elevenlabs import ElevenLabs, VoiceSettings
from PIL import Image, ImageDraw, ImageFont
import base64


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
        
        # Generate response with language support
        response = self._generate_response(intent_result, tool_result, entities, context.preferred_language.value)
        
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
                "new_balance": f"{random.uniform(100, 500):.2f}",
                "validity_days": "30"
            }
        
        elif intent == "bill_payment":
            return {
                "status": "success", 
                "reference_id": f"BILL{random.randint(100000, 999999)}",
                "amount_paid": f"{random.uniform(200, 800):.2f}",
                "next_due_date": "2024-02-15"
            }
        
        elif intent == "balance_check":
            return {
                "status": "success",
                "main_balance": f"{random.uniform(50, 500):.2f}",
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

    def _generate_response(self, intent_result: Dict, tool_result: Dict, entities: Dict, language: str = "en") -> Dict[str, Any]:
        """Generate user-friendly response in appropriate language"""
        
        intent = intent_result["intent"]
        
        if tool_result["status"] == "escalated":
            if language == "hi":
                response_text = "मैं आपकी बात समझ गया हूं। मैं आपको हमारे ग्राहक सेवा प्रतिनिधि से जोड़ता हूं जो आपकी बेहतर सहायता कर सकते हैं।"
            else:
                response_text = "I understand your request. Let me connect you with one of our customer service representatives who can assist you better."
            response_type = "escalation"
        
        elif intent == "recharge_request" and tool_result["status"] == "success":
            amount = tool_result["amount"]
            txn_id = tool_result["transaction_id"]
            balance = tool_result["new_balance"]
            if language == "hi":
                response_text = f"बहुत बढ़िया! आपका ₹{amount} का रिचार्ज सफलतापूर्वक हो गया है। ट्रांजैक्शन आईडी: {txn_id}। आपका नया बैलेंस ₹{balance} है।"
            else:
                response_text = f"Great! Your recharge of ₹{amount} has been processed successfully. Transaction ID: {txn_id}. Your new balance is ₹{balance}."
            response_type = "success"
        
        elif intent == "bill_payment" and tool_result["status"] == "success":
            amount = tool_result["amount_paid"]
            ref_id = tool_result["reference_id"]
            if language == "hi":
                response_text = f"आपका ₹{amount} का बिल पेमेंट पूरा हो गया है। रेफरेंस आईडी: {ref_id}। अगली देय तारीख: {tool_result['next_due_date']}।"
            else:
                response_text = f"Your bill payment of ₹{amount} has been completed. Reference ID: {ref_id}. Next due date: {tool_result['next_due_date']}."
            response_type = "success"
        
        elif intent == "balance_check" and tool_result["status"] == "success":
            balance = tool_result["main_balance"]
            data = tool_result["data_balance"]
            validity = tool_result["validity_days"]
            plan = tool_result["plan_name"]
            if language == "hi":
                response_text = f"आपका वर्तमान बैलेंस ₹{balance} है और {data} डेटा बचा है। प्लान: {plan}। वैधता: {validity} दिन।"
            else:
                response_text = f"Your current balance is ₹{balance} with {data} data remaining. Plan: {plan}. Validity: {validity} days."
            response_type = "information"
        
        elif intent == "plan_inquiry" and tool_result["status"] == "success":
            plans_count = len(tool_result["available_plans"])
            recommendation = tool_result["recommendation"]
            if language == "hi":
                response_text = f"मुझे आपके लिए {plans_count} प्लान मिले हैं। {recommendation}। क्या आप किसी विशेष प्लान के बारे में और जानना चाहते हैं?"
            else:
                response_text = f"I found {plans_count} plans for you. {recommendation}. Would you like to know more about any specific plan?"
            response_type = "information"
        
        elif intent == "technical_support" and tool_result["status"] == "success":
            signal = tool_result["diagnostics"]["signal_strength"]
            if language == "hi":
                response_text = f"मैंने जांच की है। आपकी सिग्नल स्ट्रेंथ {signal} है। पहले अपना डिवाइस रीस्टार्ट करके देखें और अगर समस्या बनी रहे तो हमसे संपर्क करें।"
            else:
                response_text = f"I've run diagnostics. Your signal strength is {signal}. Try restarting your device and check if the issue persists."
            response_type = "support"
        
        elif intent == "plan_recommendation" and tool_result["status"] == "success":
            plan = tool_result["recommended_plan"]
            if language == "hi":
                response_text = f"आपके उपयोग के अनुसार, मैं {plan['name']} प्लान सुझाता हूं जो ₹{plan['price']} में है। इसमें {', '.join(plan['benefits'])} मिलता है और आप {plan['savings']} बचा सकते हैं।"
            else:
                response_text = f"Based on your usage, I recommend the {plan['name']} at {plan['price']}. It offers {', '.join(plan['benefits'])} and can save you {plan['savings']}."
            response_type = "recommendation"
        
        else:
            if language == "hi":
                response_text = "मैंने आपकी बात समझ ली है। क्या मैं आपकी और कोई सहायता कर सकता हूं?"
            else:
                response_text = "I've processed your request. Is there anything else I can help you with?"
            response_type = "general"
        
        return {
            "text": response_text,
            "type": response_type,
            "data": tool_result,
            "language": language
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

# Add CORS middleware for React frontend
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3005", "http://localhost:3002", "http://localhost:3000", "http://127.0.0.1:3005", "http://127.0.0.1:3002", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Initialize agent
agent = TelecomAIAgent()

# Initialize ElevenLabs client (for demo - using free tier)
# For production, set your API key: client = ElevenLabs(api_key="your_api_key")
try:
    # Initialize ElevenLabs client with API key if available
    # For demo purposes, we'll use enhanced browser TTS
    # To enable ElevenLabs, add your API key:
    # elevenlabs_client = ElevenLabs(api_key="your_api_key_here")
    elevenlabs_client = None  # Disabled for demo - using enhanced browser TTS
    print("Using enhanced browser TTS for natural voice experience")
except:
    elevenlabs_client = None
    print("ElevenLabs not configured - using enhanced browser TTS")


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
    
    <!-- Google Fonts for professional typography -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
    
    <style>
        :root {
            /* Modern Color Palette */
            --primary-gradient: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
            --surface-primary: #ffffff;
            --surface-secondary: #f8fafc;
            --surface-tertiary: #f1f5f9;
            --border-primary: #e2e8f0;
            --border-secondary: #cbd5e1;
            --text-primary: #0f172a;
            --text-secondary: #475569;
            --text-tertiary: #64748b;
            --accent-primary: #6366f1;
            --accent-secondary: #8b5cf6;
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
            --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
            --radius-sm: 6px;
            --radius-md: 8px;
            --radius-lg: 12px;
            --radius-xl: 16px;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--primary-gradient);
            min-height: 100vh;
            padding: 24px;
            line-height: 1.6;
            color: var(--text-primary);
            font-feature-settings: 'cv11', 'ss01';
            font-optical-sizing: auto;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: var(--surface-primary);
            border-radius: var(--radius-xl);
            box-shadow: var(--shadow-xl);
            overflow: hidden;
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .header {
            background: var(--primary-gradient);
            color: white;
            padding: 48px 32px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="20" cy="20" r="1" fill="white" opacity="0.1"/><circle cx="80" cy="40" r="1" fill="white" opacity="0.05"/><circle cx="40" cy="80" r="1" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            pointer-events: none;
        }
        
        .header-content {
            position: relative;
            z-index: 1;
        }
        
        .header h1 {
            font-size: clamp(2rem, 4vw, 3rem);
            font-weight: 700;
            margin-bottom: 16px;
            letter-spacing: -0.025em;
        }
        
        .header-subtitle {
            font-size: 1.25rem;
            font-weight: 500;
            opacity: 0.9;
            margin-bottom: 8px;
        }
        
        .header-description {
            font-size: 1rem;
            opacity: 0.8;
            font-weight: 400;
        }
        
        .demo-section {
            padding: 48px 32px;
            background: var(--surface-secondary);
        }
        
        .demo-grid {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 32px;
            margin-bottom: 32px;
        }
        
        @media (max-width: 1024px) {
            .demo-grid {
                grid-template-columns: 1fr;
            }
        }
        
        .chat-panel {
            background: var(--surface-primary);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-lg);
            border: 1px solid var(--border-primary);
            overflow: hidden;
        }
        
        .chat-header {
            background: var(--surface-tertiary);
            padding: 20px 24px;
            border-bottom: 1px solid var(--border-primary);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        
        .chat-title {
            font-size: 1.125rem;
            font-weight: 600;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .status-indicator {
            width: 8px;
            height: 8px;
            background: var(--success);
            border-radius: 50%;
            animation: pulse-dot 2s infinite;
        }
        
        @keyframes pulse-dot {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        
        .language-selector {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .language-selector select {
            padding: 8px 12px;
            border: 1px solid var(--border-secondary);
            border-radius: var(--radius-sm);
            font-size: 14px;
            background: var(--surface-primary);
            color: var(--text-primary);
            font-family: inherit;
        }
        
        .messages {
            height: 400px;
            overflow-y: auto;
            padding: 24px;
            scroll-behavior: smooth;
        }
        
        .messages::-webkit-scrollbar {
            width: 6px;
        }
        
        .messages::-webkit-scrollbar-track {
            background: var(--surface-tertiary);
        }
        
        .messages::-webkit-scrollbar-thumb {
            background: var(--border-secondary);
            border-radius: 3px;
        }
        
        .message {
            margin-bottom: 16px;
            animation: slideInMessage 0.3s ease-out;
        }
        
        @keyframes slideInMessage {
            from {
                opacity: 0;
                transform: translateY(12px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        .message-content {
            max-width: 80%;
            padding: 16px 20px;
            border-radius: var(--radius-lg);
            position: relative;
            word-wrap: break-word;
        }
        
        .user-message .message-content {
            background: var(--accent-primary);
            color: white;
            margin-left: auto;
            border-bottom-right-radius: var(--radius-sm);
        }
        
        .agent-message .message-content {
            background: var(--surface-tertiary);
            color: var(--text-primary);
            border: 1px solid var(--border-primary);
            border-bottom-left-radius: var(--radius-sm);
        }
        
        .input-section {
            padding: 24px;
            background: var(--surface-primary);
            border-top: 1px solid var(--border-primary);
        }
        
        .input-container {
            display: flex;
            gap: 12px;
            align-items: flex-end;
        }
        
        .query-input {
            flex: 1;
            padding: 16px 20px;
            border: 2px solid var(--border-primary);
            border-radius: var(--radius-lg);
            font-size: 16px;
            font-family: inherit;
            background: var(--surface-primary);
            color: var(--text-primary);
            transition: all 0.2s ease;
            resize: none;
            min-height: 56px;
            max-height: 120px;
        }
        
        .query-input:focus {
            outline: none;
            border-color: var(--accent-primary);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }
        
        .action-buttons {
            display: flex;
            gap: 8px;
        }
        
        .voice-btn, .send-btn {
            padding: 16px;
            border: none;
            border-radius: var(--radius-lg);
            cursor: pointer;
            font-size: 18px;
            font-weight: 500;
            transition: all 0.2s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            min-width: 56px;
            height: 56px;
        }
        
        .voice-btn {
            background: var(--success);
            color: white;
        }
        
        .voice-btn:hover {
            background: #059669;
            transform: translateY(-1px);
        }
        
        .voice-btn.recording {
            background: var(--error);
            animation: pulse-record 1s infinite;
        }
        
        @keyframes pulse-record {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        .send-btn {
            background: var(--accent-primary);
            color: white;
            padding: 16px 24px;
            min-width: auto;
        }
        
        .send-btn:hover:not(:disabled) {
            background: var(--accent-secondary);
            transform: translateY(-1px);
        }
        
        .send-btn:disabled {
            background: var(--border-secondary);
            cursor: not-allowed;
            transform: none;
        }
        
        .sidebar {
            display: flex;
            flex-direction: column;
            gap: 24px;
        }
        
        .quick-actions {
            background: var(--surface-primary);
            border-radius: var(--radius-lg);
            padding: 24px;
            box-shadow: var(--shadow-md);
            border: 1px solid var(--border-primary);
        }
        
        .quick-actions h3 {
            font-size: 1.125rem;
            font-weight: 600;
            margin-bottom: 16px;
            color: var(--text-primary);
        }
        
        .sample-queries {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        .sample-query {
            padding: 12px 16px;
            background: var(--surface-tertiary);
            border: 1px solid var(--border-primary);
            border-radius: var(--radius-md);
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            color: var(--text-secondary);
            transition: all 0.2s ease;
            text-align: left;
        }
        
        .sample-query:hover {
            background: var(--accent-primary);
            color: white;
            transform: translateY(-1px);
            box-shadow: var(--shadow-md);
        }
        
        .metrics-panel {
            background: var(--surface-primary);
            border-radius: var(--radius-lg);
            padding: 24px;
            box-shadow: var(--shadow-md);
            border: 1px solid var(--border-primary);
        }
        
        .metrics-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 16px;
        }
        
        .metrics-header h3 {
            font-size: 1.125rem;
            font-weight: 600;
            color: var(--text-primary);
        }
        
        .metrics-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 16px;
        }
        
        .metric-card {
            background: var(--surface-tertiary);
            padding: 16px;
            border-radius: var(--radius-md);
            text-align: center;
            border: 1px solid var(--border-primary);
        }
        
        .metric-value {
            font-size: 1.5rem;
            font-weight: 700;
            font-family: 'JetBrains Mono', monospace;
            color: var(--accent-primary);
            margin-bottom: 4px;
        }
        
        .metric-label {
            font-size: 0.875rem;
            color: var(--text-tertiary);
            font-weight: 500;
        }
        
        .loading {
            display: none;
            text-align: center;
            color: var(--accent-primary);
            margin: 16px 0;
            font-weight: 500;
        }
        
        .loading.show {
            display: block;
        }
        
        .spinner {
            width: 20px;
            height: 20px;
            border: 2px solid var(--border-primary);
            border-top-color: var(--accent-primary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
            display: inline-block;
            margin-right: 8px;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .feature-highlights {
            margin-top: 48px;
            padding: 32px;
            background: var(--surface-primary);
            border-radius: var(--radius-lg);
            box-shadow: var(--shadow-md);
            border: 1px solid var(--border-primary);
        }
        
        .feature-highlights h3 {
            font-size: 1.25rem;
            font-weight: 600;
            margin-bottom: 16px;
            color: var(--text-primary);
        }
        
        .features-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
        }
        
        .feature-item {
            display: flex;
            align-items: flex-start;
            gap: 12px;
            padding: 16px;
            background: var(--surface-tertiary);
            border-radius: var(--radius-md);
            border: 1px solid var(--border-primary);
        }
        
        .feature-icon {
            font-size: 20px;
            flex-shrink: 0;
            margin-top: 2px;
        }
        
        .feature-text {
            font-size: 14px;
            color: var(--text-secondary);
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-content">
                <h1>My Telecom AI Agent</h1>
                <div class="header-subtitle">Production-Scale Customer Service AI</div>
                <div class="header-description">Enterprise-grade multilingual voice assistant with tool integration</div>
            </div>
        </div>
        
        <div class="demo-section">
            <div class="demo-grid">
                <div class="chat-panel">
                    <div class="chat-header">
                        <div class="chat-title">
                            <div class="status-indicator"></div>
                            AI Assistant
                        </div>
                        <div class="language-selector">
                            <select id="language">
                                <option value="en">🇺🇸 English</option>
                                <option value="hi">🇮🇳 हिंदी</option>
                                <option value="ta">🇮🇳 தமிழ்</option>
                                <option value="te">🇮🇳 తెలుగు</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="messages" id="messages">
                        <div class="message agent-message">
                            <div class="message-content">
                                <strong>Welcome!</strong> I'm your AI assistant for telecom services. I can help you with:
                                <br><br>
                                • Account recharges and bill payments<br>
                                • Plan information and recommendations<br>
                                • Balance checks and account details<br>
                                • Technical support and troubleshooting<br>
                                <br>
                                How can I assist you today?
                            </div>
                        </div>
                    </div>
                    
                    <div class="loading" id="loading">
                        <div class="spinner"></div>
                        Processing your request...
                    </div>
                    
                    <div class="input-section">
                        <div class="input-container">
                            <textarea class="query-input" id="queryInput" 
                                   placeholder="Type your question here or click the mic to speak..." 
                                   onkeypress="handleKeyPress(event)" rows="1"></textarea>
                            <div class="action-buttons">
                                <button class="voice-btn" id="voiceBtn" onclick="toggleVoice()" title="Voice Input">
                                    🎤
                                </button>
                                <button class="send-btn" id="sendBtn" onclick="sendQuery()" title="Send Message">
                                    ➤ Send
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="sidebar">
                    <div class="quick-actions">
                        <h3>Quick Actions</h3>
                        <div class="sample-queries">
                            <button class="sample-query" onclick="setQuery('I want to recharge my phone for 200 rupees')">
                                💳 Recharge ₹200
                            </button>
                            <button class="sample-query" onclick="setQuery('What is my account balance?')">
                                📊 Check Balance
                            </button>
                            <button class="sample-query" onclick="setQuery('Show me available plans')">
                                📋 View Plans
                            </button>
                            <button class="sample-query" onclick="setQuery('My internet is not working')">
                                🔧 Technical Issue
                            </button>
                            <button class="sample-query" onclick="setQuery('Recommend best plan for me')">
                                🎯 Plan Recommendation
                            </button>
                            <button class="sample-query" onclick="setQuery('Pay my monthly bill')">
                                💰 Bill Payment
                            </button>
                        </div>
                    </div>
                    
                    <div class="metrics-panel">
                        <div class="metrics-header">
                            📊
                            <h3>Live Metrics</h3>
                        </div>
                        <div class="metrics-grid">
                            <div class="metric-card">
                                <div class="metric-value" id="totalQueries">0</div>
                                <div class="metric-label">Queries</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value" id="avgResponseTime">0.0s</div>
                                <div class="metric-label">Avg Time</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value" id="avgConfidence">0%</div>
                                <div class="metric-label">Confidence</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value" id="containmentRate">0%</div>
                                <div class="metric-label">Contained</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="feature-highlights">
                <h3>Production Features Demonstrated</h3>
                <div class="features-grid">
                    <div class="feature-item">
                        <div class="feature-icon">🧠</div>
                        <div class="feature-text">Multi-step conversation workflows with confidence-based decision making</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">⚡</div>
                        <div class="feature-text">Real-time tool integration for recharges, bill payments, and technical support</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">📊</div>
                        <div class="feature-text">Production-grade performance monitoring and metrics collection</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">🌍</div>
                        <div class="feature-text">Multilingual support with intelligent intent detection and cultural adaptation</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">🎤</div>
                        <div class="feature-text">High-quality voice recognition and natural text-to-speech in multiple languages</div>
                    </div>
                    <div class="feature-item">
                        <div class="feature-icon">🛡️</div>
                        <div class="feature-text">Enterprise security with PII protection and comprehensive audit trails</div>
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
        
        // Voice recognition variables
        let recognition = null;
        let isRecording = false;
        let voiceInputUsed = false;
        let speechSynthesis = window.speechSynthesis;
        let voicesLoaded = false;
        
        // Ensure voices are loaded
        function loadVoices() {
            if (speechSynthesis.getVoices().length > 0) {
                voicesLoaded = true;
                console.log('Available voices:', speechSynthesis.getVoices().map(v => `${v.name} (${v.lang})`));
            }
        }
        
        // Load voices when available
        if (speechSynthesis.onvoiceschanged !== undefined) {
            speechSynthesis.onvoiceschanged = loadVoices;
        }
        loadVoices(); // Try immediately
        
        // Initialize speech recognition
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.continuous = false;
            recognition.interimResults = false;
            recognition.maxAlternatives = 1;
            
            recognition.onstart = function() {
                isRecording = true;
                const voiceBtn = document.getElementById('voiceBtn');
                voiceBtn.classList.add('recording');
                voiceBtn.textContent = '🔴';
            };
            
            recognition.onend = function() {
                isRecording = false;
                const voiceBtn = document.getElementById('voiceBtn');
                voiceBtn.classList.remove('recording');
                voiceBtn.textContent = '🎤';
            };
            
            recognition.onresult = function(event) {
                const transcript = event.results[0][0].transcript;
                document.getElementById('queryInput').value = transcript;
                voiceInputUsed = true;
                // Auto-send the query after voice input
                setTimeout(() => sendQuery(), 500);
            };
            
            recognition.onerror = function(event) {
                console.error('Speech recognition error:', event.error);
                addMessage('Sorry, I could not understand your voice. Please try again.', 'agent');
                isRecording = false;
                const voiceBtn = document.getElementById('voiceBtn');
                voiceBtn.classList.remove('recording');
                voiceBtn.textContent = '🎤';
            };
        }

        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendQuery();
            }
        }

        function toggleVoice() {
            if (!recognition) {
                alert('Voice recognition is not supported in your browser. Please use Chrome or Edge.');
                return;
            }
            
            if (isRecording) {
                recognition.stop();
            } else {
                // Set language based on current selection
                const language = document.getElementById('language').value;
                const langCodes = {
                    'en': 'en-US',
                    'hi': 'hi-IN',
                    'ta': 'ta-IN', 
                    'te': 'te-IN'
                };
                recognition.lang = langCodes[language] || 'en-US';
                recognition.start();
            }
        }
        
        function speakResponse(text, language) {
            // High-quality native speech synthesis
            if (speechSynthesis) {
                speechSynthesis.cancel();
                
                const utterance = new SpeechSynthesisUtterance(text);
                const voices = speechSynthesis.getVoices();
                
                // Better voice selection for natural sound
                let voice = null;
                if (language === 'hi') {
                    // Prefer Google Hindi voices if available
                    voice = voices.find(v => v.name.includes('Google') && v.lang.startsWith('hi')) ||
                           voices.find(v => v.lang === 'hi-IN') ||
                           voices.find(v => v.lang.startsWith('hi'));
                } else {
                    // Prefer Google or natural English voices
                    voice = voices.find(v => v.name.includes('Google') && v.lang.startsWith('en')) ||
                           voices.find(v => v.name.includes('Samantha') || v.name.includes('Alex')) ||
                           voices.find(v => v.lang === 'en-US' || v.lang === 'en-GB');
                }
                
                if (voice) {
                    utterance.voice = voice;
                    console.log(`Using voice: ${voice.name} (${voice.lang})`);
                }
                
                // Optimized parameters for natural sound
                utterance.rate = language === 'hi' ? 0.75 : 0.85;
                utterance.pitch = 0.95;
                utterance.volume = 0.9;
                
                utterance.onstart = function() {
                    console.log(`Speaking in ${language}: ${text.substring(0, 50)}...`);
                };
                
                utterance.onerror = function(event) {
                    console.error('Speech synthesis error:', event.error);
                };
                
                speechSynthesis.speak(utterance);
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
                    
                    // Speak the response if voice was used for input
                    if (voiceInputUsed) {
                        speakResponse(result.response.text, language);
                        voiceInputUsed = false; // Reset flag
                    }
                    
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
            
            const messageContent = document.createElement('div');
            messageContent.className = 'message-content';
            messageContent.innerHTML = text.replace(/\n/g, '<br>');
            
            messageDiv.appendChild(messageContent);
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
        
        // Initialize auto-resize textarea
        document.addEventListener('DOMContentLoaded', function() {
            // Auto-resize textarea
            const textarea = document.getElementById('queryInput');
            textarea.addEventListener('input', function() {
                this.style.height = 'auto';
                this.style.height = Math.min(this.scrollHeight, 120) + 'px';
            });
            
            console.log('My Telecom AI Agent initialized successfully');
        });
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


class TTSRequest(BaseModel):
    text: str
    language: str = "en"
    voice_id: str = None

class VisualRequest(BaseModel):
    visual_type: str  # "plan_comparison", "account_summary", "recharge_receipt"
    data: dict
    language: str = "en"


@app.post("/api/tts")
async def text_to_speech(request: TTSRequest):
    """Generate natural voice using Edge-TTS"""
    try:
        # Select appropriate voice based on language and voice preference
        voice_mapping = {
            "en": {
                "aria": "en-US-AriaNeural",       # Female - Professional
                "jenny": "en-US-JennyNeural",     # Female - Conversational  
                "guy": "en-US-GuyNeural",         # Male - Professional
                "davis": "en-US-DavisNeural",     # Male - Natural
            },
            "hi": {
                "swara": "hi-IN-SwaraNeural",     # Female - Standard
                "madhur": "hi-IN-MadhurNeural",   # Male - Natural
                "kavya": "hi-IN-KavyaNeural",     # Female - Young
                "aarohi": "hi-IN-AarohiNeural",   # Female - Child-like
            },
            "ta": {
                "pallavi": "ta-IN-PallaviNeural", # Female - Standard
                "valluvar": "ta-IN-ValluvarNeural", # Male - Professional
                "shreya": "ta-IN-ShreyaNeural",   # Female - Young
            },
            "te": {
                "shruti": "te-IN-ShrutiNeural",   # Female - Standard
                "mohan": "te-IN-MohanNeural",     # Male - Natural
                "nandhini": "te-IN-NandhiniNeural", # Female - Expressive
            }
        }
        
        # Get voice ID from request or use default
        language_voices = voice_mapping.get(request.language, voice_mapping["en"])
        if request.voice_id and request.voice_id in language_voices:
            selected_voice = language_voices[request.voice_id]
        else:
            # Use first voice as default
            selected_voice = list(language_voices.values())[0]
        
        # Create TTS communication
        communicate = edge_tts.Communicate(request.text, selected_voice)
        
        # Generate audio
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        
        if not audio_data:
            raise HTTPException(status_code=500, detail="No audio data generated")
        
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/webm",
            headers={
                "Content-Disposition": "attachment; filename=speech.webm",
                "Content-Type": "audio/webm"
            }
        )
        
    except Exception as e:
        print(f"Edge-TTS Error: {e}")
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {str(e)}")


@app.post("/api/generate-visual")
async def generate_visual_response(request: VisualRequest):
    """Generate dynamic visual responses using PIL"""
    try:
        if request.visual_type == "plan_comparison":
            return generate_plan_comparison_card(request.data, request.language)
        elif request.visual_type == "account_summary":
            return generate_account_summary_card(request.data, request.language)
        elif request.visual_type == "recharge_receipt":
            return generate_recharge_receipt_card(request.data, request.language)
        else:
            raise HTTPException(status_code=400, detail="Invalid visual type")
            
    except Exception as e:
        print(f"Visual Generation Error: {e}")
        raise HTTPException(status_code=500, detail=f"Visual generation failed: {str(e)}")

def generate_plan_comparison_card(data, language="en"):
    """Generate a plan comparison visual card"""
    # Create image with modern design
    width, height = 800, 400
    img = Image.new('RGB', (width, height), color='#f8fafc')
    draw = ImageDraw.Draw(img)
    
    # Try to load system font, fallback to default
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        text_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
        price_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        price_font = ImageFont.load_default()
    
    # Draw header
    draw.rectangle([0, 0, width, 80], fill='#3b82f6')
    title = "📋 Plan Comparison" if language == "en" else "📋 योजना तुलना"
    draw.text((20, 25), title, fill='white', font=title_font)
    
    # Sample plans data
    plans = data.get('plans', [
        {"name": "Basic Plan", "price": "₹199", "features": ["2GB Daily", "Unlimited Calls"]},
        {"name": "Premium Plan", "price": "₹399", "features": ["4GB Daily", "Unlimited Calls", "Free Roaming"]}
    ])
    
    # Draw plan cards
    x_offset = 50
    for i, plan in enumerate(plans[:2]):
        card_x = x_offset + (i * 350)
        card_y = 120
        
        # Plan card background
        draw.rectangle([card_x, card_y, card_x + 300, card_y + 220], 
                      fill='white', outline='#e2e8f0', width=2)
        
        # Plan name
        draw.text((card_x + 20, card_y + 20), plan['name'], fill='#1e293b', font=price_font)
        
        # Plan price
        draw.text((card_x + 20, card_y + 60), plan['price'], fill='#059669', font=price_font)
        
        # Features
        for j, feature in enumerate(plan.get('features', [])[:3]):
            draw.text((card_x + 20, card_y + 100 + (j * 25)), 
                     f"✓ {feature}", fill='#64748b', font=text_font)
    
    # Convert to base64
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    
    return {"image": f"data:image/png;base64,{img_base64}", "type": "plan_comparison"}

def generate_account_summary_card(data, language="en"):
    """Generate account summary visual card"""
    width, height = 600, 300
    img = Image.new('RGB', (width, height), color='#f8fafc')
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
        text_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    # Header
    draw.rectangle([0, 0, width, 60], fill='#6366f1')
    title = "📊 Account Summary" if language == "en" else "📊 खाता सारांश"
    draw.text((20, 18), title, fill='white', font=title_font)
    
    # Account details
    balance = data.get('balance', '₹156.50')
    data_left = data.get('data_left', '2.5 GB')
    validity = data.get('validity', '15 days')
    
    details = [
        f"💰 Balance: {balance}",
        f"📶 Data Left: {data_left}",
        f"📅 Validity: {validity}"
    ]
    
    for i, detail in enumerate(details):
        draw.text((30, 90 + (i * 40)), detail, fill='#1e293b', font=text_font)
    
    # Convert to base64
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    
    return {"image": f"data:image/png;base64,{img_base64}", "type": "account_summary"}

def generate_recharge_receipt_card(data, language="en"):
    """Generate recharge receipt visual card"""
    width, height = 500, 400
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 18)
        text_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
    
    # Header
    draw.rectangle([0, 0, width, 50], fill='#10b981')
    title = "✅ Recharge Successful" if language == "en" else "✅ रिचार्ज सफल"
    draw.text((20, 15), title, fill='white', font=title_font)
    
    # Receipt details
    amount = data.get('amount', '₹199')
    phone = data.get('phone', '9876543210')
    transaction_id = data.get('transaction_id', 'TXN123456789')
    timestamp = data.get('timestamp', '2024-08-21 15:30:45')
    
    details = [
        f"📱 Phone: {phone}",
        f"💵 Amount: {amount}",
        f"🆔 Transaction: {transaction_id}",
        f"⏰ Time: {timestamp}"
    ]
    
    for i, detail in enumerate(details):
        draw.text((30, 80 + (i * 35)), detail, fill='#1e293b', font=text_font)
    
    # Success message
    success_msg = "Thank you for your recharge!" if language == "en" else "रिचार्ज के लिए धन्यवाद!"
    draw.text((30, 280), success_msg, fill='#059669', font=title_font)
    
    # Convert to base64
    img_buffer = io.BytesIO()
    img.save(img_buffer, format='PNG')
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
    
    return {"image": f"data:image/png;base64,{img_base64}", "type": "recharge_receipt"}

@app.get("/api/voices")
async def get_available_voices():
    """Get list of available Edge-TTS voices"""
    return {
        "voices": {
            "en": [
                {"id": "aria", "name": "Aria (Professional Female)", "description": "Clear, professional voice"},
                {"id": "jenny", "name": "Jenny (Conversational Female)", "description": "Natural, friendly tone"},
                {"id": "guy", "name": "Guy (Professional Male)", "description": "Authoritative male voice"},
                {"id": "davis", "name": "Davis (Natural Male)", "description": "Warm, approachable tone"}
            ],
            "hi": [
                {"id": "swara", "name": "स्वरा (Standard Female)", "description": "Standard Hindi female voice"},
                {"id": "madhur", "name": "मधुर (Natural Male)", "description": "Natural Hindi male voice"},
                {"id": "kavya", "name": "काव्या (Young Female)", "description": "Youthful, energetic tone"},
                {"id": "aarohi", "name": "आरोही (Expressive Female)", "description": "Expressive, warm voice"}
            ],
            "ta": [
                {"id": "pallavi", "name": "பல்லவி (Standard Female)", "description": "Standard Tamil female voice"},
                {"id": "valluvar", "name": "वल्लुवर (Professional Male)", "description": "Professional Tamil male voice"},
                {"id": "shreya", "name": "श्रेया (Young Female)", "description": "Youthful Tamil voice"}
            ],
            "te": [
                {"id": "shruti", "name": "శ్రుతి (Standard Female)", "description": "Standard Telugu female voice"},
                {"id": "mohan", "name": "మోహన్ (Natural Male)", "description": "Natural Telugu male voice"},
                {"id": "nandhini", "name": "నందిని (Expressive Female)", "description": "Expressive Telugu voice"}
            ]
        }
    }


if __name__ == "__main__":
    print("\n🚀 Starting My Telecom AI Agent Web Demo")
    print("=" * 60)
    print("📱 Production-scale customer service AI demonstration")
    print("🌐 Web interface: http://localhost:8000")
    print("🎯 Features: Multi-language, Tool integration, Real-time metrics")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")