#!/usr/bin/env python3
"""
Simplified Agentic Security Operations Demo

This demo shows the agentic AI capabilities without complex dependencies,
perfect for testing and interview demonstrations.
"""

import streamlit as st
import time
import json
from datetime import datetime
from typing import Dict, Any, List

def main():
    """Streamlit interface for agentic AI demonstration"""
    
    st.set_page_config(
        page_title="🤖 Agentic Security Operations - IHCL Portfolio",
        page_icon="🏨",
        layout="wide"
    )
    
    st.title("🤖 Agentic AI Security Operations System")
    st.markdown("**Live demonstration of autonomous hotel security incident response**")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.markdown("### 🎯 Demo Features")
        st.markdown("""
        ✅ **Autonomous Decision Making**  
        ✅ **Multi-System Integration**  
        ✅ **Real-Time Tool Execution**  
        ✅ **Business Impact Tracking**  
        ✅ **Human Escalation Workflows**
        """)
    
    # Main interface
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("🚨 Security Incident Simulator")
        
        # Predefined incident scenarios
        incident_scenarios = {
            "Unauthorized Room Access": {
                "type": "unauthorized_access",
                "description": "Guest attempting to access Room 315 after checkout, keycard still active",
                "location": "Room 315, Floor 3",
                "priority": "high"
            },
            "Payment Fraud Detection": {
                "type": "payment_fraud",
                "description": "Multiple failed payment attempts detected for booking ID BK-7891, suspicious IP address",
                "location": "Front Desk, Payment Terminal 2",
                "priority": "critical"
            },
            "Data Privacy Breach": {
                "type": "data_breach",
                "description": "Potential PII exposure detected in guest services system logs",
                "location": "IT Server Room, Database Cluster",
                "priority": "critical"
            },
            "Physical Security Alert": {
                "type": "physical_security",
                "description": "Motion detected in restricted spa area during closed hours",
                "location": "Spa Wellness Center, Floor 2",
                "priority": "medium"
            }
        }
        
        selected_scenario = st.selectbox("Select Incident Scenario:", list(incident_scenarios.keys()))
        incident_data = incident_scenarios[selected_scenario]
        
        # Allow customization
        st.subheader("Incident Details")
        incident_type = st.text_input("Incident Type", value=incident_data["type"])
        description = st.text_area("Description", value=incident_data["description"])
        location = st.text_input("Location", value=incident_data["location"])
        priority = st.selectbox("Priority", ["low", "medium", "high", "critical"], 
                               index=["low", "medium", "high", "critical"].index(incident_data["priority"]))
        
        # Trigger button
        if st.button("🚀 Launch Autonomous Response", type="primary", use_container_width=True):
            st.session_state.incident_triggered = True
            st.session_state.incident_data = {
                "type": incident_type,
                "description": description,
                "location": location,
                "priority": priority
            }
    
    with col2:
        st.header("📊 Real-Time Agent Dashboard")
        
        if hasattr(st.session_state, 'incident_triggered') and st.session_state.incident_triggered:
            
            # Show live agent execution
            with st.container():
                st.info("🤖 Autonomous agent is now processing the incident...")
                
                # Create placeholders for live updates
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                # Simulate agentic workflow execution
                incident_result = simulate_agentic_response(st.session_state.incident_data, progress_bar, status_text)
                
                # Display results
                if incident_result:
                    display_incident_results(incident_result)
                
                st.session_state.incident_triggered = False
        
        else:
            # System status when idle
            st.info("🟢 Autonomous Security Agent ready to respond to incidents")
            
            with st.expander("🔧 System Capabilities", expanded=True):
                st.markdown("""
                **Hotel System Integrations:**
                - 🏨 Property Management System (PMS) 
                - 🔐 Access Control & Keycard Management
                - 📱 Multi-Channel Notification System
                - 🛡️ Security Monitoring & CCTV
                - 💰 Payment & Fraud Detection Systems
                
                **Autonomous Capabilities:**
                - 🧠 Multi-criteria risk assessment
                - ⚡ Real-time decision making
                - 🔄 Multi-step workflow execution
                - 📈 Business impact optimization
                - 👥 Intelligent human escalation
                """)
    
    # Performance Metrics Section
    st.markdown("---")
    st.header("📈 Agent Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Task Success Rate", "87%", "+5% vs baseline")
    with col2:
        st.metric("Avg Response Time", "2.3s", "-40% vs manual")
    with col3:
        st.metric("Automation Rate", "85%", "+12% this month")
    with col4:
        st.metric("Cost per Incident", "₹125", "-60% vs traditional")


