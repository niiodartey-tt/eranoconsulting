"""Client onboarding endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.client import Client, ClientStatus
from app.repositories.base import BaseRepository

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


class SubmitForReviewRequest(BaseModel):
    """Request to submit documents for review"""

    confirm_submission: bool = True


@router.get("/status", response_model=OnboardingStatusResponse)
async def get_onboarding_status(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Get current onboarding status for the logged-in client"""

    # Get client record
    client_repo = BaseRepository(Client, db)
    client = await client_repo.get_by_field("user_id", current_user.id)

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client profile not found"
        )

    # Determine next step and message
    next_step = ""
    message = ""

    if client.status == ClientStatus.PRE_ACTIVE:
        next_step = "upload_documents"
        message = "Please complete your onboarding form and upload required documents"
    elif client.status == ClientStatus.PENDING_REVIEW:
        next_step = "wait_for_review"
        message = "Your documents are under review. We'll notify you once verified."
    elif client.status == ClientStatus.INACTIVE:
        next_step = "sign_engagement_letter"
        message = "Your documents are verified. Please sign the engagement letter to activate your account."
    elif client.status == ClientStatus.ACTIVE:
        next_step = "complete"
        message = "Your account is fully active!"
    elif client.status == ClientStatus.REJECTED:
        next_step = "resubmit_documents"
        message = "Your submission was rejected. Please review feedback and resubmit."

    return OnboardingStatusResponse(
        status=client.status.value,
        kyc_uploaded=client.kyc_uploaded,
        payment_verified=client.payment_verified,
        onboarding_completed=client.onboarding_completed,
        engagement_letter_signed=client.engagement_letter_signed,
        next_step=next_step,
        message=message,
    )


@router.post("/submit-for-review")
async def submit_for_review(
    request: SubmitForReviewRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit documents for admin review"""

    client_repo = BaseRepository(Client, db)
    client = await client_repo.get_by_field("user_id", current_user.id)

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client profile not found"
        )

    # Check if documents are uploaded
    if not client.kyc_uploaded:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please upload all required documents before submitting for review",
        )

    # Update status to pending review
    client.status = ClientStatus.PENDING_REVIEW
    client.onboarding_completed = True
    await db.commit()
    await db.refresh(client)

    return {
        "message": "Documents submitted successfully! Your submission is now under review.",
        "status": client.status.value,
        "redirect_to": "/client/dashboard/inactive",
    }


@router.put("/mark-kyc-uploaded")
async def mark_kyc_uploaded(
    db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)
):
    """Mark that KYC documents have been uploaded"""

    client_repo = BaseRepository(Client, db)
    client = await client_repo.get_by_field("user_id", current_user.id)

    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Client profile not found"
        )

    client.kyc_uploaded = True
    await db.commit()

    return {"message": "KYC upload status updated", "kyc_uploaded": True}
