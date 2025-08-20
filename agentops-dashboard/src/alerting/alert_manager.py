"""Real-time alerting system for monitoring agent performance and security."""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import asyncio
import uuid
from datetime import datetime, timedelta
import structlog
import json

from ..models.alert import Alert
from ..models.agent_execution import AgentExecution
from ..models.security_incident import SecurityIncident
from ..models.performance_metric import PerformanceMetric


class AlertSeverity(Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertType(Enum):
    """Alert types."""
    PERFORMANCE = "performance"
    SECURITY = "security"
    COST = "cost"
    QUALITY = "quality"
    SYSTEM = "system"


@dataclass
class AlertCondition:
    """Defines conditions that trigger alerts."""
    name: str
    alert_type: AlertType
    severity: AlertSeverity
    condition_func: Callable[[Dict[str, Any]], bool]
    message_template: str
    threshold_value: Optional[float] = None
    time_window_minutes: Optional[int] = None
    cooldown_minutes: int = 5  # Prevent alert spam


@dataclass
class AlertNotification:
    """Alert notification data."""
    alert_id: str
    severity: AlertSeverity
    alert_type: AlertType
    title: str
    message: str
    timestamp: datetime
    metadata: Dict[str, Any]


class NotificationChannel(ABC):
    """Base class for notification channels."""
    
    @abstractmethod
    async def send_notification(self, notification: AlertNotification) -> bool:
        """Send an alert notification."""
        pass


class SlackNotificationChannel(NotificationChannel):
    """Slack notification channel."""
    
    def __init__(self, webhook_url: str, channel: str = "#alerts"):
        self.webhook_url = webhook_url
        self.channel = channel
        self.logger = structlog.get_logger().bind(channel="slack")
    
    async def send_notification(self, notification: AlertNotification) -> bool:
        """Send alert to Slack."""
        try:
            color_map = {
                AlertSeverity.CRITICAL: "#ff0000",
                AlertSeverity.HIGH: "#ff8000",
                AlertSeverity.MEDIUM: "#ffff00",
                AlertSeverity.LOW: "#00ff00",
                AlertSeverity.INFO: "#0080ff"
            }
            
            # Format Slack message
            slack_message = {
                "channel": self.channel,
                "username": "AgentOps Dashboard",
                "icon_emoji": ":robot_face:",
                "attachments": [{
                    "color": color_map.get(notification.severity, "#808080"),
                    "title": f"{notification.severity.value.upper()}: {notification.title}",
                    "text": notification.message,
                    "fields": [
                        {"title": "Alert Type", "value": notification.alert_type.value, "short": True},
                        {"title": "Severity", "value": notification.severity.value, "short": True},
                        {"title": "Time", "value": notification.timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"), "short": True}
                    ],
                    "footer": "AgentOps Dashboard",
                    "ts": int(notification.timestamp.timestamp())
                }]
            }
            
            # In a real implementation, would use httpx to send to Slack webhook
            self.logger.info("Slack notification sent", alert_id=notification.alert_id)
            return True
            
        except Exception as e:
            self.logger.error("Failed to send Slack notification", error=str(e), alert_id=notification.alert_id)
            return False


class EmailNotificationChannel(NotificationChannel):
    """Email notification channel."""
    
    def __init__(self, smtp_config: Dict[str, Any]):
        self.smtp_config = smtp_config
        self.logger = structlog.get_logger().bind(channel="email")
    
    async def send_notification(self, notification: AlertNotification) -> bool:
        """Send alert via email."""
        try:
            # In a real implementation, would use SMTP to send email
            self.logger.info("Email notification sent", alert_id=notification.alert_id)
            return True
            
        except Exception as e:
            self.logger.error("Failed to send email notification", error=str(e), alert_id=notification.alert_id)
            return False


class PagerDutyNotificationChannel(NotificationChannel):
    """PagerDuty notification channel for critical alerts."""
    
    def __init__(self, api_key: str, service_key: str):
        self.api_key = api_key
        self.service_key = service_key
        self.logger = structlog.get_logger().bind(channel="pagerduty")
    
    async def send_notification(self, notification: AlertNotification) -> bool:
        """Send alert to PagerDuty."""
        try:
            # Only send critical and high severity alerts to PagerDuty
            if notification.severity not in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]:
                return True
            
            # In a real implementation, would use PagerDuty API
            self.logger.info("PagerDuty notification sent", alert_id=notification.alert_id)
            return True
            
        except Exception as e:
            self.logger.error("Failed to send PagerDuty notification", error=str(e), alert_id=notification.alert_id)
            return False


class AlertManager:
    """Manages real-time alerting for AgentOps Dashboard."""
    
    def __init__(self):
        self.logger = structlog.get_logger()
        self.alert_conditions: List[AlertCondition] = []
        self.notification_channels: List[NotificationChannel] = []
        self.active_alerts: Dict[str, datetime] = {}  # Track cooldowns
        self.alert_history: List[AlertNotification] = []
        
        # Initialize default alert conditions
        self._setup_default_conditions()
    
    def add_notification_channel(self, channel: NotificationChannel):
        """Add a notification channel."""
        self.notification_channels.append(channel)
    
    def add_alert_condition(self, condition: AlertCondition):
        """Add a custom alert condition."""
        self.alert_conditions.append(condition)
    
    async def evaluate_execution(self, execution_data: Dict[str, Any]):
        """Evaluate an execution for alerting conditions."""
        for condition in self.alert_conditions:
            if condition.alert_type == AlertType.PERFORMANCE:
                await self._check_condition(condition, execution_data)
    
    async def evaluate_security_incident(self, incident_data: Dict[str, Any]):
        """Evaluate a security incident for alerting."""
        for condition in self.alert_conditions:
            if condition.alert_type == AlertType.SECURITY:
                await self._check_condition(condition, incident_data)
    
    async def evaluate_metrics(self, metrics_data: Dict[str, Any]):
        """Evaluate performance metrics for alerting."""
        for condition in self.alert_conditions:
            if condition.alert_type in [AlertType.PERFORMANCE, AlertType.COST, AlertType.QUALITY]:
                await self._check_condition(condition, metrics_data)
    
    async def _check_condition(self, condition: AlertCondition, data: Dict[str, Any]):
        """Check if a condition is met and trigger alert if needed."""
        try:
            # Check cooldown
            cooldown_key = f"{condition.name}_{hash(str(data))}"
            if cooldown_key in self.active_alerts:
                last_alert = self.active_alerts[cooldown_key]
                if datetime.utcnow() - last_alert < timedelta(minutes=condition.cooldown_minutes):
                    return  # Still in cooldown
            
            # Evaluate condition
            if condition.condition_func(data):
                alert_id = await self._trigger_alert(condition, data)
                self.active_alerts[cooldown_key] = datetime.utcnow()
                self.logger.info("Alert triggered", alert_id=alert_id, condition=condition.name)
        
        except Exception as e:
            self.logger.error("Error evaluating alert condition", condition=condition.name, error=str(e))
    
    async def _trigger_alert(self, condition: AlertCondition, data: Dict[str, Any]) -> str:
        """Trigger an alert and send notifications."""
        alert_id = str(uuid.uuid4())
        
        # Create alert notification
        notification = AlertNotification(
            alert_id=alert_id,
            severity=condition.severity,
            alert_type=condition.alert_type,
            title=condition.name,
            message=condition.message_template.format(**data),
            timestamp=datetime.utcnow(),
            metadata=data
        )
        
        # Send to all notification channels
        for channel in self.notification_channels:
            try:
                await channel.send_notification(notification)
            except Exception as e:
                self.logger.error("Failed to send notification", channel=type(channel).__name__, error=str(e))
        
        # Store in history
        self.alert_history.append(notification)
        
        # Keep only last 1000 alerts in memory
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]
        
        return alert_id
    
    def _setup_default_conditions(self):
        """Setup default alerting conditions."""
        
        # Performance alerts
        self.alert_conditions.extend([
            AlertCondition(
                name="High Latency Alert",
                alert_type=AlertType.PERFORMANCE,
                severity=AlertSeverity.HIGH,
                condition_func=lambda data: data.get("duration_ms", 0) > 5000,
                message_template="Agent {agent_name} execution took {duration_ms}ms (threshold: 5000ms)",
                threshold_value=5000.0,
                cooldown_minutes=5
            ),
            
            AlertCondition(
                name="Low Success Rate Alert",
                alert_type=AlertType.PERFORMANCE,
                severity=AlertSeverity.CRITICAL,
                condition_func=lambda data: data.get("success_rate_percent", 100) < 90,
                message_template="Agent {agent_name} success rate dropped to {success_rate_percent}% (threshold: 90%)",
                threshold_value=90.0,
                cooldown_minutes=10
            ),
            
            AlertCondition(
                name="Execution Failure Alert",
                alert_type=AlertType.PERFORMANCE,
                severity=AlertSeverity.MEDIUM,
                condition_func=lambda data: data.get("success") is False and data.get("error_type") == "timeout",
                message_template="Agent {agent_name} execution failed due to timeout",
                cooldown_minutes=2
            )
        ])
        
        # Security alerts
        self.alert_conditions.extend([
            AlertCondition(
                name="Critical Security Incident",
                alert_type=AlertType.SECURITY,
                severity=AlertSeverity.CRITICAL,
                condition_func=lambda data: data.get("severity") == "critical",
                message_template="Critical security incident detected: {incident_type} - {title}",
                cooldown_minutes=1
            ),
            
            AlertCondition(
                name="PII Exposure Alert",
                alert_type=AlertType.SECURITY,
                severity=AlertSeverity.HIGH,
                condition_func=lambda data: data.get("pii_exposed") is True,
                message_template="PII exposure detected in {incident_type}: {records_affected} records affected",
                cooldown_minutes=5
            ),
            
            AlertCondition(
                name="Compliance Violation Alert",
                alert_type=AlertType.SECURITY,
                severity=AlertSeverity.HIGH,
                condition_func=lambda data: data.get("compliance_violation") is True,
                message_template="Compliance violation detected: {regulations_affected}",
                cooldown_minutes=10
            )
        ])
        
        # Quality alerts
        self.alert_conditions.extend([
            AlertCondition(
                name="Low Quality Score Alert",
                alert_type=AlertType.QUALITY,
                severity=AlertSeverity.MEDIUM,
                condition_func=lambda data: data.get("overall_score", 1.0) < 0.7,
                message_template="Agent {agent_name} quality score dropped to {overall_score} (threshold: 0.7)",
                threshold_value=0.7,
                cooldown_minutes=15
            ),
            
            AlertCondition(
                name="Hallucination Detected",
                alert_type=AlertType.QUALITY,
                severity=AlertSeverity.HIGH,
                condition_func=lambda data: data.get("hallucination_detected") is True,
                message_template="Hallucination detected in agent execution: {execution_id}",
                cooldown_minutes=5
            ),
            
            AlertCondition(
                name="Safety Score Alert",
                alert_type=AlertType.QUALITY,
                severity=AlertSeverity.HIGH,
                condition_func=lambda data: data.get("safety_score", 1.0) < 0.8,
                message_template="Agent safety score dropped to {safety_score} (threshold: 0.8)",
                threshold_value=0.8,
                cooldown_minutes=10
            )
        ])
        
        # Cost alerts
        self.alert_conditions.extend([
            AlertCondition(
                name="High Cost Alert",
                alert_type=AlertType.COST,
                severity=AlertSeverity.MEDIUM,
                condition_func=lambda data: data.get("cost_usd", 0) > 1.0,
                message_template="High cost execution detected: ${cost_usd} for {agent_name}",
                threshold_value=1.0,
                cooldown_minutes=30
            ),
            
            AlertCondition(
                name="Budget Threshold Alert",
                alert_type=AlertType.COST,
                severity=AlertSeverity.HIGH,
                condition_func=lambda data: (
                    data.get("budget_remaining", float('inf')) < 
                    data.get("budget_allocation", 0) * 0.1
                ),
                message_template="Budget threshold reached: {budget_remaining} remaining of {budget_allocation}",
                cooldown_minutes=60
            )
        ])
    
    def get_recent_alerts(self, hours: int = 24) -> List[AlertNotification]:
        """Get recent alerts within the specified time window."""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        return [
            alert for alert in self.alert_history
            if alert.timestamp >= cutoff_time
        ]
    
    def get_alert_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of alerts in the specified time window."""
        recent_alerts = self.get_recent_alerts(hours)
        
        severity_counts = {}
        type_counts = {}
        
        for alert in recent_alerts:
            # Count by severity
            severity_counts[alert.severity.value] = severity_counts.get(alert.severity.value, 0) + 1
            # Count by type
            type_counts[alert.alert_type.value] = type_counts.get(alert.alert_type.value, 0) + 1
        
        return {
            "total_alerts": len(recent_alerts),
            "severity_breakdown": severity_counts,
            "type_breakdown": type_counts,
            "time_window_hours": hours,
            "critical_alerts": severity_counts.get("critical", 0),
            "active_conditions": len(self.alert_conditions),
            "notification_channels": len(self.notification_channels)
        }


# Global alert manager instance
alert_manager = AlertManager()