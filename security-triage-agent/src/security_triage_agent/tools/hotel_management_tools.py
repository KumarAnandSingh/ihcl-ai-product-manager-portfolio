"""
Hotel Management System Integration Tools for Agentic Security Operations.

These tools provide real-time integration with hotel management systems including
PMS (Property Management System), access control, workforce management, and
guest services for autonomous security incident response.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from uuid import uuid4
from enum import Enum

from pydantic import BaseModel, Field
from langchain_core.tools import BaseTool
import httpx
import aioredis


class SystemStatus(str, Enum):
    """System status enumeration"""
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"
    ERROR = "error"


class RoomStatus(str, Enum):
    """Hotel room status enumeration"""
    OCCUPIED = "occupied"
    VACANT_CLEAN = "vacant_clean"
    VACANT_DIRTY = "vacant_dirty"
    OUT_OF_ORDER = "out_of_order"
    SECURITY_HOLD = "security_hold"
    MAINTENANCE = "maintenance"


class NotificationChannel(str, Enum):
    """Notification channel options"""
    SMS = "sms"
    EMAIL = "email"
    PHONE_CALL = "phone_call"
    SLACK = "slack"
    WHATSAPP = "whatsapp"
    PUSH_NOTIFICATION = "push_notification"


# Data Models

class GuestProfile(BaseModel):
    """Guest profile information"""
    guest_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    room_number: str
    check_in_date: datetime
    check_out_date: datetime
    guest_type: str  # VIP, Regular, Corporate, etc.
    preferences: Dict[str, Any] = Field(default_factory=dict)
    loyalty_status: str = "regular"
    special_requests: List[str] = Field(default_factory=list)
    security_notes: List[str] = Field(default_factory=list)


class AccessControlResult(BaseModel):
    """Access control operation result"""
    success: bool
    action: str
    card_id: str
    timestamp: datetime
    affected_areas: List[str] = Field(default_factory=list)
    rollback_token: Optional[str] = None
    expires_at: Optional[datetime] = None


class NotificationResult(BaseModel):
    """Notification delivery result"""
    success: bool
    channel: NotificationChannel
    recipient: str
    message_id: str
    delivery_status: str
    timestamp: datetime
    retry_count: int = 0
    estimated_delivery: Optional[datetime] = None


class TaskAssignment(BaseModel):
    """Security task assignment"""
    task_id: str
    staff_id: str
    staff_name: str
    task_type: str
    description: str
    priority: str
    location: str
    estimated_duration: int  # minutes
    assigned_at: datetime
    due_at: datetime
    status: str = "assigned"
    completion_notes: Optional[str] = None


# Hotel Management Tools

class PropertyManagementTool(BaseTool):
    """
    Direct integration with hotel Property Management System (PMS).
    Provides real-time access to guest information, room management, and incident tracking.
    """
    
    name: str = "property_management_system"
    description: str = "Interact with hotel PMS for guest data, room status, and incident management"
    
    def __init__(self, pms_api_url: str, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self.pms_api_url = pms_api_url.rstrip('/')
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        
        # Connection pool for async HTTP requests
        self.http_client = None
        
    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self.http_client is None:
            self.http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(10.0, connect=5.0),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
        return self.http_client
    
    async def get_guest_info(self, room_number: str) -> Optional[GuestProfile]:
        """
        Retrieve comprehensive guest information from PMS.
        
        Args:
            room_number: Hotel room number
            
        Returns:
            GuestProfile with complete guest information or None if not found
        """
        try:
            client = await self._get_http_client()
            
            response = await client.get(f"{self.pms_api_url}/api/v1/guests/by-room/{room_number}")
            response.raise_for_status()
            
            guest_data = response.json()
            if not guest_data:
                return None
            
            return GuestProfile(**guest_data)
            
        except httpx.HTTPError as e:
            self.logger.error(f"PMS API error getting guest info: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error getting guest info: {e}")
            return None
    
    async def update_room_status(self, room_number: str, status: RoomStatus, 
                               reason: str, duration_hours: Optional[int] = None) -> bool:
        """
        Update room status in PMS system.
        
        Args:
            room_number: Hotel room number
            status: New room status
            reason: Reason for status change
            duration_hours: How long status should remain (for temporary statuses)
            
        Returns:
            Success status
        """
        try:
            client = await self._get_http_client()
            
            payload = {
                "room_number": room_number,
                "status": status.value,
                "reason": reason,
                "updated_by": "security_agent",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if duration_hours:
                payload["expires_at"] = (datetime.utcnow() + timedelta(hours=duration_hours)).isoformat()
            
            response = await client.post(f"{self.pms_api_url}/api/v1/rooms/status", json=payload)
            response.raise_for_status()
            
            self.logger.info(f"Updated room {room_number} status to {status.value}: {reason}")
            return True
            
        except httpx.HTTPError as e:
            self.logger.error(f"PMS API error updating room status: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error updating room status: {e}")
            return False
    
    async def create_incident_note(self, guest_id: str, incident_summary: str, 
                                 incident_id: str) -> bool:
        """
        Add security incident note to guest profile.
        
        Args:
            guest_id: Guest identifier
            incident_summary: Brief incident description
            incident_id: Security incident reference ID
            
        Returns:
            Success status
        """
        try:
            client = await self._get_http_client()
            
            payload = {
                "guest_id": guest_id,
                "note_type": "security_incident",
                "summary": incident_summary,
                "incident_id": incident_id,
                "created_by": "security_agent",
                "created_at": datetime.utcnow().isoformat(),
                "priority": "high",
                "requires_followup": True
            }
            
            response = await client.post(f"{self.pms_api_url}/api/v1/guests/notes", json=payload)
            response.raise_for_status()
            
            self.logger.info(f"Added security incident note for guest {guest_id}")
            return True
            
        except httpx.HTTPError as e:
            self.logger.error(f"PMS API error creating incident note: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error creating incident note: {e}")
            return False
    
    async def get_room_occupancy_history(self, room_number: str, 
                                       hours_back: int = 48) -> List[Dict[str, Any]]:
        """
        Get room occupancy history for investigation purposes.
        
        Args:
            room_number: Hotel room number
            hours_back: How many hours of history to retrieve
            
        Returns:
            List of occupancy records
        """
        try:
            client = await self._get_http_client()
            
            start_time = (datetime.utcnow() - timedelta(hours=hours_back)).isoformat()
            
            response = await client.get(
                f"{self.pms_api_url}/api/v1/rooms/{room_number}/occupancy-history",
                params={"start_time": start_time}
            )
            response.raise_for_status()
            
            return response.json().get("occupancy_records", [])
            
        except httpx.HTTPError as e:
            self.logger.error(f"PMS API error getting occupancy history: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error getting occupancy history: {e}")
            return []


class AccessControlTool(BaseTool):
    """
    Real-time integration with hotel access control systems.
    Provides keycard management, area access control, and emergency lockdown capabilities.
    """
    
    name: str = "access_control_system"
    description: str = "Manage hotel access control systems, keycards, and security locks"
    
    def __init__(self, access_control_api_url: str, api_key: str, **kwargs):
        super().__init__(**kwargs)
        self.api_url = access_control_api_url.rstrip('/')
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        self.http_client = None
    
    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client"""
        if self.http_client is None:
            self.http_client = httpx.AsyncClient(
                timeout=httpx.Timeout(10.0, connect=5.0),
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
            )
        return self.http_client
    
    async def revoke_access(self, card_id: str, reason: str) -> AccessControlResult:
        """
        Immediately revoke keycard access across all hotel areas.
        
        Args:
            card_id: Keycard identifier
            reason: Reason for revocation
            
        Returns:
            AccessControlResult with operation details
        """
        try:
            client = await self._get_http_client()
            
            payload = {
                "card_id": card_id,
                "action": "revoke",
                "reason": reason,
                "revoked_by": "security_agent",
                "timestamp": datetime.utcnow().isoformat()
            }
            
            response = await client.post(f"{self.api_url}/api/v1/access/revoke", json=payload)
            response.raise_for_status()
            
            result_data = response.json()
            
            self.logger.info(f"Revoked access for card {card_id}: {reason}")
            
            return AccessControlResult(
                success=True,
                action="revoke",
                card_id=card_id,
                timestamp=datetime.utcnow(),
                affected_areas=result_data.get("affected_areas", []),
                rollback_token=result_data.get("rollback_token")
            )
            
        except httpx.HTTPError as e:
            self.logger.error(f"Access control API error revoking access: {e}")
            return AccessControlResult(
                success=False,
                action="revoke",
                card_id=card_id,
                timestamp=datetime.utcnow()
            )
    
    async def create_temporary_access(self, staff_id: str, areas: List[str], 
                                    expires_in_hours: int = 4) -> AccessControlResult:
        """
        Create temporary access credentials for security staff.
        
        Args:
            staff_id: Staff member identifier
            areas: List of area codes for access
            expires_in_hours: Access duration in hours
            
        Returns:
            AccessControlResult with temporary access details
        """
        try:
            client = await self._get_http_client()
            
            expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
            
            payload = {
                "staff_id": staff_id,
                "access_areas": areas,
                "expires_at": expires_at.isoformat(),
                "access_type": "temporary_security",
                "created_by": "security_agent",
                "reason": "security_incident_response"
            }
            
            response = await client.post(f"{self.api_url}/api/v1/access/temporary", json=payload)
            response.raise_for_status()
            
            result_data = response.json()
            
            return AccessControlResult(
                success=True,
                action="temporary_access",
                card_id=result_data.get("temp_card_id"),
                timestamp=datetime.utcnow(),
                affected_areas=areas,
                expires_at=expires_at
            )
            
        except httpx.HTTPError as e:
            self.logger.error(f"Access control API error creating temporary access: {e}")
            return AccessControlResult(
                success=False,
                action="temporary_access",
                card_id="",
                timestamp=datetime.utcnow()
            )
    
    async def lock_area(self, area_id: str, duration_minutes: int = 30, 
                       emergency: bool = False) -> AccessControlResult:
        """
        Lock down specific hotel area for security purposes.
        
        Args:
            area_id: Area identifier to lock down
            duration_minutes: How long to maintain lockdown
            emergency: Whether this is an emergency lockdown
            
        Returns:
            AccessControlResult with lockdown details
        """
        try:
            client = await self._get_http_client()
            
            expires_at = datetime.utcnow() + timedelta(minutes=duration_minutes)
            
            payload = {
                "area_id": area_id,
                "action": "lockdown",
                "duration_minutes": duration_minutes,
                "expires_at": expires_at.isoformat(),
                "emergency": emergency,
                "initiated_by": "security_agent",
                "reason": "security_incident_response"
            }
            
            response = await client.post(f"{self.api_url}/api/v1/areas/lockdown", json=payload)
            response.raise_for_status()
            
            result_data = response.json()
            
            lockdown_type = "Emergency" if emergency else "Standard"
            self.logger.warning(f"{lockdown_type} lockdown initiated for area {area_id} for {duration_minutes} minutes")
            
            return AccessControlResult(
                success=True,
                action="area_lockdown",
                card_id="",
                timestamp=datetime.utcnow(),
                affected_areas=[area_id],
                rollback_token=result_data.get("rollback_token"),
                expires_at=expires_at
            )
            
        except httpx.HTTPError as e:
            self.logger.error(f"Access control API error locking area: {e}")
            return AccessControlResult(
                success=False,
                action="area_lockdown",
                card_id="",
                timestamp=datetime.utcnow()
            )
    
    async def get_access_logs(self, card_id: str, hours_back: int = 24) -> List[Dict[str, Any]]:
        """
        Retrieve access logs for investigation.
        
        Args:
            card_id: Keycard identifier
            hours_back: Hours of history to retrieve
            
        Returns:
            List of access log entries
        """
        try:
            client = await self._get_http_client()
            
            start_time = (datetime.utcnow() - timedelta(hours=hours_back)).isoformat()
            
            response = await client.get(
                f"{self.api_url}/api/v1/access/logs/{card_id}",
                params={"start_time": start_time}
            )
            response.raise_for_status()
            
            return response.json().get("access_logs", [])
            
        except httpx.HTTPError as e:
            self.logger.error(f"Access control API error getting logs: {e}")
            return []


