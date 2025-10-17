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


@router.post(
    "/register",
    response_model=ClientRegistrationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_client(
    registration: ClientRegistrationRequest, db: AsyncSession = Depends(get_db)
):
    """Step 1: Public client registration"""

    # Check if email already exists
    result = await db.execute(select(User).where(User.email == registration.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # Create user account
    new_user = User(
        email=registration.email,
        hashed_password=get_password_hash(registration.password),
        full_name=registration.full_name,
        role=UserRole.CLIENT,
        is_active=False,  # Inactive until admin approves
        is_verified=False,
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
        onboarding_status="pending_verification",
    )
    db.add(new_client)
    await db.commit()
    await db.refresh(new_client)

    # Send confirmation email
    await email_service.send_registration_confirmation(
        registration.email, registration.business_name
    )

    # Alert admin
    await email_service.send_admin_new_registration_alert(
        "admin@eranoconsulting.com", registration.business_name, registration.email
    )

    return ClientRegistrationResponse(
        message="Registration successful. Awaiting admin verification.",
        user_id=new_user.id,
        client_id=new_client.id,
        email=new_user.email,
        business_name=new_client.business_name,
        onboarding_status=new_client.onboarding_status,
    )


# ==================== STEP 2: ADMIN VERIFICATION ====================


@router.get("/admin/pending-registrations", response_model=List[PendingRegistrationOut])
async def get_pending_registrations(
    db: AsyncSession = Depends(get_db), _admin: User = Depends(get_current_admin)
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
        registrations.append(
            PendingRegistrationOut(
                id=client.id,
                user_id=user.id,
                email=user.email,
                full_name=user.full_name,
                business_name=client.business_name,
                phone=client.phone,
                services_requested=client.services_requested or [],
                registration_date=client.registration_date,
                onboarding_status=client.onboarding_status,
            )
        )

    return registrations


@router.post(
    "/admin/verify-registration/{client_id}", response_model=VerifyRegistrationResponse
)
async def verify_registration(
    client_id: int,
    verification: VerifyRegistrationRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
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
            status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
        )

    client, user = client_user

    if verification.approved:
        # Generate temporary password
        temp_password = "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(12)
        )

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
            user.email, temp_password, client.business_name
        )

        return VerifyRegistrationResponse(
            message="Registration approved. Temporary credentials sent.",
            client_id=client.id,
            approved=True,
            new_status="pre_active",
            temp_password=temp_password,  # For admin reference only
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
            verification.rejection_reason or "Registration does not meet requirements",
        )

        return VerifyRegistrationResponse(
            message="Registration rejected.",
            client_id=client.id,
            approved=False,
            new_status="rejected",
            temp_password=None,
        )


# ==================== STEP 4: KYC DOCUMENT UPLOAD ====================


@router.post("/kyc/upload", response_model=KYCDocumentUploadResponse)
async def upload_kyc_document(
    document_type: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Step 4: Client uploads KYC documents"""

    # Get client record
    result = await db.execute(select(Client).where(Client.user_id == current_user.id))
    client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client record not found"
        )

    # Validate file type
    if file.content_type not in ALLOWED_KYC_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not allowed. Only PDF and images accepted.",
        )

    # Read and validate file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Maximum size is 10MB.",
        )

    # Generate unique filename
    file_extension = Path(file.filename).suffix
    unique_filename = (
        f"{client.id}_{document_type}_{secrets.token_hex(8)}{file_extension}"
    )
    file_path = KYC_UPLOAD_DIR / unique_filename

    # Save file
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(contents)

    # Create database record
    kyc_doc = KYCDocument(
        client_id=client.id,
        document_type=document_type,
        document_name=file.filename,
        file_path=str(file_path),
        file_size=len(contents),
        mime_type=file.content_type,
        verification_status="pending",
    )
    db.add(kyc_doc)

    # Update client status if first KYC upload
    if client.onboarding_status == "pre_active":
        client.onboarding_status = "kyc_submission"

    await db.commit()
    await db.refresh(kyc_doc)

    return KYCDocumentUploadResponse(
        id=kyc_doc.id,
        client_id=kyc_doc.client_id,
        document_type=kyc_doc.document_type,
        document_name=kyc_doc.document_name,
        file_size=kyc_doc.file_size,
        uploaded_at=kyc_doc.uploaded_at,
        verification_status=kyc_doc.verification_status,
    )


@router.get("/kyc/documents", response_model=List[KYCDocumentOut])
async def get_my_kyc_documents(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get current user's KYC documents"""

    result = await db.execute(select(Client).where(Client.user_id == current_user.id))
    client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client record not found"
        )

    result = await db.execute(
        select(KYCDocument)
        .where(KYCDocument.client_id == client.id)
        .order_by(KYCDocument.uploaded_at.desc())
    )
    documents = result.scalars().all()

    return [KYCDocumentOut.model_validate(doc) for doc in documents]


# ==================== STEP 5: ADMIN KYC REVIEW ====================


@router.get("/admin/kyc-review", response_model=List[dict])
async def get_kyc_review_queue(
    db: AsyncSession = Depends(get_db), _admin: User = Depends(get_current_admin)
):
    """Get all KYC documents pending review"""

    result = await db.execute(
        select(KYCDocument, Client, User)
        .join(Client, KYCDocument.client_id == Client.id)
        .join(User, Client.user_id == User.id)
        .where(KYCDocument.verification_status == "pending")
        .order_by(KYCDocument.uploaded_at.asc())
    )

    queue = []
    for kyc_doc, client, user in result.all():
        queue.append(
            {
                "document_id": kyc_doc.id,
                "client_id": client.id,
                "business_name": client.business_name,
                "client_email": user.email,
                "document_type": kyc_doc.document_type,
                "document_name": kyc_doc.document_name,
                "file_path": kyc_doc.file_path,
                "uploaded_at": kyc_doc.uploaded_at,
                "verification_status": kyc_doc.verification_status,
            }
        )

    return queue


@router.post("/admin/kyc/verify/{document_id}")
async def verify_kyc_document(
    document_id: int,
    verification: VerifyKYCDocumentRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Step 5: Admin verifies KYC document"""

    # Get document
    result = await db.execute(
        select(KYCDocument, Client, User)
        .join(Client, KYCDocument.client_id == Client.id)
        .join(User, Client.user_id == User.id)
        .where(KYCDocument.id == document_id)
    )
    doc_data = result.first()

    if not doc_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
        )

    kyc_doc, client, user = doc_data

    # Update document
    kyc_doc.verification_status = "approved" if verification.approved else "rejected"
    kyc_doc.verified_by_id = admin.id
    kyc_doc.verification_date = func.now()
    kyc_doc.admin_comments = verification.admin_comments
    kyc_doc.rejection_reason = verification.rejection_reason

    # Check if all KYC documents are approved
    if verification.approved:
        result = await db.execute(
            select(func.count(KYCDocument.id))
            .where(KYCDocument.client_id == client.id)
            .where(KYCDocument.verification_status != "approved")
        )
        pending_count = result.scalar()

        # If all documents approved, move to payment review
        if pending_count == 0:
            client.onboarding_status = "kyc_review"

    await db.commit()

    # Send notification
    await email_service.send_kyc_status_notification(
        user.email,
        kyc_doc.document_type,
        verification.approved,
        verification.admin_comments,
    )

    return {
        "message": f"Document {'approved' if verification.approved else 'rejected'}",
        "document_id": document_id,
        "new_status": kyc_doc.verification_status,
    }


# ==================== STEP 4/5: PAYMENT UPLOAD ====================


@router.post("/payment/upload", response_model=PaymentUploadResponse)
async def upload_payment_receipt(
    payment_data: PaymentUploadRequest,
    receipt_file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Step 4: Client uploads payment receipt"""

    # Get client
    result = await db.execute(select(Client).where(Client.user_id == current_user.id))
    client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client record not found"
        )

    # Validate file
    if receipt_file.content_type not in ALLOWED_KYC_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file type. Only PDF and images accepted.",
        )

    contents = await receipt_file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File too large. Maximum 10MB.",
        )

    # Save file
    file_extension = Path(receipt_file.filename).suffix
    unique_filename = f"{client.id}_payment_{secrets.token_hex(8)}{file_extension}"
    file_path = PAYMENT_UPLOAD_DIR / unique_filename

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(contents)

    # Create payment record
    payment = Payment(
        client_id=client.id,
        amount=payment_data.amount,
        payment_reference=payment_data.payment_reference,
        payment_method=payment_data.payment_method,
        payment_date=payment_data.payment_date,
        description=payment_data.description,
        receipt_file_path=str(file_path),
        receipt_filename=receipt_file.filename,
        receipt_file_size=len(contents),
        receipt_mime_type=receipt_file.content_type,
        verification_status="pending",
    )
    db.add(payment)

    # Update client status
    client.onboarding_status = "payment_review"

    await db.commit()
    await db.refresh(payment)

    return PaymentUploadResponse(
        id=payment.id,
        client_id=payment.client_id,
        amount=payment.amount,
        currency=payment.currency,
        payment_method=payment.payment_method,
        uploaded_at=payment.uploaded_at,
        verification_status=payment.verification_status,
    )


