"""Pydantic schemas for onboarding workflow"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import List, Optional
from datetime import datetime
from decimal import Decimal


# ==================== CLIENT REGISTRATION ====================

class ClientRegistrationRequest(BaseModel):
    """Step 1: Public client registration"""
    # User account fields
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=2, max_length=255)
    
    # Business fields
    business_name: str = Field(..., min_length=2, max_length=255)
    business_address: Optional[str] = None
    business_type: Optional[str] = None
    registration_number: Optional[str] = None
    
    # Contact fields
    phone: str = Field(..., min_length=10, max_length=20)
    alternate_phone: Optional[str] = None
    
    # Services
    services_requested: List[str] = Field(default_factory=list)
    
    # Terms
    terms_accepted: bool = Field(..., description="Must accept terms")
    privacy_policy_accepted: bool = Field(..., description="Must accept privacy policy")
    
    @field_validator('terms_accepted', 'privacy_policy_accepted')
    @classmethod
    def validate_acceptance(cls, v):
        if not v:
            raise ValueError('Must accept terms and privacy policy')
        return v


class ClientRegistrationResponse(BaseModel):
    """Response after successful registration"""
    message: str
    user_id: int
    client_id: int
    email: str
    business_name: str
    onboarding_status: str
    
    class Config:
        from_attributes = True


# ==================== ADMIN VERIFICATION ====================

class PendingRegistrationOut(BaseModel):
    """Pending registration details for admin review"""
    id: int
    user_id: int
    email: str
    full_name: str
    business_name: str
    phone: str
    services_requested: List[str]
    registration_date: datetime
    onboarding_status: str
    
    class Config:
        from_attributes = True


class VerifyRegistrationRequest(BaseModel):
    """Admin verification decision"""
    approved: bool
    admin_notes: Optional[str] = None
    rejection_reason: Optional[str] = None


class VerifyRegistrationResponse(BaseModel):
    """Response after admin verification"""
    message: str
    client_id: int
    approved: bool
    new_status: str
    temp_password: Optional[str] = None  # Only if approved


# ==================== KYC DOCUMENTS ====================

class KYCDocumentUploadResponse(BaseModel):
    """Response after KYC document upload"""
    id: int
    client_id: int
    document_type: str
    document_name: str
    file_size: int
    uploaded_at: datetime
    verification_status: str
    
    class Config:
        from_attributes = True


class KYCDocumentOut(BaseModel):
    """KYC document details"""
    id: int
    document_type: str
    document_name: str
    file_size: int
    uploaded_at: datetime
    verification_status: str
    admin_comments: Optional[str] = None
    rejection_reason: Optional[str] = None
    verified_by_id: Optional[int] = None
    verification_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class VerifyKYCDocumentRequest(BaseModel):
    """Admin KYC document verification"""
    approved: bool
    admin_comments: Optional[str] = None
    rejection_reason: Optional[str] = None


# ==================== PAYMENTS ====================

class PaymentUploadRequest(BaseModel):
    """Payment details submission"""
    amount: Decimal = Field(..., gt=0)
    payment_reference: Optional[str] = None
    payment_method: str = "bank_transfer"
    payment_date: Optional[datetime] = None
    description: Optional[str] = None


class PaymentUploadResponse(BaseModel):
    """Response after payment receipt upload"""
    id: int
    client_id: int
    amount: Decimal
    currency: str
    payment_method: str
    uploaded_at: datetime
    verification_status: str
    
    class Config:
        from_attributes = True


class PaymentOut(BaseModel):
    """Payment details"""
    id: int
    amount: Decimal
    currency: str
    payment_reference: Optional[str] = None
    payment_method: str
    payment_date: Optional[datetime] = None
    verification_status: str
    admin_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    verified_by_id: Optional[int] = None
    verification_date: Optional[datetime] = None
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class VerifyPaymentRequest(BaseModel):
    """Admin payment verification"""
    approved: bool
    admin_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    bank_statement_reference: Optional[str] = None


# ==================== CLIENT ACTIVATION ====================

class ActivateClientRequest(BaseModel):
    """Activate client and assign account manager"""
    account_manager_id: int
    admin_notes: Optional[str] = None


class ClientOnboardingStatusResponse(BaseModel):
    """Complete onboarding status"""
    client_id: int
    business_name: str
    onboarding_status: str
    registration_date: datetime
    verification_date: Optional[datetime] = None
    activation_date: Optional[datetime] = None
    account_manager_id: Optional[int] = None
    
    # Progress indicators
    kyc_documents_count: int
    kyc_approved_count: int
    payment_verified: bool
    
    class Config:
        from_attributes = True


# ==================== ENHANCED CLIENT OUT ====================

class ClientDetailOut(BaseModel):
    """Detailed client information"""
    id: int
    user_id: int
    business_name: str
    business_address: Optional[str] = None
    phone: str
    services_requested: List[str]
    onboarding_status: str
    account_manager_id: Optional[int] = None
    registration_date: datetime
    verification_date: Optional[datetime] = None
    activation_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True