class NotificationOrchestratorTool(BaseTool):
    """
    Multi-channel notification system for coordinated incident response.
    Handles SMS, email, calls, Slack, and push notifications with intelligent routing.
    """
    
    name: str = "notification_orchestrator"
    description: str = "Send multi-channel notifications for security incident response coordination"
    
    def __init__(self, notification_config: Dict[str, Any], **kwargs):
        super().__init__(**kwargs)
        self.config = notification_config
        self.logger = logging.getLogger(__name__)
        
        # Initialize notification service clients
        self.notification_clients = {}
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize notification service clients"""
        # This would initialize actual service clients like Twilio, SendGrid, Slack, etc.
        # For demo purposes, we'll use mock clients
        
        self.notification_clients = {
            NotificationChannel.SMS: MockSMSClient(),
            NotificationChannel.EMAIL: MockEmailClient(),
            NotificationChannel.SLACK: MockSlackClient(),
            NotificationChannel.PHONE_CALL: MockPhoneClient(),
            NotificationChannel.WHATSAPP: MockWhatsAppClient(),
            NotificationChannel.PUSH_NOTIFICATION: MockPushClient()
        }
    
    async def notify_security_team(self, incident_id: str, priority: str, 
                                 location: str, summary: str) -> List[NotificationResult]:
        """
        Immediately notify the security team about an incident.
        
        Args:
            incident_id: Incident identifier
            priority: Incident priority level
            location: Incident location
            summary: Brief incident summary
            
        Returns:
            List of NotificationResult for each team member notified
        """
        # Get on-duty security team members
        security_team = await self._get_on_duty_security_team()
        
        message = self._format_security_alert_message(incident_id, priority, location, summary)
        
        notification_results = []
        
        for team_member in security_team:
            # Choose notification method based on priority and preferences
            channels = self._select_notification_channels(priority, team_member["preferences"])
            
            for channel in channels:
                try:
                    result = await self._send_notification(
                        channel=channel,
                        recipient=team_member["contact_info"][channel.value],
                        message=message,
                        priority=priority
                    )
                    notification_results.append(result)
                    
                except Exception as e:
                    self.logger.error(f"Failed to notify {team_member['name']} via {channel}: {e}")
                    notification_results.append(NotificationResult(
                        success=False,
                        channel=channel,
                        recipient=team_member["contact_info"].get(channel.value, "unknown"),
                        message_id="",
                        delivery_status="failed",
                        timestamp=datetime.utcnow()
                    ))
        
        return notification_results
    
    async def alert_management(self, incident_summary: str, escalation_level: int, 
                             business_impact: str) -> List[NotificationResult]:
        """
        Alert management team for high-priority incidents.
        
        Args:
            incident_summary: Detailed incident summary
            escalation_level: Management escalation level (1-5)
            business_impact: Description of business impact
            
        Returns:
            List of NotificationResult for management notifications
        """
        management_contacts = await self._get_management_contacts(escalation_level)
        
        message = self._format_management_alert_message(
            incident_summary, escalation_level, business_impact
        )
        
        notification_results = []
        
        for contact in management_contacts:
            # Management typically prefers phone calls for critical incidents
            channels = [NotificationChannel.PHONE_CALL, NotificationChannel.EMAIL]
            
            if escalation_level >= 4:  # Critical incidents
                channels.insert(0, NotificationChannel.SMS)
            
            for channel in channels:
                try:
                    result = await self._send_notification(
                        channel=channel,
                        recipient=contact["contact_info"][channel.value],
                        message=message,
                        priority="critical" if escalation_level >= 4 else "high"
                    )
                    notification_results.append(result)
                    
                    # For management, wait for acknowledgment before trying next method
                    if result.success and channel == NotificationChannel.PHONE_CALL:
                        break  # Phone call successful, no need for other channels
                        
                except Exception as e:
                    self.logger.error(f"Failed to alert management {contact['name']} via {channel}: {e}")
        
        return notification_results
    
    async def update_guest(self, guest_id: str, message: str, 
                          channel: Optional[NotificationChannel] = None) -> NotificationResult:
        """
        Send communication to guest regarding security incident.
        
        Args:
            guest_id: Guest identifier
            message: Message to send to guest
            channel: Preferred communication channel (or use guest preference)
            
        Returns:
            NotificationResult for guest communication
        """
        try:
            # Get guest contact preferences
            guest_info = await self._get_guest_contact_info(guest_id)
            
            if not guest_info:
                return NotificationResult(
                    success=False,
                    channel=NotificationChannel.EMAIL,
                    recipient="unknown",
                    message_id="",
                    delivery_status="guest_not_found",
                    timestamp=datetime.utcnow()
                )
            
            # Use specified channel or guest's preferred channel
            selected_channel = channel or guest_info.get("preferred_channel", NotificationChannel.EMAIL)
            recipient = guest_info["contact_info"].get(selected_channel.value)
            
            if not recipient:
                # Fall back to email if preferred channel not available
                selected_channel = NotificationChannel.EMAIL
                recipient = guest_info["contact_info"].get("email")
            
            if not recipient:
                return NotificationResult(
                    success=False,
                    channel=selected_channel,
                    recipient="unavailable",
                    message_id="",
                    delivery_status="no_contact_method",
                    timestamp=datetime.utcnow()
                )
            
            return await self._send_notification(
                channel=selected_channel,
                recipient=recipient,
                message=message,
                priority="normal"
            )
            
        except Exception as e:
            self.logger.error(f"Error updating guest {guest_id}: {e}")
            return NotificationResult(
                success=False,
                channel=NotificationChannel.EMAIL,
                recipient="unknown",
                message_id="",
                delivery_status="error",
                timestamp=datetime.utcnow()
            )
    
    async def _send_notification(self, channel: NotificationChannel, recipient: str, 
                               message: str, priority: str) -> NotificationResult:
        """Send notification through specified channel"""
        
        client = self.notification_clients.get(channel)
        if not client:
            raise ValueError(f"No client configured for channel: {channel}")
        
        message_id = str(uuid4())
        timestamp = datetime.utcnow()
        
        try:
            # Simulate notification sending
            success = await client.send(recipient, message, priority)
            
            return NotificationResult(
                success=success,
                channel=channel,
                recipient=recipient,
                message_id=message_id,
                delivery_status="sent" if success else "failed",
                timestamp=timestamp,
                estimated_delivery=timestamp + timedelta(seconds=30) if success else None
            )
            
        except Exception as e:
            self.logger.error(f"Notification sending failed: {e}")
            return NotificationResult(
                success=False,
                channel=channel,
                recipient=recipient,
                message_id=message_id,
                delivery_status="error",
                timestamp=timestamp
            )
    
    # Helper methods
    
    async def _get_on_duty_security_team(self) -> List[Dict[str, Any]]:
        """Get list of on-duty security team members"""
        # In production, this would query the workforce management system
        return [
            {
                "id": "SEC_001",
                "name": "Rajesh Kumar",
                "role": "Security Manager",
                "contact_info": {
                    "sms": "+91-9876543210",
                    "email": "rajesh.kumar@hotel.com",
                    "phone_call": "+91-9876543210"
                },
                "preferences": ["sms", "phone_call"]
            },
            {
                "id": "SEC_002", 
                "name": "Priya Sharma",
                "role": "Security Officer",
                "contact_info": {
                    "sms": "+91-9876543211",
                    "email": "priya.sharma@hotel.com",
                    "slack": "@priya.sharma"
                },
                "preferences": ["slack", "sms"]
            }
        ]
    
    async def _get_management_contacts(self, escalation_level: int) -> List[Dict[str, Any]]:
        """Get management contacts based on escalation level"""
        # Level 1-2: Department managers
        # Level 3-4: Senior management
        # Level 5: Executive leadership
        
        contacts = {
            1: [{"id": "MGR_001", "name": "Security Manager", "contact_info": {"email": "sec.mgr@hotel.com", "phone_call": "+91-98765-00001"}}],
            2: [{"id": "MGR_002", "name": "Operations Manager", "contact_info": {"email": "ops.mgr@hotel.com", "phone_call": "+91-98765-00002"}}],
            3: [{"id": "MGR_003", "name": "General Manager", "contact_info": {"email": "gm@hotel.com", "phone_call": "+91-98765-00003", "sms": "+91-98765-00003"}}],
            4: [{"id": "MGR_004", "name": "Regional Director", "contact_info": {"email": "regional@ihcl.com", "phone_call": "+91-98765-00004", "sms": "+91-98765-00004"}}],
            5: [{"id": "MGR_005", "name": "Chief Security Officer", "contact_info": {"email": "cso@ihcl.com", "phone_call": "+91-98765-00005", "sms": "+91-98765-00005"}}]
        }
        
        return contacts.get(escalation_level, contacts[1])
    
    async def _get_guest_contact_info(self, guest_id: str) -> Optional[Dict[str, Any]]:
        """Get guest contact information and preferences"""
        # In production, this would query the PMS system
        return {
            "guest_id": guest_id,
            "preferred_channel": NotificationChannel.EMAIL,
            "contact_info": {
                "email": "guest@example.com",
                "sms": "+91-9876543999"
            }
        }
    
    def _format_security_alert_message(self, incident_id: str, priority: str, 
                                     location: str, summary: str) -> str:
        """Format security team alert message"""
        return f"""