@router.get("/payment/records", response_model=List[PaymentOut])
async def get_my_payments(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get current user's payment records"""

    result = await db.execute(select(Client).where(Client.user_id == current_user.id))
    client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client record not found"
        )

    result = await db.execute(
        select(Payment)
        .where(Payment.client_id == client.id)
        .order_by(Payment.uploaded_at.desc())
    )
    payments = result.scalars().all()

    return [PaymentOut.model_validate(p) for p in payments]


# ==================== ADMIN PAYMENT REVIEW ====================


@router.get("/admin/payment-review", response_model=List[dict])
async def get_payment_review_queue(
    db: AsyncSession = Depends(get_db), _admin: User = Depends(get_current_admin)
):
    """Get all payments pending review"""

    result = await db.execute(
        select(Payment, Client, User)
        .join(Client, Payment.client_id == Client.id)
        .join(User, Client.user_id == User.id)
        .where(Payment.verification_status == "pending")
        .order_by(Payment.uploaded_at.asc())
    )

    queue = []
    for payment, client, user in result.all():
        queue.append(
            {
                "payment_id": payment.id,
                "client_id": client.id,
                "business_name": client.business_name,
                "client_email": user.email,
                "amount": float(payment.amount),
                "currency": payment.currency,
                "payment_method": payment.payment_method,
                "payment_reference": payment.payment_reference,
                "receipt_file_path": payment.receipt_file_path,
                "uploaded_at": payment.uploaded_at,
                "verification_status": payment.verification_status,
            }
        )

    return queue


