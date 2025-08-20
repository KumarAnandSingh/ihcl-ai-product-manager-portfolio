"""
Mock Hotel System Integrations.
Simulates integration with Property Management System (PMS), Point of Sale (POS),
Customer Relationship Management (CRM), Security, and Maintenance systems.
"""

import asyncio
import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union
from uuid import UUID, uuid4

import httpx
from pydantic import BaseModel, Field

from ..core.config import get_settings


class PMSReservation(BaseModel):
    """PMS Reservation data model."""
    
    reservation_id: str
    guest_id: str
    guest_name: str
    room_number: str
    room_type: str
    check_in: datetime
    check_out: datetime
    status: str  # confirmed, checked_in, checked_out, cancelled
    rate: Decimal
    currency: str = "INR"
    special_requests: Optional[str] = None
    loyalty_number: Optional[str] = None


class PMSRoomStatus(BaseModel):
    """PMS Room status data model."""
    
    room_number: str
    room_type: str
    status: str  # occupied, vacant_clean, vacant_dirty, out_of_order
    guest_name: Optional[str] = None
    check_out_time: Optional[datetime] = None
    housekeeping_status: str = "clean"  # clean, dirty, inspected, maintenance


class POSTransaction(BaseModel):
    """POS Transaction data model."""
    
    transaction_id: str
    location: str  # restaurant, bar, spa, gift_shop
    guest_id: Optional[str] = None
    room_number: Optional[str] = None
    amount: Decimal
    currency: str = "INR"
    payment_method: str  # room_charge, cash, card, points
    items: List[Dict[str, Any]]
    timestamp: datetime
    staff_id: str
    status: str = "completed"


class CRMGuestProfile(BaseModel):
    """CRM Guest profile data model."""
    
    guest_id: str
    loyalty_tier: str
    total_stays: int
    total_spend: Decimal
    preferences: Dict[str, Any]
    communication_preferences: Dict[str, bool]
    last_stay_date: Optional[datetime] = None
    average_rating: Optional[float] = None
    complaints_count: int = 0
    compliments_count: int = 0


class SecurityEvent(BaseModel):
    """Security system event data model."""
    
    event_id: str
    event_type: str  # access_denied, alarm, surveillance, incident
    location: str
    timestamp: datetime
    description: str
    severity: str  # low, medium, high, critical
    person_involved: Optional[str] = None
    action_taken: Optional[str] = None
    resolved: bool = False


class MaintenanceWorkOrder(BaseModel):
    """Maintenance work order data model."""
    
    work_order_id: str
    room_number: Optional[str] = None
    location: str
    issue_type: str  # plumbing, electrical, hvac, furniture, cleaning
    priority: str  # low, medium, high, urgent
    description: str
    reported_by: str
    assigned_to: Optional[str] = None
    status: str  # open, assigned, in_progress, completed, cancelled
    created_at: datetime
    scheduled_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_cost: Optional[Decimal] = None


