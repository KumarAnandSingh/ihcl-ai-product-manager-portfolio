"""
Logging Configuration for Security Incident Triage Agent.

Provides structured logging with security-aware formatting,
audit trails, and performance monitoring integration.
"""

import logging
import logging.handlers
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import structlog
from pythonjsonlogger import jsonlogger


class SecurityAwareFormatter(logging.Formatter):
    """
    Security-aware log formatter that sanitizes sensitive information.
    
    Automatically redacts common PII patterns and security-sensitive data
    while maintaining log utility for debugging and audit purposes.
    """
    
    SENSITIVE_PATTERNS = [
        # Credit card patterns
        r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3[0-9]{13}|6(?:011|5[0-9]{2})[0-9]{12})\b',
        # Email patterns
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        # Phone patterns
        r'(\+?[1-9]\d{1,14}|\(\d{3}\)\s?\d{3}-?\d{4}|\d{3}-?\d{3}-?\d{4})',
        # API keys and tokens
        r'(?i)(api[_-]?key|token|secret|password)["\s]*[:=]["\s]*[a-zA-Z0-9_-]{8,}',
    ]
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record with security sanitization."""
        
        # Sanitize the message
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            record.msg = self._sanitize_message(record.msg)
        
        # Sanitize args if present
        if hasattr(record, 'args') and record.args:
            sanitized_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    sanitized_args.append(self._sanitize_message(arg))
                else:
                    sanitized_args.append(arg)
            record.args = tuple(sanitized_args)
        
        return super().format(record)
    
    def _sanitize_message(self, message: str) -> str:
        """Sanitize sensitive information from log message."""
        import re
        
        sanitized = message
        
        # Redact sensitive patterns
        for pattern in self.SENSITIVE_PATTERNS:
            sanitized = re.sub(pattern, '[REDACTED]', sanitized)
        
        # Redact common sensitive field names
        sensitive_fields = ['password', 'token', 'api_key', 'secret', 'credit_card']
        for field in sensitive_fields:
            # Match field: value patterns
            pattern = rf'{field}["\s]*[:=]["\s]*[^,\s}}\]]+(?=[,\s}}\]]|$)'
            sanitized = re.sub(pattern, f'{field}: [REDACTED]', sanitized, flags=re.IGNORECASE)
        
        return sanitized


class StructuredFormatter(jsonlogger.JsonFormatter):
    """
    Structured JSON formatter for machine-readable logs.
    
    Includes security context, performance metrics, and
    hospitality industry specific fields.
    """
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add service context
        log_record['service'] = 'security-triage-agent'
        log_record['component'] = getattr(record, 'component', 'unknown')
        
        # Add security context
        log_record['incident_id'] = getattr(record, 'incident_id', None)
        log_record['session_id'] = getattr(record, 'session_id', None)
        log_record['user_id'] = getattr(record, 'user_id', None)
        
        # Add performance context
        log_record['execution_time_ms'] = getattr(record, 'execution_time_ms', None)
        log_record['memory_usage_mb'] = getattr(record, 'memory_usage_mb', None)
        
        # Add hospitality context
        log_record['property_code'] = getattr(record, 'property_code', None)
        log_record['guest_impact'] = getattr(record, 'guest_impact', None)
        
        # Add workflow context
        log_record['workflow_step'] = getattr(record, 'workflow_step', None)
        log_record['tool_name'] = getattr(record, 'tool_name', None)


def setup_logger(
    name: str,
    level: str = "INFO",
    log_directory: str = "logs",
    enable_console: bool = True,
    enable_file: bool = True,
    enable_json: bool = True,
    max_file_size_mb: int = 10,
    backup_count: int = 5
) -> logging.Logger:
    """
    Set up comprehensive logging for the Security Triage Agent.
    
    Args:
        name: Logger name
        level: Logging level
        log_directory: Directory for log files
        enable_console: Enable console logging
        enable_file: Enable file logging
        enable_json: Enable JSON structured logging
        max_file_size_mb: Maximum log file size in MB
        backup_count: Number of backup files to keep
        
    Returns:
        Configured logger instance
    """
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create log directory
    log_path = Path(log_directory)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # Console handler with security-aware formatting
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = SecurityAwareFormatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # File handler with rotation
    if enable_file:
        file_handler = logging.handlers.RotatingFileHandler(
            filename=log_path / f"{name}.log",
            maxBytes=max_file_size_mb * 1024 * 1024,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_formatter = SecurityAwareFormatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(component)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # JSON structured logging for machine processing
    if enable_json:
        json_handler = logging.handlers.RotatingFileHandler(
            filename=log_path / f"{name}_structured.jsonl",
            maxBytes=max_file_size_mb * 1024 * 1024,
            backupCount=backup_count,
            encoding='utf-8'
        )
        json_formatter = StructuredFormatter()
        json_handler.setFormatter(json_formatter)
        logger.addHandler(json_handler)
    
    # Audit trail handler for security events
    audit_handler = logging.handlers.RotatingFileHandler(
        filename=log_path / f"{name}_audit.log",
        maxBytes=max_file_size_mb * 1024 * 1024,
        backupCount=backup_count * 2,  # Keep more audit logs
        encoding='utf-8'
    )
    audit_formatter = StructuredFormatter()
    audit_handler.setFormatter(audit_formatter)
    audit_handler.setLevel(logging.WARNING)  # Only warnings and above for audit
    logger.addHandler(audit_handler)
    
    return logger


class SecurityLoggerAdapter(logging.LoggerAdapter):
    """
    Logger adapter that automatically includes security context.
    
    Provides convenience methods for security-specific logging
    with proper context and formatting.
    """
    
    def __init__(self, logger: logging.Logger, extra: Optional[Dict[str, Any]] = None):
        super().__init__(logger, extra or {})
    
    def incident_log(
        self,
        level: int,
        message: str,
        incident_id: str,
        component: str = "incident_processing",
        **kwargs
    ) -> None:
        """Log incident-related message with context."""
        extra = {
            'incident_id': incident_id,
            'component': component,
            **kwargs
        }
        self.log(level, message, extra=extra)
    
    def security_event(
        self,
        message: str,
        event_type: str,
        severity: str = "medium",
        incident_id: Optional[str] = None,
        **kwargs
    ) -> None:
        """Log security event for audit trail."""
        extra = {
            'event_type': event_type,
            'security_severity': severity,
            'component': 'security_monitor',
            'incident_id': incident_id,
            **kwargs
        }
        self.warning(f"SECURITY_EVENT: {message}", extra=extra)
    
    def performance_log(
        self,
        message: str,
        execution_time_ms: float,
        component: str,
        tool_name: Optional[str] = None,
        incident_id: Optional[str] = None,
        **kwargs
    ) -> None:
        """Log performance metrics."""
        extra = {
            'execution_time_ms': execution_time_ms,
            'component': component,
            'tool_name': tool_name,
            'incident_id': incident_id,
            **kwargs
        }
        self.info(f"PERFORMANCE: {message}", extra=extra)
    
    def compliance_log(
        self,
        message: str,
        framework: str,
        compliance_status: str,
        incident_id: Optional[str] = None,
        **kwargs
    ) -> None:
        """Log compliance-related events."""
        extra = {
            'compliance_framework': framework,
            'compliance_status': compliance_status,
            'component': 'compliance_checker',
            'incident_id': incident_id,
            **kwargs
        }
        level = logging.WARNING if compliance_status == 'violation' else logging.INFO
        self.log(level, f"COMPLIANCE: {message}", extra=extra)
    
    def guest_impact_log(
        self,
        message: str,
        impact_level: str,
        guest_count: int = 0,
        incident_id: Optional[str] = None,
        **kwargs
    ) -> None:
        """Log guest impact events."""
        extra = {
            'guest_impact': impact_level,
            'affected_guest_count': guest_count,
            'component': 'guest_impact_monitor',
            'incident_id': incident_id,
            **kwargs
        }
        level = logging.WARNING if impact_level in ['high', 'critical'] else logging.INFO
        self.log(level, f"GUEST_IMPACT: {message}", extra=extra)
    
    def workflow_log(
        self,
        message: str,
        workflow_step: str,
        step_status: str,
        incident_id: Optional[str] = None,
        **kwargs
    ) -> None:
        """Log workflow step execution."""
        extra = {
            'workflow_step': workflow_step,
            'step_status': step_status,
            'component': 'workflow_engine',
            'incident_id': incident_id,
            **kwargs
        }
        level = logging.ERROR if step_status == 'failed' else logging.INFO
        self.log(level, f"WORKFLOW: {message}", extra=extra)


def get_security_logger(name: str, **context) -> SecurityLoggerAdapter:
    """
    Get a security-aware logger adapter with context.
    
    Args:
        name: Logger name
        **context: Additional context to include in all log messages
        
    Returns:
        Security logger adapter
    """
    base_logger = logging.getLogger(name)
    return SecurityLoggerAdapter(base_logger, context)


# Configure structlog for better structured logging
def configure_structlog() -> None:
    """Configure structlog for enhanced structured logging."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.WriteLoggerFactory(),
        cache_logger_on_first_use=False,
    )