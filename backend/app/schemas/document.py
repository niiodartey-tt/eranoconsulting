"""Pydantic schemas for general document uploads"""
from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class DocumentUploadRequest(BaseModel):
    """Request for uploading general documents"""
    category: str  # bank_statements, tax_filings, payroll, etc.
    document_date: Optional[datetime] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = []


class DocumentUploadResponse(BaseModel):
    """Response after document upload"""
    id: int
    client_id: int
    category: str
    filename: str
    file_path: str
    file_size: int
    quarter: str
    year: str
    uploaded_at: datetime
    
    class Config:
        from_attributes = True


class DocumentOut(BaseModel):
    """Document details"""
    id: int
    client_id: int
    category: str
    filename: str
    file_path: str
    file_size: int
    description: Optional[str] = None
    tags: Optional[list[str]] = []
    quarter: str
    year: str
    uploaded_at: datetime
    uploaded_by: Optional[int] = None
    
    class Config:
        from_attributes = True


class ReceiptIssuedRequest(BaseModel):
    """Request for issuing receipt to client"""
    receipt_number: str
    amount: float
    description: str
    receipt_date: Optional[datetime] = None


class ReceiptIssuedResponse(BaseModel):
    """Response after issuing receipt"""
    id: int
    client_id: int
    receipt_number: str
    file_path: str
    amount: float
    issued_at: datetime
    
    class Config:
        from_attributes = True