@router.post("/admin/payment/verify/{payment_id}")
async def verify_payment(
    payment_id: int,
    verification: VerifyPaymentRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Step 5: Admin verifies payment"""

    # Get payment
    result = await db.execute(
        select(Payment, Client, User)
        .join(Client, Payment.client_id == Client.id)
        .join(User, Client.user_id == User.id)
        .where(Payment.id == payment_id)
    )
    payment_data = result.first()

    if not payment_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found"
        )

    payment, client, user = payment_data

    # Update payment
    payment.verification_status = "approved" if verification.approved else "rejected"
    payment.verified_by_id = admin.id
    payment.verification_date = func.now()
    payment.admin_notes = verification.admin_notes
    payment.rejection_reason = verification.rejection_reason

    if verification.bank_statement_reference:
        payment.bank_statement_matched = True
        payment.bank_statement_reference = verification.bank_statement_reference

    # If approved, move to next stage
    if verification.approved:
        client.onboarding_status = "awaiting_signature"

    await db.commit()

    # Send notification
    await email_service.send_payment_verification_notification(
        user.email,
        float(payment.amount),
        verification.approved,
        verification.admin_notes,
    )

    return {
        "message": f"Payment {'approved' if verification.approved else 'rejected'}",
        "payment_id": payment_id,
        "new_status": payment.verification_status,
        "client_status": client.onboarding_status,
    }


# ==================== STEP 7: CLIENT ACTIVATION ====================


@router.post("/admin/activate-client/{client_id}")
async def activate_client(
    client_id: int,
    activation_data: ActivateClientRequest,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Step 7: Admin activates client portal"""

    # Get client and user
    result = await db.execute(
        select(Client, User)
        .join(User, Client.user_id == User.id)
        .where(Client.id == client_id)
    )
    client_user = result.first()

    if not client_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
        )

    client, user = client_user

    # Verify account manager exists and is staff
    result = await db.execute(
        select(User).where(User.id == activation_data.account_manager_id)
    )
    account_manager = result.scalar_one_or_none()

    if not account_manager or account_manager.role not in [
        UserRole.ADMIN,
        UserRole.STAFF,
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid account manager"
        )

    # Activate client
    client.onboarding_status = "active"
    client.activation_date = func.now()
    client.account_manager_id = activation_data.account_manager_id
    client.admin_notes = activation_data.admin_notes

    await db.commit()

    # Send activation email
    await email_service.send_activation_notification(
        user.email,
        client.business_name,
        account_manager.full_name or account_manager.email,
    )

    return {
        "message": "Client activated successfully",
        "client_id": client_id,
        "status": "active",
        "account_manager": account_manager.full_name,
        "activation_date": client.activation_date,
    }


# ==================== CLIENT ONBOARDING STATUS ====================


@router.get("/onboarding-status", response_model=ClientOnboardingStatusResponse)
async def get_onboarding_status(
    current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    """Get current user's onboarding status"""

    result = await db.execute(select(Client).where(Client.user_id == current_user.id))
    client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client record not found"
        )

    # Count KYC documents
    result = await db.execute(
        select(func.count(KYCDocument.id)).where(KYCDocument.client_id == client.id)
    )
    kyc_total = result.scalar()

    result = await db.execute(
        select(func.count(KYCDocument.id))
        .where(KYCDocument.client_id == client.id)
        .where(KYCDocument.verification_status == "approved")
    )
    kyc_approved = result.scalar()

    # Check payment status
    result = await db.execute(
        select(func.count(Payment.id))
        .where(Payment.client_id == client.id)
        .where(Payment.verification_status == "approved")
    )
    payment_verified = result.scalar() > 0

    return ClientOnboardingStatusResponse(
        client_id=client.id,
        business_name=client.business_name,
        onboarding_status=client.onboarding_status,
        registration_date=client.registration_date,
        verification_date=client.verification_date,
        activation_date=client.activation_date,
        account_manager_id=client.account_manager_id,
        kyc_documents_count=kyc_total,
        kyc_approved_count=kyc_approved,
        payment_verified=payment_verified,
    )


@router.get("/admin/client/{client_id}", response_model=ClientDetailOut)
async def get_client_details(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: User = Depends(get_current_admin),
):
    """Admin: Get detailed client information"""

    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
        )

    return ClientDetailOut.model_validate(client)
