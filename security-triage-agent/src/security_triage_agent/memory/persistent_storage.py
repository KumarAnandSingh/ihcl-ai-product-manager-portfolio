"""
Persistent Storage for Security Incident Triage Agent.

Provides SQLite-based persistent storage for incident records, analytics,
and long-term data retention with proper indexing and querying capabilities.
"""

import sqlite3
import json
import asyncio
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from pathlib import Path
from pydantic import BaseModel, Field
import aiosqlite

from ..core.state import IncidentState, IncidentCategory, IncidentPriority


class IncidentRecord(BaseModel):
    """Persistent incident record structure."""
    incident_id: str
    title: str
    description: str
    category: Optional[str] = None
    priority: Optional[str] = None
    status: str = "active"  # active, resolved, closed
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime] = None
    
    # Analysis results
    risk_score: Optional[float] = None
    classification_confidence: Optional[float] = None
    
    # Processing metadata
    processing_time_seconds: Optional[float] = None
    human_interventions: int = 0
    workflow_steps_completed: int = 0
    workflow_steps_failed: int = 0
    
    # Structured data (JSON serialized)
    metadata_json: str = "{}"
    tool_results_json: str = "{}"
    response_plan_json: str = "{}"
    quality_scores_json: str = "{}"
    
    # Compliance and safety
    compliance_frameworks: str = ""  # Comma-separated list
    safety_violations: int = 0
    requires_followup: bool = False