🚨 SECURITY ALERT - {priority.upper()}

Incident ID: {incident_id}
Location: {location}
Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

Summary: {summary}

Please respond immediately to assess and manage this incident.
Use incident ID {incident_id} for all communications.
        """.strip()
    
    def _format_management_alert_message(self, summary: str, escalation_level: int, 
                                       business_impact: str) -> str:
        """Format management alert message"""
        urgency = "CRITICAL" if escalation_level >= 4 else "HIGH PRIORITY"
        
        return f"""
🔴 {urgency} SECURITY INCIDENT - Management Alert

Escalation Level: {escalation_level}/5
Time: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}

Incident Summary: {summary}

Business Impact: {business_impact}

Security team has been notified and response is underway.
Your attention and potential intervention may be required.
        """.strip()
    
    def _select_notification_channels(self, priority: str, 
                                    preferences: List[str]) -> List[NotificationChannel]:
        """Select appropriate notification channels based on priority"""
        
        if priority == "critical":
            # For critical incidents, use all available channels
            return [NotificationChannel(ch) for ch in preferences] + [NotificationChannel.PHONE_CALL]
        elif priority == "high":
            # For high priority, use primary preferences
            return [NotificationChannel(preferences[0])] if preferences else [NotificationChannel.SMS]
        else:
            # For normal priority, use less intrusive methods
            return [NotificationChannel.EMAIL, NotificationChannel.SLACK]


# Mock notification clients for demonstration

class MockSMSClient:
    async def send(self, recipient: str, message: str, priority: str) -> bool:
        await asyncio.sleep(0.1)  # Simulate API call
        return True

class MockEmailClient:
    async def send(self, recipient: str, message: str, priority: str) -> bool:
        await asyncio.sleep(0.2)  # Simulate API call
        return True

class MockSlackClient:
    async def send(self, recipient: str, message: str, priority: str) -> bool:
        await asyncio.sleep(0.1)  # Simulate API call
        return True

class MockPhoneClient:
    async def send(self, recipient: str, message: str, priority: str) -> bool:
        await asyncio.sleep(1.0)  # Simulate phone call
        return priority in ["critical", "high"]  # Phone calls more likely to succeed for urgent matters

class MockWhatsAppClient:
    async def send(self, recipient: str, message: str, priority: str) -> bool:
        await asyncio.sleep(0.3)  # Simulate API call
        return True

class MockPushClient:
    async def send(self, recipient: str, message: str, priority: str) -> bool:
        await asyncio.sleep(0.1)  # Simulate push notification
        return True