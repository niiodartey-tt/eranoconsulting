# backend/app/api/v1/client_onboarding.py
# CREATE THIS FILE

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.client import Client
from sqlalchemy import select

router = APIRouter()


class OnboardingStatusResponse(BaseModel):
    """Response for onboarding status check"""
    status: str
    kyc_uploaded: bool
    payment_verified: bool
    onboarding_completed: bool
    engagement_letter_signed: bool
    next_step: str
    message: str


@router.get("/status", response_model=OnboardingStatusResponse)
async def get_onboarding_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current onboarding status for the logged-in client"""
    
    # Get or create client record
    query = select(Client).where(Client.user_id == current_user.id)
    result = await db.execute(query)
    client = result.scalar_one_or_none()
    
    if not client:
        # Create client record if it doesn't exist
        client = Client(
            user_id=current_user.id,
            status="pre_active",
            kyc_uploaded=False,
            payment_verified=False,
            onboarding_completed=False,
            engagement_letter_signed=False
        )
        db.add(client)
        await db.commit()
        await db.refresh(client)
    
    # Determine next step and message based on status
    next_step = ""
    message = ""
    
    if client.status == "pre_active":
        next_step = "upload_documents"
        message = "Welcome! Please complete your onboarding and upload required documents."
    elif client.status == "pending_review":
        next_step = "wait_for_review"
        message = "Your documents are under review. We'll notify you once verified."
    elif client.status == "inactive":
        next_step = "sign_engagement_letter"
        message = "Your documents are verified. Please sign the engagement letter to activate your account."
    elif client.status == "active":
        next_step = "complete"
        message = "Your account is fully active!"
    elif client.status == "rejected":
        next_step = "resubmit_documents"
        message = "Your submission was rejected. Please review feedback and resubmit."
    else:
        next_step = "upload_documents"
        message = "Please complete your onboarding."
    
    return OnboardingStatusResponse(
        status=client.status,
        kyc_uploaded=client.kyc_uploaded if hasattr(client, 'kyc_uploaded') else False,
        payment_verified=client.payment_verified if hasattr(client, 'payment_verified') else False,
        onboarding_completed=client.onboarding_completed if hasattr(client, 'onboarding_completed') else False,
        engagement_letter_signed=client.engagement_letter_signed if hasattr(client, 'engagement_letter_signed') else False,
        next_step=next_step,
        message=message
    )


@router.post("/submit-for-review")
async def submit_for_review(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit documents for admin review"""
    
    query = select(Client).where(Client.user_id == current_user.id)
    result = await db.execute(query)
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client profile not found"
        )
    
    # Check if documents are uploaded
    if not client.kyc_uploaded:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload all required documents before submitting for review"
        )
    
    # Update status to pending review
    client.status = "pending_review"
    client.onboarding_completed = True
    await db.commit()
    await db.refresh(client)
    
    return {
        "message": "Documents submitted successfully! Your submission is now under review.",
        "status": client.status,
        "redirect_to": "/client/dashboard/inactive"
    }


@router.put("/mark-kyc-uploaded")
async def mark_kyc_uploaded(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark that KYC documents have been uploaded"""
    
    query = select(Client).where(Client.user_id == current_user.id)
    result = await db.execute(query)
    client = result.scalar_one_or_none()
    
    if not client:
        # Create client if doesn't exist
        client = Client(
            user_id=current_user.id,
            status="pre_active",
            kyc_uploaded=True
        )
        db.add(client)
    else:
        client.kyc_uploaded = True
    
    await db.commit()
    
    return {"message": "KYC upload status updated", "kyc_uploaded": True}