class PMSService:
    """Property Management System service integration."""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = str(self.settings.pms_api_url)
        self.timeout = 30.0
        
        # Mock data for demonstration
        self._mock_reservations = self._generate_mock_reservations()
        self._mock_rooms = self._generate_mock_rooms()
    
    def _generate_mock_reservations(self) -> List[PMSReservation]:
        """Generate mock reservation data."""
        reservations = []
        for i in range(50):
            check_in = datetime.now() + timedelta(days=random.randint(-7, 30))
            check_out = check_in + timedelta(days=random.randint(1, 14))
            
            reservations.append(PMSReservation(
                reservation_id=f"RES{1000+i:04d}",
                guest_id=f"GUEST{100+i:03d}",
                guest_name=f"Guest {i+1}",
                room_number=f"{random.randint(1,4)}{random.randint(1,9):02d}",
                room_type=random.choice(["Deluxe", "Executive", "Suite", "Presidential"]),
                check_in=check_in,
                check_out=check_out,
                status=random.choice(["confirmed", "checked_in", "checked_out"]),
                rate=Decimal(random.randint(5000, 50000)),
                special_requests=random.choice([None, "High floor", "Ocean view", "Late checkout"])
            ))
        return reservations
    
    def _generate_mock_rooms(self) -> List[PMSRoomStatus]:
        """Generate mock room status data."""
        rooms = []
        for floor in range(1, 5):
            for room in range(1, 51):
                room_number = f"{floor}{room:02d}"
                rooms.append(PMSRoomStatus(
                    room_number=room_number,
                    room_type=random.choice(["Deluxe", "Executive", "Suite", "Presidential"]),
                    status=random.choice(["occupied", "vacant_clean", "vacant_dirty", "out_of_order"]),
                    guest_name=f"Guest {random.randint(1, 100)}" if random.random() > 0.5 else None,
                    check_out_time=datetime.now() + timedelta(hours=random.randint(-12, 12)) if random.random() > 0.7 else None,
                    housekeeping_status=random.choice(["clean", "dirty", "inspected"])
                ))
        return rooms
    
    async def get_guest_reservation(self, guest_id: str) -> Optional[PMSReservation]:
        """Get current reservation for a guest."""
        # Simulate API call delay
        await asyncio.sleep(0.1)
        
        for reservation in self._mock_reservations:
            if reservation.guest_id == guest_id and reservation.status in ["confirmed", "checked_in"]:
                return reservation
        return None
    
    async def get_room_status(self, room_number: str) -> Optional[PMSRoomStatus]:
        """Get current status of a room."""
        await asyncio.sleep(0.1)
        
        for room in self._mock_rooms:
            if room.room_number == room_number:
                return room
        return None
    
    async def update_room_status(self, room_number: str, status: str, notes: Optional[str] = None) -> bool:
        """Update room status in PMS."""
        await asyncio.sleep(0.2)
        
        for room in self._mock_rooms:
            if room.room_number == room_number:
                room.status = status
                return True
        return False
    
    async def create_service_request(self, request_data: Dict[str, Any]) -> str:
        """Create a service request in PMS."""
        await asyncio.sleep(0.3)
        
        # Simulate creating service request
        request_id = f"SR{random.randint(10000, 99999)}"
        return request_id
    
    async def get_guest_folio(self, guest_id: str) -> Dict[str, Any]:
        """Get guest folio/billing information."""
        await asyncio.sleep(0.2)
        
        # Mock folio data
        return {
            "guest_id": guest_id,
            "total_charges": Decimal(random.randint(10000, 100000)),
            "room_charges": Decimal(random.randint(5000, 50000)),
            "incidental_charges": Decimal(random.randint(1000, 10000)),
            "payments": Decimal(random.randint(0, 50000)),
            "balance": Decimal(random.randint(-5000, 50000)),
            "currency": "INR"
        }


class POSService:
    """Point of Sale system service integration."""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = str(self.settings.pos_api_url)
        self.timeout = 30.0
        
        self._mock_transactions = self._generate_mock_transactions()
    
    def _generate_mock_transactions(self) -> List[POSTransaction]:
        """Generate mock POS transaction data."""
        transactions = []
        locations = ["Restaurant", "Bar", "Spa", "Gift Shop", "Room Service"]
        
        for i in range(100):
            transactions.append(POSTransaction(
                transaction_id=f"TXN{10000+i:05d}",
                location=random.choice(locations),
                guest_id=f"GUEST{random.randint(100, 199):03d}" if random.random() > 0.3 else None,
                room_number=f"{random.randint(1,4)}{random.randint(1,50):02d}" if random.random() > 0.3 else None,
                amount=Decimal(random.randint(500, 15000)),
                payment_method=random.choice(["room_charge", "cash", "card", "points"]),
                items=[{
                    "name": f"Item {j+1}",
                    "quantity": random.randint(1, 3),
                    "price": Decimal(random.randint(200, 5000))
                } for j in range(random.randint(1, 5))],
                timestamp=datetime.now() - timedelta(days=random.randint(0, 30)),
                staff_id=f"STAFF{random.randint(1, 20):03d}"
            ))
        return transactions
    
    async def get_guest_transactions(self, guest_id: str, days: int = 30) -> List[POSTransaction]:
        """Get recent transactions for a guest."""
        await asyncio.sleep(0.1)
        
        cutoff_date = datetime.now() - timedelta(days=days)
        return [
            txn for txn in self._mock_transactions
            if txn.guest_id == guest_id and txn.timestamp >= cutoff_date
        ]
    
    async def process_refund(self, transaction_id: str, amount: Decimal, reason: str) -> Dict[str, Any]:
        """Process a refund for a transaction."""
        await asyncio.sleep(0.3)
        
        refund_id = f"REF{random.randint(10000, 99999)}"
        return {
            "refund_id": refund_id,
            "original_transaction_id": transaction_id,
            "refund_amount": amount,
            "reason": reason,
            "status": "completed",
            "processed_at": datetime.now()
        }
    
    async def get_location_sales(self, location: str, date: datetime) -> Dict[str, Any]:
        """Get sales data for a specific location and date."""
        await asyncio.sleep(0.2)
        
        # Mock sales data
        return {
            "location": location,
            "date": date.date(),
            "total_sales": Decimal(random.randint(50000, 500000)),
            "transaction_count": random.randint(50, 300),
            "average_ticket": Decimal(random.randint(1000, 3000)),
            "payment_methods": {
                "cash": Decimal(random.randint(10000, 50000)),
                "card": Decimal(random.randint(30000, 200000)),
                "room_charge": Decimal(random.randint(20000, 150000))
            }
        }