def simulate_agentic_response(incident_data: Dict[str, Any], progress_bar, status_text) -> Dict[str, Any]:
    """Simulate realistic agentic AI workflow execution"""
    
    incident_id = f"INC-{datetime.now().strftime('%Y%m%d')}-{int(time.time()) % 10000}"
    
    # Simulate workflow steps with real-time updates
    steps = [
        ("🧠 Analyzing incident and assessing risk...", 0.15),
        ("⚖️ Making autonomous decisions (94% confidence)...", 0.30),
        ("📋 Planning coordinated response actions...", 0.45),
        ("🔧 Executing tools across hotel systems...", 0.70),
        ("📢 Coordinating notifications and alerts...", 0.85),
        ("✅ Monitoring outcomes and completing workflow...", 1.0)
    ]
    
    for step_text, progress in steps:
        status_text.text(step_text)
        progress_bar.progress(progress)
        time.sleep(1.5)  # Realistic execution timing
    
    # Determine actions based on incident type
    actions_completed = get_actions_for_incident_type(incident_data["type"])
    notifications_sent = get_notifications_for_incident_type(incident_data["type"])
    
    # Calculate business impact
    base_cost_prevented = {
        "unauthorized_access": 15000,
        "payment_fraud": 45000,
        "data_breach": 125000,
        "physical_security": 8000
    }
    
    return {
        "incident_id": incident_id,
        "response_status": "completed",
        "autonomous_actions_taken": len(actions_completed),
        "human_intervention_required": False,
        "response_time_seconds": 2.3,
        "automation_success_rate": 1.0,
        "business_impact": {
            "potential_loss_prevented": base_cost_prevented.get(incident_data["type"], 10000),
            "operational_efficiency_gain": "85%",
            "guest_satisfaction_maintained": "98%",
            "compliance_status": "Fully compliant"
        },
        "actions_summary": {
            "planned": len(actions_completed),
            "completed": actions_completed,
            "failed": []
        },
        "notifications_sent": notifications_sent,
        "reasoning_log": [
            f"Incident classified as {incident_data['priority']} priority {incident_data['type']}",
            f"Multi-criteria risk assessment completed in 0.3s",
            f"Decision confidence: 94% - proceeding with autonomous response",
            f"Executed {len(actions_completed)} coordinated actions across hotel systems",
            f"All system integrations successful - no human intervention required",
            f"Business impact: ₹{base_cost_prevented.get(incident_data['type'], 10000):,} potential loss prevented"
        ],
        "performance_metrics": {
            "decision_confidence": 0.94,
            "system_integrations": len(actions_completed),
            "escalation_level": 0
        }
    }


def get_actions_for_incident_type(incident_type: str) -> List[Dict[str, Any]]:
    """Get realistic actions based on incident type"""
    
    actions_map = {
        "unauthorized_access": [
            {
                "action_type": "access_control",
                "description": "Revoked keycard access for Room 315",
                "tool": "Access Control System",
                "result": "Success - Card ID GUEST_315_789 deactivated",
                "execution_time": "0.3s"
            },
            {
                "action_type": "room_management", 
                "description": "Updated room status to Security Hold",
                "tool": "Property Management System",
                "result": "Success - Room 315 marked for investigation",
                "execution_time": "0.5s"
            },
            {
                "action_type": "guest_notification",
                "description": "Contacted guest regarding checkout procedure",
                "tool": "Notification Orchestrator",
                "result": "Success - SMS sent to guest mobile",
                "execution_time": "0.8s"
            }
        ],
        "payment_fraud": [
            {
                "action_type": "fraud_analysis",
                "description": "Analyzed payment pattern and IP geolocation",
                "tool": "Fraud Detection System",
                "result": "Success - 92% fraud probability confirmed",
                "execution_time": "1.2s"
            },
            {
                "action_type": "payment_block",
                "description": "Blocked suspicious payment methods",
                "tool": "Payment Gateway",
                "result": "Success - 3 cards flagged and blocked",
                "execution_time": "0.6s"
            },
            {
                "action_type": "guest_verification",
                "description": "Initiated identity verification process",
                "tool": "Guest Services System",
                "result": "Success - Verification link sent to guest",
                "execution_time": "0.4s"
            }
        ],
        "data_breach": [
            {
                "action_type": "breach_containment",
                "description": "Isolated affected database cluster",
                "tool": "Database Management System",
                "result": "Success - Cluster DB-03 isolated",
                "execution_time": "0.7s"
            },
            {
                "action_type": "data_audit",
                "description": "Scanned for PII exposure patterns",
                "tool": "Data Privacy Scanner",
                "result": "Success - 247 records flagged for review",
                "execution_time": "2.1s"
            },
            {
                "action_type": "regulatory_notification",
                "description": "Prepared DPDP compliance notification",
                "tool": "Compliance Management",
                "result": "Success - 72-hour notice prepared",
                "execution_time": "0.5s"
            }
        ],
        "physical_security": [
            {
                "action_type": "area_assessment",
                "description": "Activated motion sensors and cameras",
                "tool": "Security Monitoring System",
                "result": "Success - Live feed enabled for Spa area",
                "execution_time": "0.4s"
            },
            {
                "action_type": "access_restriction",
                "description": "Temporary lockdown of spa wellness center",
                "tool": "Access Control System", 
                "result": "Success - Area secured for 30 minutes",
                "execution_time": "0.6s"
            }
        ]
    }
    
    return actions_map.get(incident_type, [])


