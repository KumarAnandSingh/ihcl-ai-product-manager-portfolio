"""
Session Management for Security Incident Triage Agent.

Manages session state, context, and temporary data for active incident processing
with Redis-based storage and automatic cleanup.
"""

import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
import redis.asyncio as redis
from ..core.state import IncidentState


class SessionContext(BaseModel):
    """Session context information."""
    session_id: str
    incident_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    user_context: Dict[str, Any] = Field(default_factory=dict)
    processing_context: Dict[str, Any] = Field(default_factory=dict)
    temporary_data: Dict[str, Any] = Field(default_factory=dict)
    related_incidents: List[str] = Field(default_factory=list)
    workflow_state: Dict[str, Any] = Field(default_factory=dict)


class SessionManager:
    """
    Manages session state and context for incident processing.
    
    Provides Redis-based session storage with automatic expiration,
    context management, and state synchronization.
    """
    
    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        session_ttl_hours: int = 24,
        max_sessions: int = 10000
    ):
        self.redis_url = redis_url
        self.session_ttl_hours = session_ttl_hours
        self.max_sessions = max_sessions
        self.redis_client = None
        
        # Session key prefixes
        self.session_prefix = "security_triage:session:"
        self.incident_prefix = "security_triage:incident:"
        self.context_prefix = "security_triage:context:"
        self.workflow_prefix = "security_triage:workflow:"
    
    async def initialize(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
        except Exception as e:
            # Fallback to in-memory storage if Redis is not available
            print(f"Redis not available, using in-memory storage: {e}")
            self.redis_client = None
            self._memory_storage = {}
    
    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
    
    async def create_session(
        self,
        incident_id: str,
        user_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Create a new session for incident processing.
        
        Args:
            incident_id: Unique incident identifier
            user_context: Initial user context data
            
        Returns:
            Session ID
        """
        session_id = f"session_{incident_id}_{int(datetime.utcnow().timestamp())}"
        
        session_context = SessionContext(
            session_id=session_id,
            incident_id=incident_id,
            user_context=user_context or {}
        )
        
        await self._store_session_context(session_context)
        return session_id
    
    async def get_session_context(self, incident_id: str) -> Dict[str, Any]:
        """
        Get session context for an incident.
        
        Args:
            incident_id: Incident identifier
            
        Returns:
            Session context dictionary
        """
        # Find session by incident ID
        session_key = await self._find_session_by_incident(incident_id)
        if not session_key:
            return {}
        
        session_context = await self._load_session_context(session_key)
        if session_context:
            # Update last accessed time
            session_context.last_accessed = datetime.utcnow()
            await self._store_session_context(session_context)
            
            return {
                "session_id": session_context.session_id,
                "user_context": session_context.user_context,
                "processing_context": session_context.processing_context,
                "related_incidents": session_context.related_incidents,
                "workflow_state": session_context.workflow_state
            }
        
        return {}
    
    async def update_session_context(
        self,
        incident_id: str,
        context_update: Dict[str, Any]
    ) -> bool:
        """
        Update session context for an incident.
        
        Args:
            incident_id: Incident identifier
            context_update: Context updates to apply
            
        Returns:
            Success status
        """
        session_key = await self._find_session_by_incident(incident_id)
        if not session_key:
            return False
        
        session_context = await self._load_session_context(session_key)
        if not session_context:
            return False
        
        # Apply updates
        for key, value in context_update.items():
            if key == "user_context":
                session_context.user_context.update(value)
            elif key == "processing_context":
                session_context.processing_context.update(value)
            elif key == "temporary_data":
                session_context.temporary_data.update(value)
            elif key == "workflow_state":
                session_context.workflow_state.update(value)
            elif key == "related_incidents" and isinstance(value, list):
                session_context.related_incidents.extend(value)
                # Remove duplicates
                session_context.related_incidents = list(set(session_context.related_incidents))
        
        session_context.last_accessed = datetime.utcnow()
        await self._store_session_context(session_context)
        return True
    
    async def store_incident_state(
        self,
        incident_state: IncidentState
    ) -> bool:
        """
        Store incident state in session.
        
        Args:
            incident_state: Current incident state
            
        Returns:
            Success status
        """
        incident_key = f"{self.incident_prefix}{incident_state.incident_id}"
        
        # Serialize incident state
        state_data = {
            "incident_id": incident_state.incident_id,
            "title": incident_state.title,
            "description": incident_state.description,
            "severity": incident_state.severity.value if incident_state.severity else None,
            "category": incident_state.category.value if incident_state.category else None,
            "current_step": incident_state.current_step,
            "completed_steps": incident_state.completed_steps,
            "failed_steps": incident_state.failed_steps,
            "created_at": incident_state.created_at.isoformat(),
            "updated_at": incident_state.updated_at.isoformat(),
            "tool_results": incident_state.tool_results,
            "processing_metrics": incident_state.processing_metrics,
            "requires_human_intervention": incident_state.requires_human_intervention,
            "workflow_paused": incident_state.workflow_paused
        }
        
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    incident_key,
                    timedelta(hours=self.session_ttl_hours),
                    json.dumps(state_data, default=str)
                )
                return True
            except Exception as e:
                print(f"Error storing incident state in Redis: {e}")
                return False
        else:
            # In-memory fallback
            self._memory_storage[incident_key] = state_data
            return True
    
    async def load_incident_state(
        self,
        incident_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Load incident state from session.
        
        Args:
            incident_id: Incident identifier
            
        Returns:
            Incident state data or None
        """
        incident_key = f"{self.incident_prefix}{incident_id}"
        
        if self.redis_client:
            try:
                state_json = await self.redis_client.get(incident_key)
                if state_json:
                    return json.loads(state_json)
            except Exception as e:
                print(f"Error loading incident state from Redis: {e}")
        else:
            # In-memory fallback
            return self._memory_storage.get(incident_key)
        
        return None
    
    async def store_workflow_checkpoint(
        self,
        incident_id: str,
        step_name: str,
        checkpoint_data: Dict[str, Any]
    ) -> bool:
        """
        Store workflow checkpoint for recovery.
        
        Args:
            incident_id: Incident identifier
            step_name: Current workflow step
            checkpoint_data: Checkpoint data
            
        Returns:
            Success status
        """
        checkpoint_key = f"{self.workflow_prefix}{incident_id}:{step_name}"
        
        checkpoint_record = {
            "incident_id": incident_id,
            "step_name": step_name,
            "timestamp": datetime.utcnow().isoformat(),
            "data": checkpoint_data
        }
        
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    checkpoint_key,
                    timedelta(hours=self.session_ttl_hours),
                    json.dumps(checkpoint_record, default=str)
                )
                return True
            except Exception as e:
                print(f"Error storing workflow checkpoint: {e}")
                return False
        else:
            # In-memory fallback
            self._memory_storage[checkpoint_key] = checkpoint_record
            return True
    
    async def load_workflow_checkpoint(
        self,
        incident_id: str,
        step_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Load workflow checkpoint for recovery.
        
        Args:
            incident_id: Incident identifier
            step_name: Workflow step name
            
        Returns:
            Checkpoint data or None
        """
        checkpoint_key = f"{self.workflow_prefix}{incident_id}:{step_name}"
        
        if self.redis_client:
            try:
                checkpoint_json = await self.redis_client.get(checkpoint_key)
                if checkpoint_json:
                    return json.loads(checkpoint_json)
            except Exception as e:
                print(f"Error loading workflow checkpoint: {e}")
        else:
            # In-memory fallback
            return self._memory_storage.get(checkpoint_key)
        
        return None
    
    async def list_active_sessions(self) -> List[Dict[str, Any]]:
        """
        List all active sessions.
        
        Returns:
            List of active session summaries
        """
        sessions = []
        
        if self.redis_client:
            try:
                # Get all session keys
                session_keys = await self.redis_client.keys(f"{self.session_prefix}*")
                
                for key in session_keys:
                    session_data = await self.redis_client.get(key)
                    if session_data:
                        session_context = SessionContext.parse_raw(session_data)
                        sessions.append({
                            "session_id": session_context.session_id,
                            "incident_id": session_context.incident_id,
                            "created_at": session_context.created_at.isoformat(),
                            "last_accessed": session_context.last_accessed.isoformat()
                        })
            except Exception as e:
                print(f"Error listing sessions: {e}")
        else:
            # In-memory fallback
            for key, data in self._memory_storage.items():
                if key.startswith(self.session_prefix):
                    sessions.append({
                        "session_id": data.get("session_id"),
                        "incident_id": data.get("incident_id"),
                        "created_at": data.get("created_at"),
                        "last_accessed": data.get("last_accessed")
                    })
        
        return sessions
    
    async def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        if not self.redis_client:
            # For in-memory storage, implement basic cleanup
            cutoff_time = datetime.utcnow() - timedelta(hours=self.session_ttl_hours)
            expired_keys = []
            
            for key, data in self._memory_storage.items():
                if key.startswith(self.session_prefix):
                    last_accessed = datetime.fromisoformat(data.get("last_accessed", ""))
                    if last_accessed < cutoff_time:
                        expired_keys.append(key)
            
            for key in expired_keys:
                del self._memory_storage[key]
            
            return len(expired_keys)
        
        # Redis automatically handles expiration
        return 0
    
    async def _store_session_context(self, session_context: SessionContext):
        """Store session context."""
        session_key = f"{self.session_prefix}{session_context.session_id}"
        
        if self.redis_client:
            try:
                await self.redis_client.setex(
                    session_key,
                    timedelta(hours=self.session_ttl_hours),
                    session_context.json()
                )
            except Exception as e:
                print(f"Error storing session context: {e}")
        else:
            # In-memory fallback
            self._memory_storage[session_key] = session_context.dict()
    
    async def _load_session_context(self, session_key: str) -> Optional[SessionContext]:
        """Load session context."""
        if self.redis_client:
            try:
                session_json = await self.redis_client.get(session_key)
                if session_json:
                    return SessionContext.parse_raw(session_json)
            except Exception as e:
                print(f"Error loading session context: {e}")
        else:
            # In-memory fallback
            session_data = self._memory_storage.get(session_key)
            if session_data:
                return SessionContext.parse_obj(session_data)
        
        return None
    
    async def _find_session_by_incident(self, incident_id: str) -> Optional[str]:
        """Find session key by incident ID."""
        if self.redis_client:
            try:
                # Search through all session keys
                session_keys = await self.redis_client.keys(f"{self.session_prefix}*")
                
                for key in session_keys:
                    session_data = await self.redis_client.get(key)
                    if session_data:
                        session_context = SessionContext.parse_raw(session_data)
                        if session_context.incident_id == incident_id:
                            return key
            except Exception as e:
                print(f"Error finding session by incident: {e}")
        else:
            # In-memory fallback
            for key, data in self._memory_storage.items():
                if key.startswith(self.session_prefix):
                    if data.get("incident_id") == incident_id:
                        return key
        
        return None
    
    async def store_incident(self, incident_state: IncidentState) -> bool:
        """
        Store complete incident for historical reference.
        
        Args:
            incident_state: Complete incident state
            
        Returns:
            Success status
        """
        # This is a wrapper method that delegates to store_incident_state
        # for compatibility with the workflow
        return await self.store_incident_state(incident_state)