class CRMService:
    """Customer Relationship Management service integration."""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = str(self.settings.crm_api_url)
        self.timeout = 30.0
        
        self._mock_profiles = self._generate_mock_profiles()
    
    def _generate_mock_profiles(self) -> List[CRMGuestProfile]:
        """Generate mock CRM guest profiles."""
        profiles = []
        tiers = ["Silver", "Gold", "Platinum", "Diamond"]
        
        for i in range(100):
            profiles.append(CRMGuestProfile(
                guest_id=f"GUEST{100+i:03d}",
                loyalty_tier=random.choice(tiers),
                total_stays=random.randint(1, 50),
                total_spend=Decimal(random.randint(50000, 2000000)),
                preferences={
                    "room_floor": random.choice(["high", "low", "middle"]),
                    "pillow_type": random.choice(["soft", "firm", "hypoallergenic"]),
                    "temperature": random.randint(18, 25),
                    "housekeeping_time": random.choice(["morning", "afternoon", "evening"])
                },
                communication_preferences={
                    "email": random.choice([True, False]),
                    "sms": random.choice([True, False]),
                    "phone": random.choice([True, False]),
                    "marketing": random.choice([True, False])
                },
                last_stay_date=datetime.now() - timedelta(days=random.randint(1, 365)),
                average_rating=round(random.uniform(3.0, 5.0), 1),
                complaints_count=random.randint(0, 5),
                compliments_count=random.randint(0, 10)
            ))
        return profiles
    
    async def get_guest_profile(self, guest_id: str) -> Optional[CRMGuestProfile]:
        """Get CRM profile for a guest."""
        await asyncio.sleep(0.1)
        
        for profile in self._mock_profiles:
            if profile.guest_id == guest_id:
                return profile
        return None
    
    async def update_guest_preferences(self, guest_id: str, preferences: Dict[str, Any]) -> bool:
        """Update guest preferences in CRM."""
        await asyncio.sleep(0.2)
        
        for profile in self._mock_profiles:
            if profile.guest_id == guest_id:
                profile.preferences.update(preferences)
                return True
        return False
    
    async def record_guest_feedback(self, guest_id: str, feedback_type: str, rating: int, comments: str) -> str:
        """Record guest feedback in CRM."""
        await asyncio.sleep(0.2)
        
        feedback_id = f"FB{random.randint(10000, 99999)}"
        
        # Update profile stats
        for profile in self._mock_profiles:
            if profile.guest_id == guest_id:
                if feedback_type == "complaint":
                    profile.complaints_count += 1
                elif feedback_type == "compliment":
                    profile.compliments_count += 1
                break
        
        return feedback_id
    
    async def get_guest_history(self, guest_id: str) -> Dict[str, Any]:
        """Get comprehensive guest history from CRM."""
        await asyncio.sleep(0.3)
        
        # Mock history data
        return {
            "guest_id": guest_id,
            "stay_history": [
                {
                    "date": datetime.now() - timedelta(days=random.randint(1, 365)),
                    "hotel": f"Hotel {random.randint(1, 5)}",
                    "room_type": random.choice(["Deluxe", "Executive", "Suite"]),
                    "duration": random.randint(1, 7),
                    "total_spend": Decimal(random.randint(10000, 100000))
                } for _ in range(random.randint(1, 10))
            ],
            "preference_evolution": {
                "room_type_preferences": ["Deluxe", "Executive"],
                "service_preferences": ["Late checkout", "High floor"],
                "dining_preferences": ["Vegetarian", "Local cuisine"]
            },
            "interaction_summary": {
                "total_interactions": random.randint(10, 100),
                "satisfaction_trend": "improving",
                "last_complaint": datetime.now() - timedelta(days=random.randint(30, 365)) if random.random() > 0.5 else None
            }
        }