def get_notifications_for_incident_type(incident_type: str) -> List[Dict[str, str]]:
    """Get realistic notifications based on incident type"""
    
    notifications_map = {
        "unauthorized_access": [
            {"recipient": "Security Manager", "channel": "SMS", "status": "Delivered"},
            {"recipient": "Housekeeping Supervisor", "channel": "Slack", "status": "Read"},
            {"recipient": "Guest Relations", "channel": "Email", "status": "Delivered"}
        ],
        "payment_fraud": [
            {"recipient": "Finance Manager", "channel": "Phone Call", "status": "Answered"},
            {"recipient": "General Manager", "channel": "SMS", "status": "Delivered"},
            {"recipient": "Compliance Officer", "channel": "Email", "status": "Delivered"}
        ],
        "data_breach": [
            {"recipient": "Chief Security Officer", "channel": "Phone Call", "status": "Answered"},
            {"recipient": "Legal Counsel", "channel": "Email", "status": "Delivered"},
            {"recipient": "Data Protection Officer", "channel": "SMS", "status": "Delivered"}
        ],
        "physical_security": [
            {"recipient": "Security Officer Kumar", "channel": "Mobile App", "status": "Acknowledged"},
            {"recipient": "Spa Manager", "channel": "WhatsApp", "status": "Read"}
        ]
    }
    
    return notifications_map.get(incident_type, [])


def display_incident_results(result: Dict[str, Any]):
    """Display the results of the agentic workflow execution"""
    
    st.success(f"✅ Incident {result['incident_id']} resolved autonomously in {result['response_time_seconds']}s")
    
    # Display metrics
    st.subheader("📊 Execution Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Response Time", f"{result['response_time_seconds']}s", "🚀 Real-time")
    with col2:
        st.metric("Actions Taken", result['autonomous_actions_taken'], "🤖 Autonomous")
    with col3:
        st.metric("Success Rate", f"{result['automation_success_rate']:.0%}", "✅ Perfect")
    with col4:
        st.metric("Business Impact", f"₹{result['business_impact']['potential_loss_prevented']:,}", "💰 Prevented")
    
    # Display actions taken
    st.subheader("🔧 Autonomous Actions Executed")
    
    for i, action in enumerate(result['actions_summary']['completed']):
        with st.expander(f"Action {i+1}: {action['description']}", expanded=True):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.write(f"**Tool Used:** {action['tool']}")
                st.write(f"**Result:** {action['result']}")
            with col2:
                st.write(f"**Execution Time:** {action['execution_time']}")
                st.success("✅ Completed")
    
    st.subheader("📢 Notifications Coordinated")
    for notification in result['notifications_sent']:
        st.write(f"• {notification['recipient']} via {notification['channel']} - {notification['status']}")
    
    st.subheader("🧠 Agent Reasoning Log")
    for reasoning in result['reasoning_log']:
        st.write(f"• {reasoning}")


if __name__ == "__main__":
    main()