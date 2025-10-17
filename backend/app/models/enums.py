"""Enumerations for onboarding workflow"""
import enum


class OnboardingStatus(str, enum.Enum):
    """Client onboarding status workflow"""
    PENDING_VERIFICATION = "pending_verification"  # Step 2: Awaiting admin phone verification
    PRE_ACTIVE = "pre_active"  # Step 3: Account created, needs KYC
    KYC_SUBMISSION = "kyc_submission"  # Step 4: Client uploading KYC documents
    KYC_REVIEW = "kyc_review"  # Step 5: Admin reviewing KYC documents
    PAYMENT_REVIEW = "payment_review"  # Step 5: Admin reviewing payment receipt
    AWAITING_SIGNATURE = "awaiting_signature"  # Step 6: Engagement letter sent
    ACTIVE = "active"  # Step 7: Fully onboarded and active
    REJECTED = "rejected"  # Admin rejected registration
    SUSPENDED = "suspended"  # Account suspended


class DocumentType(str, enum.Enum):
    """Types of KYC documents required"""
    # Business documents
    RGD_CERTIFICATE = "rgd_certificate"  # Certificate of Incorporation
    TIN_CERTIFICATE = "tin_certificate"  # Tax Identification Number
    VAT_CERTIFICATE = "vat_certificate"  # VAT Registration
    SSNIT_PROOF = "ssnit_proof"  # SSNIT Registration Proof
    
    # Director/Owner documents
    GHANA_CARD = "ghana_card"  # Ghana Card (National ID)
    PASSPORT = "passport"  # Passport
    PROOF_OF_ADDRESS = "proof_of_address"  # Utility bill or bank statement
    
    # Other
    OTHER = "other"  # Additional documents


class VerificationStatus(str, enum.Enum):
    """Document/Payment verification status"""
    PENDING = "pending"  # Awaiting review
    APPROVED = "approved"  # Verified and approved
    REJECTED = "rejected"  # Rejected with reason
    RESUBMISSION_REQUIRED = "resubmission_required"  # Needs to be resubmitted


class ServiceType(str, enum.Enum):
    """Types of services offered by Eranos Consulting"""
    TAX_COMPLIANCE = "tax_compliance"
    AUDIT_ASSURANCE = "audit_assurance"
    BUSINESS_ADVISORY = "business_advisory"
    ACCOUNTING_BOOKKEEPING = "accounting_bookkeeping"
    PAYROLL_MANAGEMENT = "payroll_management"
    COMPANY_REGISTRATION = "company_registration"
    FINANCIAL_CONSULTING = "financial_consulting"