class SecurityService:
    """Security system service integration."""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = str(self.settings.security_api_url)
        self.timeout = 30.0
        
        self._mock_events = self._generate_mock_events()
    
    def _generate_mock_events(self) -> List[SecurityEvent]:
        """Generate mock security events."""
        events = []
        event_types = ["access_denied", "alarm", "surveillance", "incident"]
        locations = ["Lobby", "Elevator", "Parking", "Pool", "Gym", "Restaurant"]
        
        for i in range(50):
            events.append(SecurityEvent(
                event_id=f"SEC{10000+i:05d}",
                event_type=random.choice(event_types),
                location=random.choice(locations),
                timestamp=datetime.now() - timedelta(hours=random.randint(0, 72)),
                description=f"Security event {i+1} description",
                severity=random.choice(["low", "medium", "high", "critical"]),
                person_involved=f"Person {random.randint(1, 100)}" if random.random() > 0.5 else None,
                action_taken="Security team notified" if random.random() > 0.3 else None,
                resolved=random.choice([True, False])
            ))
        return events
    
    async def get_recent_events(self, hours: int = 24) -> List[SecurityEvent]:
        """Get recent security events."""
        await asyncio.sleep(0.1)
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            event for event in self._mock_events
            if event.timestamp >= cutoff_time
        ]
    
    async def check_access_permissions(self, guest_id: str, location: str) -> Dict[str, Any]:
        """Check if guest has access to a location."""
        await asyncio.sleep(0.1)
        
        # Mock access check
        has_access = random.choice([True, False])
        return {
            "guest_id": guest_id,
            "location": location,
            "access_granted": has_access,
            "reason": "Valid guest access" if has_access else "Access restricted",
            "timestamp": datetime.now()
        }
    
    async def report_security_incident(self, incident_data: Dict[str, Any]) -> str:
        """Report a security incident."""
        await asyncio.sleep(0.2)
        
        incident_id = f"SEC{random.randint(10000, 99999)}"
        
        # Add to mock events
        event = SecurityEvent(
            event_id=incident_id,
            event_type="incident",
            location=incident_data.get("location", "Unknown"),
            timestamp=datetime.now(),
            description=incident_data.get("description", "Security incident"),
            severity=incident_data.get("severity", "medium"),
            person_involved=incident_data.get("person_involved"),
            resolved=False
        )
        self._mock_events.append(event)
        
        return incident_id
    
    async def get_access_logs(self, room_number: str, days: int = 7) -> List[Dict[str, Any]]:
        """Get access logs for a room."""
        await asyncio.sleep(0.2)
        
        # Mock access logs
        logs = []
        for _ in range(random.randint(5, 20)):
            logs.append({
                "timestamp": datetime.now() - timedelta(days=random.randint(0, days)),
                "room_number": room_number,
                "access_type": random.choice(["key_card", "master_key", "mobile_key"]),
                "person": f"Guest/Staff {random.randint(1, 100)}",
                "successful": random.choice([True, False]),
                "method": random.choice(["card_swipe", "mobile_app", "physical_key"])
            })
        return sorted(logs, key=lambda x: x["timestamp"], reverse=True)