class PersistentStorage:
    """
    SQLite-based persistent storage for incident records and analytics.
    
    Provides comprehensive data persistence with indexing for efficient
    querying, analytics, and reporting capabilities.
    """
    
    def __init__(self, db_path: str = "security_incidents.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
    
    async def initialize(self):
        """Initialize database schema and indexes."""
        async with aiosqlite.connect(self.db_path) as db:
            await self._create_tables(db)
            await self._create_indexes(db)
            await db.commit()
    
    async def _create_tables(self, db: aiosqlite.Connection):
        """Create database tables."""
        
        # Main incidents table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                incident_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT,
                priority TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP NOT NULL,
                updated_at TIMESTAMP NOT NULL,
                resolved_at TIMESTAMP,
                
                -- Analysis results
                risk_score REAL,
                classification_confidence REAL,
                
                -- Processing metadata
                processing_time_seconds REAL,
                human_interventions INTEGER DEFAULT 0,
                workflow_steps_completed INTEGER DEFAULT 0,
                workflow_steps_failed INTEGER DEFAULT 0,
                
                -- Structured data (JSON)
                metadata_json TEXT DEFAULT '{}',
                tool_results_json TEXT DEFAULT '{}',
                response_plan_json TEXT DEFAULT '{}',
                quality_scores_json TEXT DEFAULT '{}',
                
                -- Compliance and safety
                compliance_frameworks TEXT DEFAULT '',
                safety_violations INTEGER DEFAULT 0,
                requires_followup BOOLEAN DEFAULT FALSE
            )
        """)
        
        # Incident history table for tracking changes
        await db.execute("""
            CREATE TABLE IF NOT EXISTS incident_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT NOT NULL,
                timestamp TIMESTAMP NOT NULL,
                change_type TEXT NOT NULL,  -- created, updated, status_changed, etc.
                change_data TEXT,  -- JSON data of changes
                user_context TEXT DEFAULT '{}',
                FOREIGN KEY (incident_id) REFERENCES incidents (incident_id)
            )
        """)
        
        # Analytics aggregation table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS incident_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_bucket TEXT NOT NULL,  -- YYYY-MM-DD for daily, YYYY-MM for monthly
                bucket_type TEXT NOT NULL,  -- 'daily', 'weekly', 'monthly'
                category TEXT,
                priority TEXT,
                
                -- Counts
                total_incidents INTEGER DEFAULT 0,
                resolved_incidents INTEGER DEFAULT 0,
                escalated_incidents INTEGER DEFAULT 0,
                
                -- Performance metrics
                avg_processing_time REAL,
                avg_risk_score REAL,
                avg_quality_score REAL,
                
                -- Updated timestamp
                updated_at TIMESTAMP NOT NULL,
                
                UNIQUE(date_bucket, bucket_type, category, priority)
            )
        """)
        
        # Compliance tracking table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS compliance_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT NOT NULL,
                framework TEXT NOT NULL,  -- DPDP, PCI_DSS, etc.
                event_type TEXT NOT NULL,  -- notification_sent, violation_detected, etc.
                event_timestamp TIMESTAMP NOT NULL,
                event_data TEXT DEFAULT '{}',
                compliance_status TEXT,  -- compliant, non_compliant, pending
                FOREIGN KEY (incident_id) REFERENCES incidents (incident_id)
            )
        """)
        
        # Performance metrics table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS performance_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id TEXT NOT NULL,
                metric_name TEXT NOT NULL,
                metric_value REAL NOT NULL,
                metric_timestamp TIMESTAMP NOT NULL,
                metric_context TEXT DEFAULT '{}',
                FOREIGN KEY (incident_id) REFERENCES incidents (incident_id)
            )
        """)
    
    async def _create_indexes(self, db: aiosqlite.Connection):
        """Create database indexes for performance."""
        
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_incidents_category ON incidents (category)",
            "CREATE INDEX IF NOT EXISTS idx_incidents_priority ON incidents (priority)",
            "CREATE INDEX IF NOT EXISTS idx_incidents_status ON incidents (status)",
            "CREATE INDEX IF NOT EXISTS idx_incidents_created_at ON incidents (created_at)",
            "CREATE INDEX IF NOT EXISTS idx_incidents_updated_at ON incidents (updated_at)",
            "CREATE INDEX IF NOT EXISTS idx_incidents_risk_score ON incidents (risk_score)",
            
            "CREATE INDEX IF NOT EXISTS idx_history_incident_id ON incident_history (incident_id)",
            "CREATE INDEX IF NOT EXISTS idx_history_timestamp ON incident_history (timestamp)",
            "CREATE INDEX IF NOT EXISTS idx_history_change_type ON incident_history (change_type)",
            
            "CREATE INDEX IF NOT EXISTS idx_analytics_date_bucket ON incident_analytics (date_bucket)",
            "CREATE INDEX IF NOT EXISTS idx_analytics_category ON incident_analytics (category)",
            
            "CREATE INDEX IF NOT EXISTS idx_compliance_incident ON compliance_events (incident_id)",
            "CREATE INDEX IF NOT EXISTS idx_compliance_framework ON compliance_events (framework)",
            "CREATE INDEX IF NOT EXISTS idx_compliance_timestamp ON compliance_events (event_timestamp)",
            
            "CREATE INDEX IF NOT EXISTS idx_metrics_incident ON performance_metrics (incident_id)",
            "CREATE INDEX IF NOT EXISTS idx_metrics_name ON performance_metrics (metric_name)",
            "CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON performance_metrics (metric_timestamp)"
        ]
        
        for index_sql in indexes:
            await db.execute(index_sql)
    
    async def store_incident(self, incident_state: IncidentState) -> bool:
        """
        Store or update an incident record.
        
        Args:
            incident_state: Complete incident state
            
        Returns:
            Success status
        """
        try:
            # Convert to incident record
            record = self._state_to_record(incident_state)
            
            async with aiosqlite.connect(self.db_path) as db:
                # Check if incident exists
                cursor = await db.execute(
                    "SELECT incident_id FROM incidents WHERE incident_id = ?",
                    (record.incident_id,)
                )
                exists = await cursor.fetchone()
                
                if exists:
                    # Update existing record
                    await self._update_incident_record(db, record)
                    change_type = "updated"
                else:
                    # Insert new record
                    await self._insert_incident_record(db, record)
                    change_type = "created"
                
                # Record change in history
                await self._record_incident_history(
                    db, record.incident_id, change_type, incident_state.dict()
                )
                
                await db.commit()
                return True
                
        except Exception as e:
            print(f"Error storing incident: {e}")
            return False
    
    async def get_incident(self, incident_id: str) -> Optional[IncidentRecord]:
        """
        Retrieve an incident record.
        
        Args:
            incident_id: Incident identifier
            
        Returns:
            Incident record or None
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(
                    "SELECT * FROM incidents WHERE incident_id = ?",
                    (incident_id,)
                )
                row = await cursor.fetchone()
                
                if row:
                    return IncidentRecord(**dict(row))
                
        except Exception as e:
            print(f"Error retrieving incident: {e}")
        
        return None
    
    async def search_incidents(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: str = "created_at",
        order_direction: str = "DESC"
    ) -> List[IncidentRecord]:
        """
        Search incidents with filters.
        
        Args:
            filters: Search filters (category, priority, status, etc.)
            limit: Maximum number of results
            offset: Result offset for pagination
            order_by: Column to order by
            order_direction: ASC or DESC
            
        Returns:
            List of matching incident records
        """
        try:
            where_clauses = []
            params = []
            
            if filters:
                for key, value in filters.items():
                    if key in ["category", "priority", "status"]:
                        where_clauses.append(f"{key} = ?")
                        params.append(value)
                    elif key == "created_after":
                        where_clauses.append("created_at >= ?")
                        params.append(value)
                    elif key == "created_before":
                        where_clauses.append("created_at <= ?")
                        params.append(value)
                    elif key == "risk_score_min":
                        where_clauses.append("risk_score >= ?")
                        params.append(value)
                    elif key == "risk_score_max":
                        where_clauses.append("risk_score <= ?")
                        params.append(value)
            
            where_clause = ""
            if where_clauses:
                where_clause = "WHERE " + " AND ".join(where_clauses)
            
            query = f"""
                SELECT * FROM incidents 
                {where_clause}
                ORDER BY {order_by} {order_direction}
                LIMIT ? OFFSET ?
            """
            params.extend([limit, offset])
            
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query, params)
                rows = await cursor.fetchall()
                
                return [IncidentRecord(**dict(row)) for row in rows]
                
        except Exception as e:
            print(f"Error searching incidents: {e}")
            return []
    
    async def get_incident_analytics(
        self,
        start_date: datetime,
        end_date: datetime,
        bucket_type: str = "daily"
    ) -> List[Dict[str, Any]]:
        """
        Get incident analytics for a date range.
        
        Args:
            start_date: Start date for analytics
            end_date: End date for analytics
            bucket_type: Aggregation bucket type (daily, weekly, monthly)
            
        Returns:
            List of analytics records
        """
        try:
            # Generate analytics if not exists
            await self._generate_analytics(start_date, end_date, bucket_type)
            
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute("""
                    SELECT * FROM incident_analytics 
                    WHERE bucket_type = ? 
                    AND date_bucket BETWEEN ? AND ?
                    ORDER BY date_bucket
                """, (bucket_type, start_date.date().isoformat(), end_date.date().isoformat()))
                
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            print(f"Error getting analytics: {e}")
            return []
    
    async def record_compliance_event(
        self,
        incident_id: str,
        framework: str,
        event_type: str,
        event_data: Dict[str, Any],
        compliance_status: str = "pending"
    ) -> bool:
        """
        Record a compliance event.
        
        Args:
            incident_id: Incident identifier
            framework: Compliance framework (DPDP, PCI_DSS, etc.)
            event_type: Type of compliance event
            event_data: Event details
            compliance_status: Compliance status
            
        Returns:
            Success status
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO compliance_events 
                    (incident_id, framework, event_type, event_timestamp, 
                     event_data, compliance_status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    incident_id, framework, event_type, datetime.utcnow(),
                    json.dumps(event_data), compliance_status
                ))
                await db.commit()
                return True
                
        except Exception as e:
            print(f"Error recording compliance event: {e}")
            return False
    
    async def record_performance_metric(
        self,
        incident_id: str,
        metric_name: str,
        metric_value: float,
        metric_context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Record a performance metric.
        
        Args:
            incident_id: Incident identifier
            metric_name: Name of the metric
            metric_value: Metric value
            metric_context: Additional context
            
        Returns:
            Success status
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute("""
                    INSERT INTO performance_metrics 
                    (incident_id, metric_name, metric_value, metric_timestamp, metric_context)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    incident_id, metric_name, metric_value, datetime.utcnow(),
                    json.dumps(metric_context or {})
                ))
                await db.commit()
                return True
                
        except Exception as e:
            print(f"Error recording performance metric: {e}")
            return False
    
    async def get_incident_history(self, incident_id: str) -> List[Dict[str, Any]]:
        """
        Get incident change history.
        
        Args:
            incident_id: Incident identifier
            
        Returns:
            List of history records
        """
        try:
            async with aiosqlite.connect(self.db_path) as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute("""
                    SELECT * FROM incident_history 
                    WHERE incident_id = ?
                    ORDER BY timestamp DESC
                """, (incident_id,))
                
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            print(f"Error getting incident history: {e}")
            return []
    
    async def cleanup_old_records(self, retention_days: int = 365) -> int:
        """
        Clean up old incident records.
        
        Args:
            retention_days: Number of days to retain records
            
        Returns:
            Number of records cleaned up
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            async with aiosqlite.connect(self.db_path) as db:
                # Count records to be deleted
                cursor = await db.execute("""
                    SELECT COUNT(*) FROM incidents 
                    WHERE created_at < ? AND status = 'closed'
                """, (cutoff_date,))
                count = (await cursor.fetchone())[0]
                
                # Delete old closed incidents
                await db.execute("""
                    DELETE FROM incidents 
                    WHERE created_at < ? AND status = 'closed'
                """, (cutoff_date,))
                
                # Clean up related records
                await db.execute("""
                    DELETE FROM incident_history 
                    WHERE incident_id NOT IN (SELECT incident_id FROM incidents)
                """)
                
                await db.execute("""
                    DELETE FROM compliance_events 
                    WHERE incident_id NOT IN (SELECT incident_id FROM incidents)
                """)
                
                await db.execute("""
                    DELETE FROM performance_metrics 
                    WHERE incident_id NOT IN (SELECT incident_id FROM incidents)
                """)
                
                await db.commit()
                return count
                
        except Exception as e:
            print(f"Error cleaning up old records: {e}")
            return 0
    
    def _state_to_record(self, state: IncidentState) -> IncidentRecord:
        """Convert incident state to database record."""
        
        # Calculate processing time
        processing_time = (state.updated_at - state.created_at).total_seconds()
        
        # Extract compliance frameworks
        compliance_frameworks = []
        if state.compliance_checks:
            compliance_frameworks = list(state.compliance_checks.keys())
        
        # Count safety violations
        safety_violations = 0
        safety_result = state.tool_results.get("safety_check", {})
        if safety_result.get("violations"):
            safety_violations = len(safety_result["violations"])
        
        return IncidentRecord(
            incident_id=state.incident_id,
            title=state.title,
            description=state.description,
            category=state.category.value if state.category else None,
            priority=state.severity.value if state.severity else None,
            created_at=state.created_at,
            updated_at=state.updated_at,
            risk_score=state.risk_assessment.risk_score if state.risk_assessment else None,
            classification_confidence=state.classification_confidence,
            processing_time_seconds=processing_time,
            human_interventions=len(state.approval_history),
            workflow_steps_completed=len(state.completed_steps),
            workflow_steps_failed=len(state.failed_steps),
            metadata_json=json.dumps(state.metadata.dict()),
            tool_results_json=json.dumps(state.tool_results),
            response_plan_json=json.dumps(state.incident_response.dict() if state.incident_response else {}),
            quality_scores_json=json.dumps(state.quality_scores),
            compliance_frameworks=",".join([fw.value for fw in compliance_frameworks]),
            safety_violations=safety_violations,
            requires_followup=state.requires_human_intervention
        )
    
    async def _insert_incident_record(self, db: aiosqlite.Connection, record: IncidentRecord):
        """Insert new incident record."""
        await db.execute("""
            INSERT INTO incidents (
                incident_id, title, description, category, priority, status,
                created_at, updated_at, resolved_at, risk_score, classification_confidence,
                processing_time_seconds, human_interventions, workflow_steps_completed,
                workflow_steps_failed, metadata_json, tool_results_json, response_plan_json,
                quality_scores_json, compliance_frameworks, safety_violations, requires_followup
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.incident_id, record.title, record.description, record.category,
            record.priority, record.status, record.created_at, record.updated_at,
            record.resolved_at, record.risk_score, record.classification_confidence,
            record.processing_time_seconds, record.human_interventions,
            record.workflow_steps_completed, record.workflow_steps_failed,
            record.metadata_json, record.tool_results_json, record.response_plan_json,
            record.quality_scores_json, record.compliance_frameworks,
            record.safety_violations, record.requires_followup
        ))
    
    async def _update_incident_record(self, db: aiosqlite.Connection, record: IncidentRecord):
        """Update existing incident record."""
        await db.execute("""
            UPDATE incidents SET
                title = ?, description = ?, category = ?, priority = ?, status = ?,
                updated_at = ?, resolved_at = ?, risk_score = ?, classification_confidence = ?,
                processing_time_seconds = ?, human_interventions = ?, workflow_steps_completed = ?,
                workflow_steps_failed = ?, metadata_json = ?, tool_results_json = ?,
                response_plan_json = ?, quality_scores_json = ?, compliance_frameworks = ?,
                safety_violations = ?, requires_followup = ?
            WHERE incident_id = ?
        """, (
            record.title, record.description, record.category, record.priority,
            record.status, record.updated_at, record.resolved_at, record.risk_score,
            record.classification_confidence, record.processing_time_seconds,
            record.human_interventions, record.workflow_steps_completed,
            record.workflow_steps_failed, record.metadata_json, record.tool_results_json,
            record.response_plan_json, record.quality_scores_json,
            record.compliance_frameworks, record.safety_violations,
            record.requires_followup, record.incident_id
        ))
    
    async def _record_incident_history(
        self,
        db: aiosqlite.Connection,
        incident_id: str,
        change_type: str,
        change_data: Dict[str, Any]
    ):
        """Record incident history."""
        await db.execute("""
            INSERT INTO incident_history (incident_id, timestamp, change_type, change_data)
            VALUES (?, ?, ?, ?)
        """, (incident_id, datetime.utcnow(), change_type, json.dumps(change_data, default=str)))
    
    async def _generate_analytics(
        self,
        start_date: datetime,
        end_date: datetime,
        bucket_type: str
    ):
        """Generate analytics data if not exists."""
        # This is a simplified implementation
        # In production, you'd implement comprehensive analytics generation
        pass