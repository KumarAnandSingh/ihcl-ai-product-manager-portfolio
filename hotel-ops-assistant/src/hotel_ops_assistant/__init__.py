"""
Hotel Operations Assistant.
AI-powered hotel operations management system with comprehensive guest services,
compliance monitoring, and fraud detection capabilities.
"""

__version__ = "1.0.0"
__author__ = "IHCL AI Portfolio"
__description__ = "Comprehensive Hotel Operations Assistant with AI-powered incident management and guest services"

from .api.main import create_app
from .core.config import get_settings

__all__ = ["create_app", "get_settings"]