class MaintenanceService:
    """Maintenance system service integration."""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = str(self.settings.maintenance_api_url)
        self.timeout = 30.0
        
        self._mock_work_orders = self._generate_mock_work_orders()
    
    def _generate_mock_work_orders(self) -> List[MaintenanceWorkOrder]:
        """Generate mock maintenance work orders."""
        work_orders = []
        issue_types = ["plumbing", "electrical", "hvac", "furniture", "cleaning"]
        priorities = ["low", "medium", "high", "urgent"]
        statuses = ["open", "assigned", "in_progress", "completed", "cancelled"]
        
        for i in range(100):
            created_at = datetime.now() - timedelta(days=random.randint(0, 90))
            work_orders.append(MaintenanceWorkOrder(
                work_order_id=f"WO{10000+i:05d}",
                room_number=f"{random.randint(1,4)}{random.randint(1,50):02d}" if random.random() > 0.3 else None,
                location=f"Floor {random.randint(1, 4)}" if not work_orders else "Public Area",
                issue_type=random.choice(issue_types),
                priority=random.choice(priorities),
                description=f"Maintenance issue {i+1} requiring attention",
                reported_by=f"Staff{random.randint(1, 50):03d}",
                assigned_to=f"Tech{random.randint(1, 10):03d}" if random.random() > 0.3 else None,
                status=random.choice(statuses),
                created_at=created_at,
                scheduled_at=created_at + timedelta(hours=random.randint(1, 48)) if random.random() > 0.5 else None,
                completed_at=created_at + timedelta(hours=random.randint(2, 72)) if random.random() > 0.6 else None,
                estimated_cost=Decimal(random.randint(500, 10000)) if random.random() > 0.4 else None
            ))
        return work_orders
    
    async def create_work_order(self, work_order_data: Dict[str, Any]) -> str:
        """Create a new maintenance work order."""
        await asyncio.sleep(0.2)
        
        work_order_id = f"WO{random.randint(10000, 99999)}"
        
        # Add to mock work orders
        work_order = MaintenanceWorkOrder(
            work_order_id=work_order_id,
            room_number=work_order_data.get("room_number"),
            location=work_order_data.get("location", "Unknown"),
            issue_type=work_order_data.get("issue_type", "general"),
            priority=work_order_data.get("priority", "medium"),
            description=work_order_data.get("description", "Maintenance required"),
            reported_by=work_order_data.get("reported_by", "System"),
            status="open",
            created_at=datetime.now()
        )
        self._mock_work_orders.append(work_order)
        
        return work_order_id
    
    async def get_work_orders_by_room(self, room_number: str, status: Optional[str] = None) -> List[MaintenanceWorkOrder]:
        """Get work orders for a specific room."""
        await asyncio.sleep(0.1)
        
        orders = [wo for wo in self._mock_work_orders if wo.room_number == room_number]
        if status:
            orders = [wo for wo in orders if wo.status == status]
        
        return sorted(orders, key=lambda x: x.created_at, reverse=True)
    
    async def update_work_order_status(self, work_order_id: str, status: str, notes: Optional[str] = None) -> bool:
        """Update work order status."""
        await asyncio.sleep(0.2)
        
        for wo in self._mock_work_orders:
            if wo.work_order_id == work_order_id:
                wo.status = status
                if status == "completed":
                    wo.completed_at = datetime.now()
                return True
        return False
    
    async def get_maintenance_schedule(self, date: datetime) -> List[MaintenanceWorkOrder]:
        """Get scheduled maintenance for a specific date."""
        await asyncio.sleep(0.1)
        
        target_date = date.date()
        return [
            wo for wo in self._mock_work_orders
            if wo.scheduled_at and wo.scheduled_at.date() == target_date
        ]
    
    async def get_maintenance_stats(self, days: int = 30) -> Dict[str, Any]:
        """Get maintenance statistics."""
        await asyncio.sleep(0.2)
        
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_orders = [wo for wo in self._mock_work_orders if wo.created_at >= cutoff_date]
        
        # Calculate stats
        total_orders = len(recent_orders)
        completed_orders = len([wo for wo in recent_orders if wo.status == "completed"])
        
        return {
            "total_work_orders": total_orders,
            "completed_work_orders": completed_orders,
            "completion_rate": (completed_orders / total_orders * 100) if total_orders > 0 else 0,
            "average_completion_time_hours": random.randint(4, 48),
            "orders_by_priority": {
                "low": len([wo for wo in recent_orders if wo.priority == "low"]),
                "medium": len([wo for wo in recent_orders if wo.priority == "medium"]),
                "high": len([wo for wo in recent_orders if wo.priority == "high"]),
                "urgent": len([wo for wo in recent_orders if wo.priority == "urgent"])
            },
            "orders_by_type": {
                issue_type: len([wo for wo in recent_orders if wo.issue_type == issue_type])
                for issue_type in ["plumbing", "electrical", "hvac", "furniture", "cleaning"]
            }
        }