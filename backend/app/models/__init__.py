"""Models package - Import all models for Alembic auto-detection"""

# ✅ CRITICAL: Import base and enums FIRST
from app.models.base import BaseModel

# Import enums
from app.models.enums import (
    OnboardingStatus,
    DocumentType,
    VerificationStatus,
    ServiceType,
)

# ✅ CRITICAL: Import User BEFORE Client (Client depends on User)
from app.models.user import User, UserRole

# Import other models that depend on User
from app.models.refresh_token import RefreshToken
from app.models.message import Message
from app.models.uploaded_file import UploadedFile

# ✅ Import Client AFTER User
from app.models.client import Client

# Import models that depend on Client
from app.models.kyc_document import KYCDocument
from app.models.payment import Payment
from app.models.engagement_letter import EngagementLetter

# Export all models for easy imports
__all__ = [
    "BaseModel",
    "User",
    "UserRole",
    "RefreshToken",
    "Message",
    "UploadedFile",
    "Client",
    "KYCDocument",
    "Payment",
    "EngagementLetter",
    "OnboardingStatus",
    "DocumentType",
    "VerificationStatus",
    "ServiceType",
]
