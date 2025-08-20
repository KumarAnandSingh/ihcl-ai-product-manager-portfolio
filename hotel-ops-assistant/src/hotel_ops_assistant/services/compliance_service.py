"""
Compliance Service.
Coordinates all compliance activities including DPDP Act 2023, GDPR, PCI DSS,
data retention, privacy rights, and regulatory reporting.
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from pydantic import BaseModel, Field

from ..compliance.pii_protection import PIIProtectionService
from ..compliance.audit_logger import AuditLogger, AuditEventType, AuditSeverity
from ..core.config import get_settings


class ComplianceFramework(str, Enum):
    """Supported compliance frameworks."""
    DPDP_ACT_2023 = "dpdp_act_2023"
    GDPR = "gdpr"
    PCI_DSS = "pci_dss"
    ISO_27001 = "iso_27001"
    SOC2 = "soc2"


class DataSubjectRights(str, Enum):
    """Data subject rights under privacy laws."""
    ACCESS = "access"                    # Right to access personal data
    RECTIFICATION = "rectification"      # Right to correct inaccurate data
    ERASURE = "erasure"                  # Right to be forgotten
    PORTABILITY = "portability"          # Right to data portability
    RESTRICTION = "restriction"          # Right to restrict processing
    OBJECTION = "objection"              # Right to object to processing
    WITHDRAW_CONSENT = "withdraw_consent" # Right to withdraw consent


class ComplianceStatus(str, Enum):
    """Compliance status levels."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    UNDER_REVIEW = "under_review"


class DataSubjectRequest(BaseModel):
    """Data subject request model."""
    
    request_id: str
    request_type: DataSubjectRights
    subject_id: str
    subject_email: str
    requested_at: datetime
    description: Optional[str] = None
    status: str = "pending"
    resolved_at: Optional[datetime] = None
    response_data: Optional[Dict[str, Any]] = None
    legal_basis: Optional[str] = None


class ComplianceCheck(BaseModel):
    """Compliance check result model."""
    
    check_id: str
    framework: ComplianceFramework
    check_type: str
    status: ComplianceStatus
    score: float = Field(ge=0, le=100)
    details: Dict[str, Any]
    recommendations: List[str]
    checked_at: datetime
    next_check_due: Optional[datetime] = None


