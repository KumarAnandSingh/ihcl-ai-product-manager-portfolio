"""
PII Protection Service.
Provides encryption, masking, and secure handling of personally identifiable information
in compliance with DPDP Act 2023, GDPR, and industry best practices.
"""

import hashlib
import secrets
from typing import Any, Dict, List, Optional, Set
import re
import base64
from datetime import datetime, timedelta

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from ..core.config import get_settings


class PIIDetector:
    """Detects and classifies PII in text and data structures."""
    
    # Regex patterns for PII detection
    PII_PATTERNS = {
        'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        'phone': re.compile(r'(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'),
        'credit_card': re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
        'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
        'aadhaar': re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
        'pan': re.compile(r'\b[A-Z]{5}\d{4}[A-Z]{1}\b'),
        'passport': re.compile(r'\b[A-Z]\d{7}\b|\b[A-Z]{2}\d{6}\b'),
        'ip_address': re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b'),
    }
    
    # Field names that commonly contain PII
    PII_FIELD_NAMES = {
        'name', 'first_name', 'last_name', 'full_name', 'email', 'phone', 'mobile',
        'address', 'street', 'city', 'postal_code', 'zip_code', 'ssn', 'social_security',
        'date_of_birth', 'dob', 'birthday', 'passport', 'license', 'aadhaar', 'pan',
        'credit_card', 'card_number', 'account_number', 'bank_account'
    }
    
    @classmethod
    def detect_pii_in_text(cls, text: str) -> Dict[str, List[str]]:
        """Detect PII patterns in text."""
        if not isinstance(text, str):
            return {}
        
        detected = {}
        for pii_type, pattern in cls.PII_PATTERNS.items():
            matches = pattern.findall(text)
            if matches:
                detected[pii_type] = matches
        
        return detected
    
    @classmethod
    def detect_pii_in_dict(cls, data: Dict[str, Any]) -> Set[str]:
        """Detect PII field names in dictionary."""
        pii_fields = set()
        
        for key in data.keys():
            if isinstance(key, str):
                key_lower = key.lower()
                if any(pii_field in key_lower for pii_field in cls.PII_FIELD_NAMES):
                    pii_fields.add(key)
        
        return pii_fields
    
    @classmethod
    def classify_sensitivity(cls, field_name: str, value: Any) -> str:
        """Classify data sensitivity level."""
        if not isinstance(field_name, str):
            return "public"
        
        field_lower = field_name.lower()
        
        # High sensitivity
        if any(term in field_lower for term in ['ssn', 'passport', 'credit_card', 'bank', 'password']):
            return "high"
        
        # Medium sensitivity  
        if any(term in field_lower for term in ['name', 'email', 'phone', 'address', 'dob']):
            return "medium"
        
        # Low sensitivity
        if any(term in field_lower for term in ['id', 'reference', 'number']):
            return "low"
        
        # Check value patterns
        if isinstance(value, str):
            pii_detected = cls.detect_pii_in_text(value)
            if pii_detected:
                if 'credit_card' in pii_detected or 'ssn' in pii_detected:
                    return "high"
                if 'email' in pii_detected or 'phone' in pii_detected:
                    return "medium"
        
        return "public"


class PIIEncryption:
    """Handles encryption and decryption of PII data."""
    
    def __init__(self, master_key: Optional[str] = None):
        self.settings = get_settings()
        self._master_key = master_key or self.settings.secret_key
        self._fernet = self._create_fernet()
    
    def _create_fernet(self) -> Fernet:
        """Create Fernet encryption instance."""
        # Use PBKDF2 to derive encryption key from master key
        password = self._master_key.encode()
        salt = b'hotel_ops_salt'  # In production, use random salt per instance
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt sensitive data."""
        if not data:
            return ""
        
        try:
            encrypted_data = self._fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
        except Exception as e:
            raise ValueError(f"Encryption failed: {str(e)}")
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        if not encrypted_data:
            return ""
        
        try:
            decoded_data = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted_data = self._fernet.decrypt(decoded_data)
            return decrypted_data.decode()
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")
    
    def encrypt_dict(self, data: Dict[str, Any], pii_fields: Set[str]) -> Dict[str, Any]:
        """Encrypt PII fields in a dictionary."""
        encrypted_data = data.copy()
        
        for field in pii_fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[f"{field}_encrypted"] = self.encrypt(str(encrypted_data[field]))
                del encrypted_data[field]
        
        return encrypted_data
    
    def decrypt_dict(self, data: Dict[str, Any], pii_fields: Set[str]) -> Dict[str, Any]:
        """Decrypt PII fields in a dictionary."""
        decrypted_data = data.copy()
        
        for field in pii_fields:
            encrypted_field = f"{field}_encrypted"
            if encrypted_field in decrypted_data and decrypted_data[encrypted_field]:
                decrypted_data[field] = self.decrypt(decrypted_data[encrypted_field])
                del decrypted_data[encrypted_field]
        
        return decrypted_data


class PIIMasking:
    """Handles masking and anonymization of PII data."""
    
    @staticmethod
    def mask_email(email: str) -> str:
        """Mask email address."""
        if not email or '@' not in email:
            return "*****"
        
        local, domain = email.split('@', 1)
        if len(local) <= 2:
            masked_local = "*" * len(local)
        else:
            masked_local = local[0] + "*" * (len(local) - 2) + local[-1]
        
        domain_parts = domain.split('.')
        if len(domain_parts[0]) <= 2:
            masked_domain = "*" * len(domain_parts[0])
        else:
            masked_domain = domain_parts[0][0] + "*" * (len(domain_parts[0]) - 2) + domain_parts[0][-1]
        
        return f"{masked_local}@{masked_domain}.{'*' * len('.'.join(domain_parts[1:]))}"
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """Mask phone number."""
        if not phone:
            return "*****"
        
        # Extract digits only
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 4:
            return "*" * len(phone)
        
        # Keep first 2 and last 2 digits
        return f"{digits[:2]}{'*' * (len(digits) - 4)}{digits[-2:]}"
    
    @staticmethod
    def mask_name(name: str) -> str:
        """Mask personal name."""
        if not name:
            return "*****"
        
        if len(name) <= 2:
            return "*" * len(name)
        
        return name[0] + "*" * (len(name) - 2) + name[-1]
    
    @staticmethod
    def mask_credit_card(card_number: str) -> str:
        """Mask credit card number."""
        if not card_number:
            return "*****"
        
        # Extract digits only
        digits = re.sub(r'\D', '', card_number)
        if len(digits) < 4:
            return "*" * len(card_number)
        
        # Show only last 4 digits
        return "*" * (len(digits) - 4) + digits[-4:]
    
    @classmethod
    def mask_value(cls, value: str, pii_type: str) -> str:
        """Mask value based on PII type."""
        if not value:
            return "*****"
        
        masking_functions = {
            'email': cls.mask_email,
            'phone': cls.mask_phone,
            'name': cls.mask_name,
            'first_name': cls.mask_name,
            'last_name': cls.mask_name,
            'credit_card': cls.mask_credit_card,
        }
        
        masking_func = masking_functions.get(pii_type.lower(), lambda x: "*****")
        return masking_func(value)
    
    @classmethod
    def mask_dict(cls, data: Dict[str, Any], pii_fields: Set[str]) -> Dict[str, Any]:
        """Mask PII fields in a dictionary."""
        masked_data = data.copy()
        
        for field in pii_fields:
            if field in masked_data and masked_data[field]:
                masked_data[field] = cls.mask_value(str(masked_data[field]), field)
        
        return masked_data


class PIIProtectionService:
    """Main PII protection service coordinating all privacy features."""
    
    def __init__(self):
        self.settings = get_settings()
        self.detector = PIIDetector()
        self.encryption = PIIEncryption()
        self.masking = PIIMasking()
        
        # Track data access for audit
        self._access_log = []
    
    def analyze_data_sensitivity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze data to identify PII and sensitivity levels."""
        pii_fields = self.detector.detect_pii_in_dict(data)
        
        sensitivity_analysis = {}
        for field, value in data.items():
            sensitivity_level = self.detector.classify_sensitivity(field, value)
            
            analysis = {
                "field": field,
                "is_pii": field in pii_fields,
                "sensitivity_level": sensitivity_level,
                "requires_encryption": sensitivity_level in ["high", "medium"],
                "requires_masking": sensitivity_level != "public"
            }
            
            # Check for PII patterns in text values
            if isinstance(value, str):
                pii_patterns = self.detector.detect_pii_in_text(value)
                if pii_patterns:
                    analysis["detected_patterns"] = pii_patterns
                    analysis["is_pii"] = True
            
            sensitivity_analysis[field] = analysis
        
        return sensitivity_analysis
    
    def protect_data(self, data: Dict[str, Any], operation: str = "store") -> Dict[str, Any]:
        """Apply appropriate PII protection based on operation."""
        if not self.settings.enable_pii_protection:
            return data
        
        analysis = self.analyze_data_sensitivity(data)
        
        # Determine which fields need protection
        encrypt_fields = {
            field for field, info in analysis.items()
            if info.get("requires_encryption", False)
        }
        
        mask_fields = {
            field for field, info in analysis.items()
            if info.get("requires_masking", False)
        }
        
        if operation == "store":
            # Encrypt sensitive data for storage
            protected_data = self.encryption.encrypt_dict(data, encrypt_fields)
        elif operation == "display":
            # Mask data for display
            protected_data = self.masking.mask_dict(data, mask_fields)
        elif operation == "api_response":
            # Mask for API responses (unless explicitly authorized)
            protected_data = self.masking.mask_dict(data, mask_fields)
        else:
            protected_data = data.copy()
        
        # Log data access
        self._log_data_access(data, operation, analysis)
        
        return protected_data
    
    def unprotect_data(self, data: Dict[str, Any], user_id: str, purpose: str) -> Dict[str, Any]:
        """Decrypt data for authorized access."""
        if not self.settings.enable_pii_protection:
            return data
        
        # Check authorization (simplified for demo)
        if not self._check_data_access_authorization(user_id, purpose):
            raise PermissionError(f"User {user_id} not authorized for purpose: {purpose}")
        
        # Find encrypted fields
        encrypted_fields = {
            field.replace("_encrypted", "") for field in data.keys()
            if field.endswith("_encrypted")
        }
        
        if encrypted_fields:
            unprotected_data = self.encryption.decrypt_dict(data, encrypted_fields)
        else:
            unprotected_data = data.copy()
        
        # Log data access
        self._log_data_access(unprotected_data, f"decrypt_{purpose}", {}, user_id)
        
        return unprotected_data
    
    def _check_data_access_authorization(self, user_id: str, purpose: str) -> bool:
        """Check if user is authorized to access PII for given purpose."""
        # Simplified authorization logic
        authorized_purposes = {
            "guest_service", "incident_resolution", "fraud_investigation",
            "compliance_audit", "legal_requirement"
        }
        
        return purpose in authorized_purposes
    
    def _log_data_access(self, data: Dict[str, Any], operation: str, 
                        analysis: Dict[str, Any], user_id: Optional[str] = None):
        """Log data access for audit trail."""
        access_record = {
            "timestamp": datetime.now(),
            "operation": operation,
            "user_id": user_id,
            "data_fields": list(data.keys()),
            "pii_fields": [
                field for field, info in analysis.items()
                if info.get("is_pii", False)
            ] if analysis else [],
            "sensitivity_levels": {
                field: info.get("sensitivity_level", "unknown")
                for field, info in analysis.items()
            } if analysis else {}
        }
        
        self._access_log.append(access_record)
        
        # Keep only recent records (in production, this would go to persistent storage)
        if len(self._access_log) > 1000:
            self._access_log = self._access_log[-1000:]
    
    def get_data_access_audit(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get audit trail of data access."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        return [
            record for record in self._access_log
            if record["timestamp"] >= cutoff_time
        ]
    
    def anonymize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymize data by removing all PII."""
        analysis = self.analyze_data_sensitivity(data)
        anonymized_data = {}
        
        for field, value in data.items():
            field_analysis = analysis.get(field, {})
            
            if not field_analysis.get("is_pii", False):
                # Keep non-PII data
                anonymized_data[field] = value
            else:
                # Replace PII with generic identifiers
                if "id" in field.lower():
                    anonymized_data[field] = f"anonymous_{secrets.token_hex(4)}"
                elif "name" in field.lower():
                    anonymized_data[field] = "Anonymous User"
                elif "email" in field.lower():
                    anonymized_data[field] = f"user{secrets.token_hex(4)}@anonymous.com"
                else:
                    anonymized_data[field] = "[ANONYMIZED]"
        
        return anonymized_data
    
    def generate_privacy_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate privacy compliance report for data."""
        analysis = self.analyze_data_sensitivity(data)
        
        pii_fields = [field for field, info in analysis.items() if info.get("is_pii")]
        high_sensitivity_fields = [
            field for field, info in analysis.items()
            if info.get("sensitivity_level") == "high"
        ]
        
        report = {
            "timestamp": datetime.now(),
            "total_fields": len(data),
            "pii_fields_count": len(pii_fields),
            "pii_fields": pii_fields,
            "high_sensitivity_fields": high_sensitivity_fields,
            "compliance_status": {
                "encryption_required": len([
                    f for f, info in analysis.items()
                    if info.get("requires_encryption")
                ]),
                "masking_required": len([
                    f for f, info in analysis.items()
                    if info.get("requires_masking")
                ]),
                "pii_protection_enabled": self.settings.enable_pii_protection
            },
            "data_sensitivity_distribution": {
                level: len([
                    f for f, info in analysis.items()
                    if info.get("sensitivity_level") == level
                ])
                for level in ["public", "low", "medium", "high"]
            },
            "recommendations": self._generate_privacy_recommendations(analysis)
        }
        
        return report
    
    def _generate_privacy_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate privacy compliance recommendations."""
        recommendations = []
        
        high_sensitivity_fields = [
            field for field, info in analysis.items()
            if info.get("sensitivity_level") == "high"
        ]
        
        if high_sensitivity_fields:
            recommendations.append(
                f"Enable field-level encryption for high sensitivity fields: {', '.join(high_sensitivity_fields)}"
            )
        
        pii_fields = [field for field, info in analysis.items() if info.get("is_pii")]
        if len(pii_fields) > 5:
            recommendations.append(
                "Consider data minimization - reduce collection of PII fields where possible"
            )
        
        if not self.settings.enable_pii_protection:
            recommendations.append("Enable PII protection in system configuration")
        
        return recommendations