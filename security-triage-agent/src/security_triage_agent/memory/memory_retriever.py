"""
Memory Retrieval System for Security Incident Triage Agent.

Provides intelligent retrieval of historical incidents, patterns, and context
to inform current incident processing and improve decision-making.
"""

import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Tuple
from pydantic import BaseModel, Field
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from .persistent_storage import PersistentStorage, IncidentRecord
from ..core.state import IncidentCategory, IncidentPriority


class SimilarIncident(BaseModel):
    """Similar incident with relevance score."""
    incident_record: IncidentRecord
    similarity_score: float = Field(ge=0.0, le=1.0)
    similarity_factors: List[str] = Field(default_factory=list)


class IncidentPattern(BaseModel):
    """Identified incident pattern."""
    pattern_id: str
    pattern_type: str  # "temporal", "categorical", "severity_escalation", etc.
    description: str
    confidence: float = Field(ge=0.0, le=1.0)
    incidents: List[str] = Field(default_factory=list)  # incident IDs
    characteristics: Dict[str, Any] = Field(default_factory=dict)
    recommendation: str = ""


class HistoricalContext(BaseModel):
    """Historical context for incident processing."""
    similar_incidents: List[SimilarIncident] = Field(default_factory=list)
    identified_patterns: List[IncidentPattern] = Field(default_factory=list)
    category_statistics: Dict[str, Any] = Field(default_factory=dict)
    temporal_trends: Dict[str, Any] = Field(default_factory=dict)
    success_metrics: Dict[str, float] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)


