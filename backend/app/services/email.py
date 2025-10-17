"""Email service for sending notifications"""
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending notifications (Mock implementation)"""

    @staticmethod
    async def send_registration_confirmation(email: str, business_name: str):
        """Send registration confirmation email"""
        logger.info(f"📧 [MOCK EMAIL] Registration Confirmation")
        logger.info(f"   To: {email}")
        logger.info(f"   Subject: Registration Received - {business_name}")
        logger.info(
            f"   Body: Your registration has been received and is pending admin verification."
        )
        return True

    @staticmethod
    async def send_temporary_credentials(
        email: str, temp_password: str, business_name: str
    ):
        """Send temporary login credentials"""
        logger.info(f"📧 [MOCK EMAIL] Temporary Credentials")
        logger.info(f"   To: {email}")
        logger.info(f"   Subject: Your Client Portal Access - {business_name}")
        logger.info(f"   Temporary Password: {temp_password}")
        logger.info(f"   Login URL: http://localhost:3000/login")
        logger.info(
            f"   Note: You will be required to change your password on first login."
        )
        return True

    @staticmethod
    async def send_rejection_notification(email: str, business_name: str, reason: str):
        """Send registration rejection email"""
        logger.info(f"📧 [MOCK EMAIL] Registration Rejected")
        logger.info(f"   To: {email}")
        logger.info(f"   Subject: Registration Update - {business_name}")
        logger.info(f"   Reason: {reason}")
        return True

    @staticmethod
    async def send_kyc_status_notification(
        email: str, document_type: str, approved: bool, comments: Optional[str] = None
    ):
        """Send KYC document verification status"""
        status = "Approved" if approved else "Rejected"
        logger.info(f"📧 [MOCK EMAIL] KYC Document {status}")
        logger.info(f"   To: {email}")
        logger.info(f"   Document: {document_type}")
        logger.info(f"   Status: {status}")
        if comments:
            logger.info(f"   Comments: {comments}")
        return True

    @staticmethod
    async def send_payment_verification_notification(
        email: str, amount: float, approved: bool, notes: Optional[str] = None
    ):
        """Send payment verification status"""
        status = "Approved" if approved else "Rejected"
        logger.info(f"📧 [MOCK EMAIL] Payment {status}")
        logger.info(f"   To: {email}")
        logger.info(f"   Amount: GHS {amount:,.2f}")
        logger.info(f"   Status: {status}")
        if notes:
            logger.info(f"   Notes: {notes}")
        return True

    @staticmethod
    async def send_activation_notification(
        email: str, business_name: str, account_manager_name: str
    ):
        """Send portal activation notification"""
        logger.info(f"📧 [MOCK EMAIL] Portal Activated!")
        logger.info(f"   To: {email}")
        logger.info(f"   Subject: Welcome to Eranos Consulting Client Portal")
        logger.info(f"   Business: {business_name}")
        logger.info(f"   Account Manager: {account_manager_name}")
        logger.info(f"   Your portal is now fully active!")
        return True

    @staticmethod
    async def send_admin_new_registration_alert(
        admin_email: str, business_name: str, client_email: str
    ):
        """Alert admin of new registration"""
        logger.info(f"📧 [MOCK EMAIL] New Client Registration Alert")
        logger.info(f"   To: {admin_email}")
        logger.info(f"   Subject: New Client Registration Pending")
        logger.info(f"   Business: {business_name}")
        logger.info(f"   Email: {client_email}")
        logger.info(f"   Action Required: Please review and verify")
        return True


# Singleton instance
email_service = EmailService()
