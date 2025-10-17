"""Client onboarding API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
import secrets
import string
from pathlib import Path
import aiofiles

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_admin
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.client import Client
from app.models.kyc_document import KYCDocument
from app.models.payment import Payment
from app.schemas.onboarding import (
    ClientRegistrationRequest,
    ClientRegistrationResponse,
    PendingRegistrationOut,
    VerifyRegistrationRequest,
    VerifyRegistrationResponse,
    KYCDocumentUploadResponse,
    KYCDocumentOut,
    VerifyKYCDocumentRequest,
    PaymentUploadRequest,
    PaymentUploadResponse,
    PaymentOut,
    VerifyPaymentRequest,
    ActivateClientRequest,
    ClientOnboardingStatusResponse,
    ClientDetailOut,
)
from app.services.email import email_service

router = APIRouter()

# File upload configuration
UPLOAD_BASE_DIR = Path("uploads")
KYC_UPLOAD_DIR = UPLOAD_BASE_DIR / "kyc"
PAYMENT_UPLOAD_DIR = UPLOAD_BASE_DIR / "payments"
KYC_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
PAYMENT_UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_KYC_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/jpg",
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


# ==================== STEP 1: PUBLIC REGISTRATION ====================

@router.post("/register", response_model=ClientRegistrationResponse, status_code=status.HTTP_201_CREATED)
async def register_client(
    registration: ClientRegistrationRequest,
    db: AsyncSession = Depends(get_db)
):
    """Step 1: Public client registration"""
    
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == registration.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user account
    new_user = User(
        email=registration.email,
        hashed_password=get_password_hash(registration.password),
        full_name=registration.full_name,
        role=UserRole.CLIENT,
        is_active=False,  # Inactive until admin approves
        is_verified=False
    )
    db.add(new_user)
    await db.flush()  # Get user ID
    
    # Create client record
    new_client = Client(
        user_id=new_user.id,
        business_name=registration.business_name,
        business_address=registration.business_address,
        business_type=registration.business_type,
        registration_number=registration.registration_number,
        phone=registration.phone,
        alternate_phone=registration.alternate_phone,
        services_requested=registration.services_requested,
        terms_accepted=registration.terms_accepted,
        privacy_policy_accepted=registration.privacy_policy_accepted,
        onboarding_status="pending_verification"
    )
    db.add(new_client)
    await db.commit()
    await db.refresh(new_client)
    
    # Send confirmation email
    await email_service.send_registration_confirmation(
        registration.email,
        registration.business_name
    )
    
    # Alert admin
    await email_service.send_admin_new_registration_alert(
        "admin@eranoconsulting.com",
        registration.business_name,
        registration.email
    )
    
    return ClientRegistrationResponse(
        message="Registration successful. Awaiting admin verification.",
        user_id=new_user.id,
        client_id=new_client.id,
        email=new_user.email,
        business_name=new_client.business_name,
        onboarding_status=new_client.onboarding_status
    )


# ==================== STEP 2: ADMIN VERIFICATION ====================

@router.get("/admin/pending-registrations", response_model=List[PendingRegistrationOut])
async def get_pending_registrations(
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin)
):
    """Get all pending client registrations for admin review"""
    
    result = await db.execute(
        select(Client, User)
        .join(User, Client.user_id == User.id)
        .where(Client.onboarding_status == "pending_verification")
        .order_by(Client.registration_date.desc())
    )
    
    registrations = []
    for client, user in result.all():
        registrations.append(PendingRegistrationOut(
            id=client.id,
            user_id=user.id,
            email=user.email,
            full_name=user.full_name,
            business_name=client.business_name,
            phone=client.phone,
            services_requested=client.services_requested or [],
            registration_date=client.registration_date,
            onboarding_status=client.onboarding_status
        ))
    
    return registrations


@router.post("/admin/verify-registration/{client_id}", response_model=VerifyRegistrationResponse)
async def verify_registration(
    client_id: int,
    verification: VerifyRegistrationRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin)
):
    """Step 2: Admin verifies client registration"""
    
    # Get client and user
    result = await db.execute(
        select(Client, User)
        .join(User, Client.user_id == User.id)
        .where(Client.id == client_id)
    )
    client_user = result.first()
    
    if not client_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    client, user = client_user
    
    if verification.approved:
        # Generate temporary password
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        
        # Update user
        user.hashed_password = get_password_hash(temp_password)
        user.is_active = True
        
        # Update client
        client.onboarding_status = "pre_active"
        client.verification_date = func.now()
        client.admin_notes = verification.admin_notes
        client.temp_password_sent = True
        client.temp_password_sent_at = func.now()
        
        await db.commit()
        
        # Send temporary credentials
        await email_service.send_temporary_credentials(
            user.email,
            temp_password,
            client.business_name
        )
        
        return VerifyRegistrationResponse(
            message="Registration approved. Temporary credentials sent.",
            client_id=client.id,
            approved=True,
            new_status="pre_active",
            temp_password=temp_password  # For admin reference only
        )
    
    else:
        # Rejection
        client.onboarding_status = "rejected"
        client.rejection_reason = verification.rejection_reason
        client.admin_notes = verification.admin_notes
        user.is_active = False
        
        await db.commit()
        
        # Send rejection email
        await email_service.send_rejection_notification(
            user.email,
            client.business_name,
            verification.rejection_reason or "Registration does not meet requirements"
        )
        
        return VerifyRegistrationResponse(
            message="Registration rejected.",
            client_id=client.id,
            approved=False,
            new_status="rejected",
            temp_password=None
        )


# Continue to next artifact for remaining endpoints...
