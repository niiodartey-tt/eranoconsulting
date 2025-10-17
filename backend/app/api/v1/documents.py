"""General document upload API endpoints"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
import json

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_admin, get_current_staff
from app.models.user import User
from app.models.client import Client
from app.models.document import Document
from app.schemas.document import (
    DocumentUploadResponse,
    DocumentOut,
    ReceiptIssuedRequest,
    ReceiptIssuedResponse
)
from app.services.file_storage import file_storage_service, FileCategory

router = APIRouter()

ALLOWED_FILE_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/png",
    "image/jpg",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


# ==================== CLIENT DOCUMENT UPLOAD ====================

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    category: str = Form(...),
    file: UploadFile = File(...),
    document_date: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Client uploads a general document"""
    
    # Get client
    result = await db.execute(select(Client).where(Client.user_id == current_user.id))
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client record not found")
    
    # Validate file type
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not allowed."
        )
    
    # Read and validate file size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large. Maximum 10MB.")
    
    # Parse document date
    doc_date = None
    if document_date:
        try:
            doc_date = datetime.fromisoformat(document_date.replace('Z', '+00:00'))
        except:
            doc_date = datetime.now()
    else:
        doc_date = datetime.now()
    
    # Parse tags
    tag_list = []
    if tags:
        try:
            tag_list = json.loads(tags)
        except:
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]
    
    # Save file using organized storage
    full_path, relative_path = file_storage_service.save_document(
        client_id=client.id,
        business_name=client.business_name,
        category=category,
        original_filename=file.filename,
        file_contents=contents,
        document_date=doc_date
    )
    
    # Get quarter info
    quarter, _ = file_storage_service.get_quarter_from_month(doc_date.month)
    year = doc_date.strftime("%Y")
    
    # Create database record
    document = Document(
        client_id=client.id,
        category=category,
        filename=file.filename,
        file_path=relative_path,
        file_size=len(contents),
        mime_type=file.content_type,
        year=year,
        quarter=quarter,
        document_date=doc_date,
        description=description,
        tags=tag_list,
        uploaded_by_id=current_user.id
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    
    return DocumentUploadResponse(
        id=document.id,
        client_id=document.client_id,
        category=document.category,
        filename=document.filename,
        file_path=document.file_path,
        file_size=document.file_size,
        quarter=document.quarter,
        year=document.year,
        uploaded_at=document.uploaded_at
    )


@router.get("/my-documents", response_model=List[DocumentOut])
async def get_my_documents(
    category: Optional[str] = None,
    year: Optional[str] = None,
    quarter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current client's documents with optional filters"""
    
    result = await db.execute(select(Client).where(Client.user_id == current_user.id))
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client record not found")
    
    # Build query
    query = select(Document).where(Document.client_id == client.id)
    
    if category:
        query = query.where(Document.category == category)
    if year:
        query = query.where(Document.year == year)
    if quarter:
        query = query.where(Document.quarter == quarter)
    
    query = query.order_by(Document.uploaded_at.desc())
    
    result = await db.execute(query)
    documents = result.scalars().all()
    
    return [DocumentOut.model_validate(doc) for doc in documents]


@router.get("/categories")
async def get_document_categories(current_user: User = Depends(get_current_user)):
    """Get list of available document categories"""
    
    return {
        "categories": [
            {"value": FileCategory.BANK_STATEMENTS, "label": "Bank Statements"},
            {"value": FileCategory.TAX_FILINGS, "label": "Tax Filings"},
            {"value": FileCategory.PAYROLL, "label": "Payroll Documents"},
            {"value": FileCategory.INVOICES, "label": "Invoices"},
            {"value": FileCategory.RECEIPTS, "label": "Receipts"},
            {"value": FileCategory.CONTRACTS, "label": "Contracts"},
            {"value": FileCategory.AUDIT_REPORTS, "label": "Audit Reports"},
            {"value": FileCategory.FINANCIAL_STATEMENTS, "label": "Financial Statements"},
            {"value": FileCategory.CORRESPONDENCE, "label": "Correspondence"},
            {"value": FileCategory.OTHER, "label": "Other Documents"},
        ]
    }


# ==================== STAFF/ADMIN DOCUMENT UPLOAD FOR CLIENT ====================

@router.post("/upload-for-client/{client_id}", response_model=DocumentUploadResponse)
async def upload_document_for_client(
    client_id: int,
    category: str = Form(...),
    file: UploadFile = File(...),
    document_date: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),
    current_user: User = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db)
):
    """Staff/Admin uploads document on behalf of client"""
    
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    
    if file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file.content_type} not allowed."
        )
    
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large. Maximum 10MB.")
    
    doc_date = None
    if document_date:
        try:
            doc_date = datetime.fromisoformat(document_date.replace('Z', '+00:00'))
        except:
            doc_date = datetime.now()
    else:
        doc_date = datetime.now()
    
    tag_list = []
    if tags:
        try:
            tag_list = json.loads(tags)
        except:
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]
    
    full_path, relative_path = file_storage_service.save_document(
        client_id=client.id,
        business_name=client.business_name,
        category=category,
        original_filename=file.filename,
        file_contents=contents,
        document_date=doc_date
    )
    
    quarter, _ = file_storage_service.get_quarter_from_month(doc_date.month)
    year = doc_date.strftime("%Y")
    
    document = Document(
        client_id=client.id,
        category=category,
        filename=file.filename,
        file_path=relative_path,
        file_size=len(contents),
        mime_type=file.content_type,
        year=year,
        quarter=quarter,
        document_date=doc_date,
        description=description,
        tags=tag_list,
        uploaded_by_id=current_user.id
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    
    return DocumentUploadResponse(
        id=document.id,
        client_id=document.client_id,
        category=document.category,
        filename=document.filename,
        file_path=document.file_path,
        file_size=document.file_size,
        quarter=document.quarter,
        year=document.year,
        uploaded_at=document.uploaded_at
    )


@router.get("/client/{client_id}/documents", response_model=List[DocumentOut])
async def get_client_documents(
    client_id: int,
    category: Optional[str] = None,
    year: Optional[str] = None,
    quarter: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _staff: User = Depends(get_current_staff)
):
    """Staff/Admin: Get documents for specific client"""
    
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    
    query = select(Document).where(Document.client_id == client_id)
    
    if category:
        query = query.where(Document.category == category)
    if year:
        query = query.where(Document.year == year)
    if quarter:
        query = query.where(Document.quarter == quarter)
    
    query = query.order_by(Document.uploaded_at.desc())
    
    result = await db.execute(query)
    documents = result.scalars().all()
    
    return [DocumentOut.model_validate(doc) for doc in documents]


@router.delete("/document/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a document (owner or staff only)"""
    
    result = await db.execute(select(Document).where(Document.id == document_id))
    document = result.scalar_one_or_none()
    
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    
    # Check permissions
    result = await db.execute(select(Client).where(Client.user_id == current_user.id))
    client = result.scalar_one_or_none()
    
    # Allow if document owner or staff/admin
    from app.models.user import UserRole
    if not (client and client.id == document.client_id) and current_user.role not in [UserRole.ADMIN, UserRole.STAFF]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    # Delete from database
    await db.delete(document)
    await db.commit()
    
    # Optionally delete physical file (be careful!)
    # from pathlib import Path
    # file_path = Path("uploads") / document.file_path
    # if file_path.exists():
    #     file_path.unlink()
    
    return None


# ==================== RECEIPT ISSUANCE (STAFF/ADMIN) ====================

@router.post("/issue-receipt/{client_id}", response_model=ReceiptIssuedResponse)
async def issue_receipt_to_client(
    client_id: int,
    receipt_number: str = Form(...),
    amount: float = Form(...),
    description: str = Form(...),
    receipt_file: UploadFile = File(...),
    receipt_date: Optional[str] = Form(None),
    current_user: User = Depends(get_current_staff),
    db: AsyncSession = Depends(get_db)
):
    """Staff/Admin: Issue receipt to client"""
    
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    
    if receipt_file.content_type not in ALLOWED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {receipt_file.content_type} not allowed."
        )
    
    contents = await receipt_file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File too large. Maximum 10MB.")
    
    # Parse receipt date
    rec_date = None
    if receipt_date:
        try:
            rec_date = datetime.fromisoformat(receipt_date.replace('Z', '+00:00'))
        except:
            rec_date = datetime.now()
    else:
        rec_date = datetime.now()
    
    # Save receipt
    full_path, relative_path = file_storage_service.save_receipt_issued(
        client_id=client.id,
        business_name=client.business_name,
        receipt_number=receipt_number,
        original_filename=receipt_file.filename,
        file_contents=contents,
        receipt_date=rec_date
    )
    
    # Create document record for receipt
    quarter, _ = file_storage_service.get_quarter_from_month(rec_date.month)
    year = rec_date.strftime("%Y")
    
    document = Document(
        client_id=client.id,
        category="receipts",
        filename=receipt_file.filename,
        file_path=relative_path,
        file_size=len(contents),
        mime_type=receipt_file.content_type,
        year=year,
        quarter=quarter,
        document_date=rec_date,
        description=f"Receipt #{receipt_number} - {description} - GHS {amount:,.2f}",
        tags=["receipt", "issued", receipt_number],
        uploaded_by_id=current_user.id
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)
    
    return ReceiptIssuedResponse(
        id=document.id,
        client_id=document.client_id,
        receipt_number=receipt_number,
        file_path=document.file_path,
        amount=amount,
        issued_at=document.uploaded_at
    )


# ==================== STATISTICS ====================

@router.get("/stats")
async def get_document_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get document statistics for current client"""
    
    result = await db.execute(select(Client).where(Client.user_id == current_user.id))
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client record not found")
    
    # Count by category
    from sqlalchemy import func as sql_func
    result = await db.execute(
        select(Document.category, sql_func.count(Document.id))
        .where(Document.client_id == client.id)
        .group_by(Document.category)
    )
    
    category_counts = {row[0]: row[1] for row in result.all()}
    
    # Count by year/quarter
    result = await db.execute(
        select(Document.year, Document.quarter, sql_func.count(Document.id))
        .where(Document.client_id == client.id)
        .group_by(Document.year, Document.quarter)
        .order_by(Document.year.desc(), Document.quarter.desc())
    )
    
    period_counts = [
        {"year": row[0], "quarter": row[1], "count": row[2]}
        for row in result.all()
    ]
    
    # Total size
    result = await db.execute(
        select(sql_func.sum(Document.file_size))
        .where(Document.client_id == client.id)
    )
    total_size = result.scalar() or 0
    
    return {
        "total_documents": sum(category_counts.values()),
        "category_breakdown": category_counts,
        "period_breakdown": period_counts,
        "total_storage_bytes": total_size,
        "total_storage_mb": round(total_size / (1024 * 1024), 2)
    }


@router.get("/admin/client/{client_id}/stats")
async def get_client_document_stats(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    _staff: User = Depends(get_current_staff)
):
    """Staff/Admin: Get document statistics for specific client"""
    
    result = await db.execute(select(Client).where(Client.id == client_id))
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Client not found")
    
    from sqlalchemy import func as sql_func
    
    result = await db.execute(
        select(Document.category, sql_func.count(Document.id))
        .where(Document.client_id == client_id)
        .group_by(Document.category)
    )
    category_counts = {row[0]: row[1] for row in result.all()}
    
    result = await db.execute(
        select(Document.year, Document.quarter, sql_func.count(Document.id))
        .where(Document.client_id == client_id)
        .group_by(Document.year, Document.quarter)
        .order_by(Document.year.desc(), Document.quarter.desc())
    )
    period_counts = [
        {"year": row[0], "quarter": row[1], "count": row[2]}
        for row in result.all()
    ]
    
    result = await db.execute(
        select(sql_func.sum(Document.file_size))
        .where(Document.client_id == client_id)
    )
    total_size = result.scalar() or 0
    
    return {
        "client_id": client_id,
        "business_name": client.business_name,
        "total_documents": sum(category_counts.values()),
        "category_breakdown": category_counts,
        "period_breakdown": period_counts,
        "total_storage_bytes": total_size,
        "total_storage_mb": round(total_size / (1024 * 1024), 2)
    }