class MemoryRetriever:
    """
    Intelligent memory retrieval system for incident analysis.
    
    Provides similarity search, pattern detection, and historical context
    to enhance incident processing with organizational learning.
    """
    
    def __init__(
        self,
        storage: PersistentStorage,
        similarity_threshold: float = 0.7,
        max_similar_incidents: int = 5
    ):
        self.storage = storage
        self.similarity_threshold = similarity_threshold
        self.max_similar_incidents = max_similar_incidents
        
        # Text vectorizer for similarity analysis
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        # Cache for vectorized incidents
        self._incident_vectors = {}
        self._last_vectorization = None
    
    async def get_historical_context(
        self,
        title: str,
        description: str,
        category: Optional[IncidentCategory] = None,
        priority: Optional[IncidentPriority] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> HistoricalContext:
        """
        Get comprehensive historical context for an incident.
        
        Args:
            title: Incident title
            description: Incident description
            category: Incident category (optional)
            priority: Incident priority (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            HistoricalContext with similar incidents, patterns, and insights
        """
        
        context = HistoricalContext()
        
        # Find similar incidents
        context.similar_incidents = await self.find_similar_incidents(
            title, description, category
        )
        
        # Identify patterns
        context.identified_patterns = await self.identify_patterns(
            category, description, metadata
        )
        
        # Get category statistics
        if category:
            context.category_statistics = await self.get_category_statistics(category)
        
        # Get temporal trends
        context.temporal_trends = await self.get_temporal_trends(category)
        
        # Calculate success metrics
        context.success_metrics = await self.calculate_success_metrics(
            context.similar_incidents
        )
        
        # Generate recommendations
        context.recommendations = self.generate_recommendations(
            context.similar_incidents,
            context.identified_patterns,
            context.success_metrics
        )
        
        return context
    
    async def find_similar_incidents(
        self,
        title: str,
        description: str,
        category: Optional[IncidentCategory] = None,
        limit: int = None
    ) -> List[SimilarIncident]:
        """
        Find incidents similar to the given description.
        
        Args:
            title: Incident title
            description: Incident description
            category: Incident category filter
            limit: Maximum number of results
            
        Returns:
            List of similar incidents with similarity scores
        """
        
        if limit is None:
            limit = self.max_similar_incidents
        
        # Get recent incidents for comparison
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=365)  # Last year
        
        filters = {"created_after": start_date}
        if category:
            filters["category"] = category.value
        
        incidents = await self.storage.search_incidents(
            filters=filters,
            limit=1000  # Large limit for comprehensive search
        )
        
        if not incidents:
            return []
        
        # Vectorize incidents if needed
        await self._update_incident_vectors(incidents)
        
        # Vectorize the query
        query_text = f"{title} {description}"
        query_vector = self.vectorizer.transform([query_text])
        
        # Calculate similarities
        similar_incidents = []
        
        for incident in incidents:
            if incident.incident_id in self._incident_vectors:
                incident_vector = self._incident_vectors[incident.incident_id]
                similarity = cosine_similarity(query_vector, incident_vector)[0][0]
                
                if similarity >= self.similarity_threshold:
                    # Determine similarity factors
                    factors = self._analyze_similarity_factors(
                        title, description, incident
                    )
                    
                    similar_incidents.append(SimilarIncident(
                        incident_record=incident,
                        similarity_score=similarity,
                        similarity_factors=factors
                    ))
        
        # Sort by similarity and return top results
        similar_incidents.sort(key=lambda x: x.similarity_score, reverse=True)
        return similar_incidents[:limit]
    
    async def identify_patterns(
        self,
        category: Optional[IncidentCategory] = None,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[IncidentPattern]:
        """
        Identify patterns in historical incidents.
        
        Args:
            category: Incident category
            description: Incident description
            metadata: Additional metadata
            
        Returns:
            List of identified patterns
        """
        
        patterns = []
        
        # Get incidents for pattern analysis
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=90)  # Last 3 months
        
        filters = {"created_after": start_date}
        if category:
            filters["category"] = category.value
        
        incidents = await self.storage.search_incidents(filters=filters, limit=500)
        
        if len(incidents) < 5:  # Need minimum incidents for pattern detection
            return patterns
        
        # Temporal patterns
        temporal_pattern = self._analyze_temporal_patterns(incidents)
        if temporal_pattern:
            patterns.append(temporal_pattern)
        
        # Severity escalation patterns
        escalation_pattern = self._analyze_escalation_patterns(incidents)
        if escalation_pattern:
            patterns.append(escalation_pattern)
        
        # Category-specific patterns
        if category:
            category_patterns = self._analyze_category_patterns(incidents, category)
            patterns.extend(category_patterns)
        
        # Location-based patterns (if metadata available)
        if metadata and metadata.get("location"):
            location_pattern = await self._analyze_location_patterns(
                incidents, metadata["location"]
            )
            if location_pattern:
                patterns.append(location_pattern)
        
        return patterns
    
    async def get_category_statistics(
        self, category: IncidentCategory
    ) -> Dict[str, Any]:
        """
        Get statistics for a specific incident category.
        
        Args:
            category: Incident category
            
        Returns:
            Statistics dictionary
        """
        
        # Get category incidents from last 6 months
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=180)
        
        incidents = await self.storage.search_incidents(
            filters={
                "category": category.value,
                "created_after": start_date
            },
            limit=1000
        )
        
        if not incidents:
            return {}
        
        # Calculate statistics
        total_incidents = len(incidents)
        resolved_incidents = len([i for i in incidents if i.status == "resolved"])
        avg_processing_time = np.mean([
            i.processing_time_seconds for i in incidents 
            if i.processing_time_seconds is not None
        ])
        avg_risk_score = np.mean([
            i.risk_score for i in incidents 
            if i.risk_score is not None
        ])
        
        # Priority distribution
        priority_dist = {}
        for incident in incidents:
            priority = incident.priority or "unknown"
            priority_dist[priority] = priority_dist.get(priority, 0) + 1
        
        # Human intervention rate
        intervention_rate = len([
            i for i in incidents if i.human_interventions > 0
        ]) / total_incidents if total_incidents > 0 else 0
        
        return {
            "total_incidents": total_incidents,
            "resolution_rate": resolved_incidents / total_incidents if total_incidents > 0 else 0,
            "avg_processing_time_hours": avg_processing_time / 3600 if avg_processing_time else 0,
            "avg_risk_score": float(avg_risk_score) if not np.isnan(avg_risk_score) else 0,
            "priority_distribution": priority_dist,
            "human_intervention_rate": intervention_rate,
            "period_start": start_date.isoformat(),
            "period_end": end_date.isoformat()
        }
    
    async def get_temporal_trends(
        self, category: Optional[IncidentCategory] = None
    ) -> Dict[str, Any]:
        """
        Get temporal trends for incidents.
        
        Args:
            category: Optional category filter
            
        Returns:
            Temporal trends data
        """
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)  # Last 30 days
        
        filters = {"created_after": start_date}
        if category:
            filters["category"] = category.value
        
        incidents = await self.storage.search_incidents(filters=filters, limit=1000)
        
        # Group by day
        daily_counts = {}
        for incident in incidents:
            day = incident.created_at.date().isoformat()
            daily_counts[day] = daily_counts.get(day, 0) + 1
        
        # Calculate trend
        days = sorted(daily_counts.keys())
        if len(days) >= 7:  # Need at least a week of data
            recent_avg = np.mean([daily_counts.get(day, 0) for day in days[-7:]])
            previous_avg = np.mean([daily_counts.get(day, 0) for day in days[-14:-7]])
            trend = "increasing" if recent_avg > previous_avg * 1.2 else \
                   "decreasing" if recent_avg < previous_avg * 0.8 else "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "daily_counts": daily_counts,
            "trend": trend,
            "total_incidents": len(incidents),
            "period_days": (end_date.date() - start_date.date()).days
        }
    
    async def calculate_success_metrics(
        self, similar_incidents: List[SimilarIncident]
    ) -> Dict[str, float]:
        """
        Calculate success metrics based on similar incidents.
        
        Args:
            similar_incidents: List of similar incidents
            
        Returns:
            Success metrics dictionary
        """
        
        if not similar_incidents:
            return {}
        
        incidents = [si.incident_record for si in similar_incidents]
        
        # Resolution rate
        resolved_count = len([i for i in incidents if i.status == "resolved"])
        resolution_rate = resolved_count / len(incidents) if incidents else 0
        
        # Average processing time
        processing_times = [
            i.processing_time_seconds for i in incidents 
            if i.processing_time_seconds is not None
        ]
        avg_processing_time = np.mean(processing_times) if processing_times else 0
        
        # Quality score
        quality_scores = []
        for incident in incidents:
            try:
                quality_data = json.loads(incident.quality_scores_json)
                overall_score = quality_data.get("overall", 0.0)
                if overall_score > 0:
                    quality_scores.append(overall_score)
            except:
                continue
        
        avg_quality_score = np.mean(quality_scores) if quality_scores else 0
        
        # Human intervention rate
        intervention_rate = len([
            i for i in incidents if i.human_interventions > 0
        ]) / len(incidents) if incidents else 0
        
        return {
            "resolution_rate": resolution_rate,
            "avg_processing_time_hours": avg_processing_time / 3600,
            "avg_quality_score": avg_quality_score,
            "human_intervention_rate": intervention_rate,
            "sample_size": len(incidents)
        }
    
    def generate_recommendations(
        self,
        similar_incidents: List[SimilarIncident],
        patterns: List[IncidentPattern],
        success_metrics: Dict[str, float]
    ) -> List[str]:
        """
        Generate recommendations based on historical analysis.
        
        Args:
            similar_incidents: Similar incidents found
            patterns: Identified patterns
            success_metrics: Success metrics
            
        Returns:
            List of recommendations
        """
        
        recommendations = []
        
        # Recommendations based on similar incidents
        if similar_incidents:
            high_quality_incidents = [
                si for si in similar_incidents 
                if si.incident_record.status == "resolved"
            ]
            
            if high_quality_incidents:
                recommendations.append(
                    f"Found {len(high_quality_incidents)} similar resolved incidents. "
                    "Review their response approaches for best practices."
                )
            
            # Check for common human intervention patterns
            intervention_incidents = [
                si for si in similar_incidents 
                if si.incident_record.human_interventions > 0
            ]
            
            if len(intervention_incidents) > len(similar_incidents) * 0.5:
                recommendations.append(
                    "Similar incidents frequently required human intervention. "
                    "Consider preparing for escalation."
                )
        
        # Recommendations based on patterns
        for pattern in patterns:
            if pattern.recommendation:
                recommendations.append(pattern.recommendation)
        
        # Recommendations based on success metrics
        if success_metrics.get("human_intervention_rate", 0) > 0.7:
            recommendations.append(
                "High human intervention rate in similar cases. "
                "Prepare detailed documentation for review."
            )
        
        if success_metrics.get("avg_processing_time_hours", 0) > 4:
            recommendations.append(
                "Similar incidents typically take longer to resolve. "
                "Allow additional time and resources."
            )
        
        if success_metrics.get("avg_quality_score", 0) < 0.7:
            recommendations.append(
                "Quality scores for similar incidents suggest room for improvement. "
                "Focus on thorough analysis and documentation."
            )
        
        # Generic recommendations if no specific insights
        if not recommendations:
            recommendations.append(
                "Limited historical data available. Follow standard procedures."
            )
        
        return recommendations
    
    async def _update_incident_vectors(self, incidents: List[IncidentRecord]):
        """Update incident text vectors for similarity analysis."""
        
        # Check if we need to update vectors
        if (self._last_vectorization and 
            datetime.utcnow() - self._last_vectorization < timedelta(hours=1)):
            return
        
        # Prepare text documents
        documents = []
        incident_ids = []
        
        for incident in incidents:
            text = f"{incident.title} {incident.description}"
            documents.append(text)
            incident_ids.append(incident.incident_id)
        
        if documents:
            # Fit vectorizer and transform documents
            vectors = self.vectorizer.fit_transform(documents)
            
            # Store vectors
            self._incident_vectors = {}
            for i, incident_id in enumerate(incident_ids):
                self._incident_vectors[incident_id] = vectors[i]
            
            self._last_vectorization = datetime.utcnow()
    
    def _analyze_similarity_factors(
        self, title: str, description: str, incident: IncidentRecord
    ) -> List[str]:
        """Analyze factors contributing to incident similarity."""
        
        factors = []
        
        # Check title similarity
        title_words = set(title.lower().split())
        incident_title_words = set(incident.title.lower().split())
        title_overlap = len(title_words & incident_title_words)
        
        if title_overlap > 0:
            factors.append(f"title_overlap_{title_overlap}_words")
        
        # Check description keywords
        description_words = set(description.lower().split())
        incident_desc_words = set(incident.description.lower().split())
        desc_overlap = len(description_words & incident_desc_words)
        
        if desc_overlap > 2:
            factors.append(f"description_overlap_{desc_overlap}_words")
        
        # Check category match
        factors.append(f"category_{incident.category}")
        
        # Check priority match
        if incident.priority:
            factors.append(f"priority_{incident.priority}")
        
        return factors
    
    def _analyze_temporal_patterns(self, incidents: List[IncidentRecord]) -> Optional[IncidentPattern]:
        """Analyze temporal patterns in incidents."""
        
        if len(incidents) < 10:
            return None
        
        # Group by day of week
        day_counts = {}
        for incident in incidents:
            day = incident.created_at.strftime("%A")
            day_counts[day] = day_counts.get(day, 0) + 1
        
        # Find peak day
        if day_counts:
            peak_day = max(day_counts, key=day_counts.get)
            peak_count = day_counts[peak_day]
            total = sum(day_counts.values())
            
            if peak_count > total * 0.3:  # More than 30% on one day
                return IncidentPattern(
                    pattern_id=f"temporal_{peak_day}",
                    pattern_type="temporal",
                    description=f"Incidents peak on {peak_day} ({peak_count}/{total})",
                    confidence=peak_count / total,
                    incidents=[i.incident_id for i in incidents],
                    characteristics={"peak_day": peak_day, "distribution": day_counts},
                    recommendation=f"Increased readiness recommended for {peak_day}"
                )
        
        return None
    
    def _analyze_escalation_patterns(self, incidents: List[IncidentRecord]) -> Optional[IncidentPattern]:
        """Analyze escalation patterns."""
        
        escalated_incidents = [i for i in incidents if i.human_interventions > 0]
        escalation_rate = len(escalated_incidents) / len(incidents) if incidents else 0
        
        if escalation_rate > 0.4:  # High escalation rate
            return IncidentPattern(
                pattern_id="high_escalation",
                pattern_type="escalation",
                description=f"High escalation rate: {escalation_rate:.1%}",
                confidence=escalation_rate,
                incidents=[i.incident_id for i in escalated_incidents],
                characteristics={"escalation_rate": escalation_rate},
                recommendation="Prepare for potential escalation and human review"
            )
        
        return None
    
    def _analyze_category_patterns(
        self, incidents: List[IncidentRecord], category: IncidentCategory
    ) -> List[IncidentPattern]:
        """Analyze category-specific patterns."""
        
        patterns = []
        
        # Risk score patterns
        risk_scores = [i.risk_score for i in incidents if i.risk_score is not None]
        if risk_scores:
            avg_risk = np.mean(risk_scores)
            if avg_risk > 7.0:
                patterns.append(IncidentPattern(
                    pattern_id=f"high_risk_{category.value}",
                    pattern_type="risk",
                    description=f"High average risk score for {category.value}: {avg_risk:.1f}",
                    confidence=min(avg_risk / 10.0, 1.0),
                    incidents=[i.incident_id for i in incidents],
                    characteristics={"avg_risk_score": avg_risk},
                    recommendation="Enhanced risk assessment and containment measures recommended"
                ))
        
        return patterns
    
    async def _analyze_location_patterns(
        self, incidents: List[IncidentRecord], location: str
    ) -> Optional[IncidentPattern]:
        """Analyze location-based patterns."""
        
        # This would be enhanced with actual location analysis
        # For now, return a basic pattern if multiple incidents at same location
        
        location_incidents = []
        for incident in incidents:
            try:
                metadata = json.loads(incident.metadata_json)
                if metadata.get("location") == location:
                    location_incidents.append(incident)
            except:
                continue
        
        if len(location_incidents) > 2:
            return IncidentPattern(
                pattern_id=f"location_{location}",
                pattern_type="location",
                description=f"Multiple incidents at {location}",
                confidence=len(location_incidents) / len(incidents),
                incidents=[i.incident_id for i in location_incidents],
                characteristics={"location": location, "incident_count": len(location_incidents)},
                recommendation=f"Review security measures and procedures for {location}"
            )
        
        return None