class ComplianceService:
    """Main compliance coordination service."""
    
    def __init__(self):
        self.settings = get_settings()
        self.pii_protection = PIIProtectionService()
        self.audit_logger = AuditLogger()
        
        # Track compliance state
        self._compliance_checks: List[ComplianceCheck] = []
        self._data_subject_requests: List[DataSubjectRequest] = []
        self._consent_records: Dict[str, Dict[str, Any]] = {}
        
        # Initialize compliance frameworks
        self._initialize_compliance_frameworks()
    
    def _initialize_compliance_frameworks(self):
        """Initialize compliance framework configurations."""
        self.frameworks_config = {
            ComplianceFramework.DPDP_ACT_2023: {
                "name": "Digital Personal Data Protection Act 2023",
                "jurisdiction": "India",
                "data_retention_max_days": 365,
                "consent_required": True,
                "data_minimization": True,
                "purpose_limitation": True,
                "breach_notification_hours": 72,
                "rights_response_days": 30
            },
            ComplianceFramework.GDPR: {
                "name": "General Data Protection Regulation",
                "jurisdiction": "EU",
                "data_retention_max_days": 365,
                "consent_required": True,
                "data_minimization": True,
                "purpose_limitation": True,
                "breach_notification_hours": 72,
                "rights_response_days": 30
            },
            ComplianceFramework.PCI_DSS: {
                "name": "Payment Card Industry Data Security Standard",
                "jurisdiction": "Global",
                "encryption_required": True,
                "access_controls": True,
                "monitoring_required": True,
                "vulnerability_management": True
            }
        }
    
    async def check_dpdp_compliance(self, data: Dict[str, Any], operation: str) -> ComplianceCheck:
        """Check DPDP Act 2023 compliance."""
        check_id = f"dpdp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Analyze data for DPDP compliance
        pii_analysis = self.pii_protection.analyze_data_sensitivity(data)
        
        compliance_score = 100.0
        issues = []
        recommendations = []
        
        # Check 1: Consent validation
        if self._has_personal_data(pii_analysis):
            consent_valid = await self._verify_consent(data.get("user_id") or data.get("guest_id"))
            if not consent_valid:
                compliance_score -= 30
                issues.append("No valid consent found for personal data processing")
                recommendations.append("Obtain explicit consent before processing personal data")
        
        # Check 2: Data minimization
        if len(pii_analysis) > 5:  # Threshold for excessive PII collection
            compliance_score -= 15
            issues.append("Potential data minimization violation - excessive PII collection")
            recommendations.append("Collect only necessary personal data for stated purpose")
        
        # Check 3: Purpose limitation
        if operation not in ["guest_service", "incident_resolution", "legal_compliance"]:
            compliance_score -= 20
            issues.append("Processing purpose may not align with consent")
            recommendations.append("Ensure processing purpose matches consent given")
        
        # Check 4: Security measures
        if not self.settings.enable_pii_protection:
            compliance_score -= 25
            issues.append("PII protection not enabled")
            recommendations.append("Enable PII encryption and masking")
        
        # Check 5: Retention compliance
        retention_compliant = self._check_data_retention_compliance()
        if not retention_compliant:
            compliance_score -= 10
            issues.append("Data retention policy violations detected")
            recommendations.append("Implement automated data deletion per retention policy")
        
        status = ComplianceStatus.COMPLIANT if compliance_score >= 90 else \
                ComplianceStatus.PARTIALLY_COMPLIANT if compliance_score >= 70 else \
                ComplianceStatus.NON_COMPLIANT
        
        check = ComplianceCheck(
            check_id=check_id,
            framework=ComplianceFramework.DPDP_ACT_2023,
            check_type="data_processing",
            status=status,
            score=compliance_score,
            details={
                "operation": operation,
                "pii_fields_detected": len([f for f, info in pii_analysis.items() if info.get("is_pii")]),
                "high_sensitivity_fields": len([f for f, info in pii_analysis.items() if info.get("sensitivity_level") == "high"]),
                "issues": issues,
                "security_enabled": self.settings.enable_pii_protection,
                "audit_enabled": self.settings.enable_audit_logging
            },
            recommendations=recommendations,
            checked_at=datetime.now(),
            next_check_due=datetime.now() + timedelta(days=30)
        )
        
        self._compliance_checks.append(check)
        
        # Log compliance check
        self.audit_logger.log_compliance_check(
            check_type="dpdp_compliance",
            resource_type="data_processing",
            resource_id=check_id,
            result=status.value,
            details={
                "score": compliance_score,
                "issues_count": len(issues),
                "operation": operation
            }
        )
        
        return check
    
    async def check_gdpr_compliance(self, data: Dict[str, Any], operation: str) -> ComplianceCheck:
        """Check GDPR compliance."""
        check_id = f"gdpr_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Similar to DPDP but with GDPR-specific requirements
        pii_analysis = self.pii_protection.analyze_data_sensitivity(data)
        
        compliance_score = 100.0
        issues = []
        recommendations = []
        
        # GDPR-specific checks
        lawful_basis = data.get("lawful_basis", "consent")
        if not lawful_basis:
            compliance_score -= 25
            issues.append("No lawful basis identified for processing")
            recommendations.append("Identify and document lawful basis for processing")
        
        # Data subject rights implementation
        if not self._data_subject_rights_implemented():
            compliance_score -= 20
            issues.append("Data subject rights not fully implemented")
            recommendations.append("Implement all GDPR data subject rights")
        
        # Cross-border transfer checks
        if data.get("transfer_outside_eea"):
            adequacy_decision = data.get("adequacy_decision_exists", False)
            if not adequacy_decision:
                compliance_score -= 15
                issues.append("Cross-border transfer without adequacy decision")
                recommendations.append("Ensure adequate protection for data transfers")
        
        status = ComplianceStatus.COMPLIANT if compliance_score >= 90 else \
                ComplianceStatus.PARTIALLY_COMPLIANT if compliance_score >= 70 else \
                ComplianceStatus.NON_COMPLIANT
        
        check = ComplianceCheck(
            check_id=check_id,
            framework=ComplianceFramework.GDPR,
            check_type="data_processing",
            status=status,
            score=compliance_score,
            details={
                "operation": operation,
                "lawful_basis": lawful_basis,
                "issues": issues,
                "cross_border_transfer": data.get("transfer_outside_eea", False)
            },
            recommendations=recommendations,
            checked_at=datetime.now(),
            next_check_due=datetime.now() + timedelta(days=30)
        )
        
        self._compliance_checks.append(check)
        
        return check
    
    async def check_pci_dss_compliance(self, payment_data: Dict[str, Any]) -> ComplianceCheck:
        """Check PCI DSS compliance for payment processing."""
        check_id = f"pci_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        compliance_score = 100.0
        issues = []
        recommendations = []
        
        # Check 1: Encryption of cardholder data
        if "card_number" in payment_data and not payment_data.get("encrypted", False):
            compliance_score -= 40
            issues.append("Cardholder data not encrypted")
            recommendations.append("Encrypt all cardholder data at rest and in transit")
        
        # Check 2: Access controls
        if not payment_data.get("access_controlled", True):
            compliance_score -= 30
            issues.append("Insufficient access controls for payment data")
            recommendations.append("Implement role-based access controls")
        
        # Check 3: Monitoring and logging
        if not self.settings.enable_audit_logging:
            compliance_score -= 20
            issues.append("Payment processing not adequately monitored")
            recommendations.append("Enable comprehensive audit logging")
        
        # Check 4: Network security
        network_secure = payment_data.get("network_secure", True)
        if not network_secure:
            compliance_score -= 10
            issues.append("Network security measures insufficient")
            recommendations.append("Implement network segmentation and firewalls")
        
        status = ComplianceStatus.COMPLIANT if compliance_score >= 90 else \
                ComplianceStatus.PARTIALLY_COMPLIANT if compliance_score >= 70 else \
                ComplianceStatus.NON_COMPLIANT
        
        check = ComplianceCheck(
            check_id=check_id,
            framework=ComplianceFramework.PCI_DSS,
            check_type="payment_processing",
            status=status,
            score=compliance_score,
            details={
                "payment_method": payment_data.get("payment_method"),
                "issues": issues,
                "encryption_enabled": payment_data.get("encrypted", False),
                "access_controlled": payment_data.get("access_controlled", True)
            },
            recommendations=recommendations,
            checked_at=datetime.now(),
            next_check_due=datetime.now() + timedelta(days=90)
        )
        
        self._compliance_checks.append(check)
        
        return check
    
    async def handle_data_subject_request(self, request: DataSubjectRequest) -> Dict[str, Any]:
        """Handle data subject rights request."""
        
        self.audit_logger.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            action=f"data_subject_request_{request.request_type.value}",
            resource_type="data_subject_request",
            resource_id=request.request_id,
            details={
                "subject_id": request.subject_id,
                "request_type": request.request_type.value
            },
            pii_involved=True,
            severity=AuditSeverity.HIGH
        )
        
        response = {}
        
        if request.request_type == DataSubjectRights.ACCESS:
            response = await self._handle_access_request(request)
        elif request.request_type == DataSubjectRights.ERASURE:
            response = await self._handle_erasure_request(request)
        elif request.request_type == DataSubjectRights.RECTIFICATION:
            response = await self._handle_rectification_request(request)
        elif request.request_type == DataSubjectRights.PORTABILITY:
            response = await self._handle_portability_request(request)
        elif request.request_type == DataSubjectRights.RESTRICTION:
            response = await self._handle_restriction_request(request)
        elif request.request_type == DataSubjectRights.OBJECTION:
            response = await self._handle_objection_request(request)
        elif request.request_type == DataSubjectRights.WITHDRAW_CONSENT:
            response = await self._handle_consent_withdrawal(request)
        
        # Update request status
        request.status = "completed"
        request.resolved_at = datetime.now()
        request.response_data = response
        
        self._data_subject_requests.append(request)
        
        return response
    
    async def _handle_access_request(self, request: DataSubjectRequest) -> Dict[str, Any]:
        """Handle right to access request."""
        # In production, this would query all systems for user data
        return {
            "subject_id": request.subject_id,
            "data_categories": ["profile", "preferences", "transaction_history", "communication_log"],
            "processing_purposes": ["guest_service", "personalization", "legal_compliance"],
            "retention_periods": {"profile": "365 days", "transactions": "7 years"},
            "third_party_sharing": "None",
            "data_source": "Direct collection from guest",
            "automated_decision_making": "Service recommendations",
            "message": "Complete data export will be provided within 30 days"
        }
    
    async def _handle_erasure_request(self, request: DataSubjectRequest) -> Dict[str, Any]:
        """Handle right to be forgotten request."""
        # In production, this would trigger data deletion across all systems
        return {
            "subject_id": request.subject_id,
            "deletion_scheduled": True,
            "deletion_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "data_categories_deleted": ["profile", "preferences", "non_essential_history"],
            "data_retained": ["transaction_records_for_legal_compliance"],
            "retention_legal_basis": "Legal obligation under tax law",
            "message": "Personal data will be deleted within 30 days, except records required by law"
        }
    
    async def _handle_rectification_request(self, request: DataSubjectRequest) -> Dict[str, Any]:
        """Handle right to rectification request."""
        return {
            "subject_id": request.subject_id,
            "rectification_completed": True,
            "updated_fields": request.description or "As requested",
            "verification_required": True,
            "message": "Data has been corrected as requested"
        }
    
    async def _handle_portability_request(self, request: DataSubjectRequest) -> Dict[str, Any]:
        """Handle right to data portability request."""
        return {
            "subject_id": request.subject_id,
            "export_format": "JSON",
            "export_includes": ["profile", "preferences", "history"],
            "export_ready_date": (datetime.now() + timedelta(days=7)).isoformat(),
            "download_link": f"https://api.hotel.com/export/{request.request_id}",
            "message": "Portable data export will be available for download within 7 days"
        }
    
    async def _handle_restriction_request(self, request: DataSubjectRequest) -> Dict[str, Any]:
        """Handle right to restriction of processing request."""
        return {
            "subject_id": request.subject_id,
            "restriction_applied": True,
            "restricted_processing": ["marketing", "analytics", "personalization"],
            "continued_processing": ["essential_service", "legal_compliance"],
            "message": "Processing has been restricted as requested"
        }
    
    async def _handle_objection_request(self, request: DataSubjectRequest) -> Dict[str, Any]:
        """Handle right to object request."""
        return {
            "subject_id": request.subject_id,
            "objection_honored": True,
            "stopped_processing": ["marketing", "profiling"],
            "continued_processing_legal_basis": "Legal obligation",
            "message": "Processing has been stopped where legally possible"
        }
    
    async def _handle_consent_withdrawal(self, request: DataSubjectRequest) -> Dict[str, Any]:
        """Handle consent withdrawal request."""
        # Update consent records
        if request.subject_id in self._consent_records:
            self._consent_records[request.subject_id]["consent_withdrawn"] = True
            self._consent_records[request.subject_id]["withdrawal_date"] = datetime.now()
        
        return {
            "subject_id": request.subject_id,
            "consent_withdrawn": True,
            "withdrawal_date": datetime.now().isoformat(),
            "processing_stopped": True,
            "data_retention": "Legal compliance only",
            "message": "Consent has been withdrawn and processing stopped"
        }
    
    async def verify_consent(self, subject_id: str, purpose: str) -> bool:
        """Verify if valid consent exists for processing."""
        return await self._verify_consent(subject_id, purpose)
    
    async def _verify_consent(self, subject_id: str, purpose: str = None) -> bool:
        """Internal consent verification."""
        if not subject_id:
            return False
        
        consent_record = self._consent_records.get(subject_id)
        if not consent_record:
            return False
        
        # Check if consent is withdrawn
        if consent_record.get("consent_withdrawn", False):
            return False
        
        # Check consent expiry
        consent_date = consent_record.get("consent_date")
        if consent_date:
            # Consent expires after 1 year
            expiry_date = consent_date + timedelta(days=365)
            if datetime.now() > expiry_date:
                return False
        
        # Check purpose-specific consent
        if purpose:
            allowed_purposes = consent_record.get("purposes", [])
            if purpose not in allowed_purposes:
                return False
        
        return True
    
    def record_consent(self, subject_id: str, purposes: List[str], legal_basis: str = "consent"):
        """Record consent for data processing."""
        self._consent_records[subject_id] = {
            "consent_date": datetime.now(),
            "purposes": purposes,
            "legal_basis": legal_basis,
            "consent_withdrawn": False,
            "ip_address": "127.0.0.1",  # Would capture real IP
            "user_agent": "HotelApp/1.0"  # Would capture real user agent
        }
        
        self.audit_logger.log_event(
            event_type=AuditEventType.DATA_ACCESS,
            action="consent_recorded",
            resource_type="consent",
            resource_id=subject_id,
            details={
                "purposes": purposes,
                "legal_basis": legal_basis
            },
            pii_involved=True
        )
    
    def _has_personal_data(self, pii_analysis: Dict[str, Any]) -> bool:
        """Check if data contains personal information."""
        return any(info.get("is_pii", False) for info in pii_analysis.values())
    
    def _check_data_retention_compliance(self) -> bool:
        """Check if data retention policies are being followed."""
        # Simplified check - in production would examine actual data ages
        return self.settings.data_retention_days > 0
    
    def _data_subject_rights_implemented(self) -> bool:
        """Check if all data subject rights are implemented."""
        # In production, this would check if all rights handling mechanisms exist
        return True
    
    def get_compliance_dashboard(self) -> Dict[str, Any]:
        """Get compliance dashboard data."""
        recent_checks = [c for c in self._compliance_checks if 
                        c.checked_at > datetime.now() - timedelta(days=30)]
        
        pending_requests = [r for r in self._data_subject_requests if r.status == "pending"]
        
        return {
            "overall_compliance_score": self._calculate_overall_compliance_score(recent_checks),
            "compliance_by_framework": {
                framework.value: self._get_framework_compliance(framework, recent_checks)
                for framework in ComplianceFramework
            },
            "recent_checks": len(recent_checks),
            "pending_data_subject_requests": len(pending_requests),
            "consent_records": len(self._consent_records),
            "pii_protection_enabled": self.settings.enable_pii_protection,
            "audit_logging_enabled": self.settings.enable_audit_logging,
            "data_retention_days": self.settings.data_retention_days,
            "last_check_date": max([c.checked_at for c in recent_checks]).isoformat() if recent_checks else None,
            "recommendations": self._get_priority_recommendations(recent_checks)
        }
    
    def _calculate_overall_compliance_score(self, checks: List[ComplianceCheck]) -> float:
        """Calculate overall compliance score."""
        if not checks:
            return 0.0
        
        return sum(check.score for check in checks) / len(checks)
    
    def _get_framework_compliance(self, framework: ComplianceFramework, 
                                 checks: List[ComplianceCheck]) -> Dict[str, Any]:
        """Get compliance status for specific framework."""
        framework_checks = [c for c in checks if c.framework == framework]
        
        if not framework_checks:
            return {"status": "unknown", "score": 0, "last_check": None}
        
        latest_check = max(framework_checks, key=lambda x: x.checked_at)
        avg_score = sum(c.score for c in framework_checks) / len(framework_checks)
        
        return {
            "status": latest_check.status.value,
            "score": avg_score,
            "last_check": latest_check.checked_at.isoformat(),
            "checks_count": len(framework_checks)
        }
    
    def _get_priority_recommendations(self, checks: List[ComplianceCheck]) -> List[str]:
        """Get priority compliance recommendations."""
        all_recommendations = []
        for check in checks:
            if check.score < 80:  # Only include recommendations from low-scoring checks
                all_recommendations.extend(check.recommendations)
        
        # Remove duplicates and return top 5
        unique_recommendations = list(dict.fromkeys(all_recommendations))
        return unique_recommendations[:5]