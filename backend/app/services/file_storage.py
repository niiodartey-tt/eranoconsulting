"""File storage service with organized folder structure per client"""
from pathlib import Path
from datetime import datetime
from typing import Optional
import re
import secrets


class FileCategory:
    """Document categories for organized storage"""
    BANK_STATEMENTS = "bank_statements"
    TAX_FILINGS = "tax_filings"
    PAYROLL = "payroll"
    INVOICES = "invoices"
    RECEIPTS = "receipts"
    CONTRACTS = "contracts"
    AUDIT_REPORTS = "audit_reports"
    FINANCIAL_STATEMENTS = "financial_statements"
    CORRESPONDENCE = "correspondence"
    OTHER = "other"


class FileStorageService:
    """Manages organized file storage for clients"""
    
    def __init__(self, base_upload_dir: str = "uploads"):
        self.base_dir = Path(base_upload_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def sanitize_name(name: str) -> str:
        """Sanitize business name for folder creation"""
        # Remove special characters, keep alphanumeric and spaces
        sanitized = re.sub(r'[^\w\s-]', '', name.lower())
        # Replace spaces with underscores
        sanitized = re.sub(r'\s+', '_', sanitized)
        # Remove multiple underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        return sanitized.strip('_')
    
    def get_client_root_folder(self, client_id: int, business_name: str) -> Path:
        """Get or create client's root folder"""
        sanitized_name = self.sanitize_name(business_name)
        folder_name = f"client_{client_id}_{sanitized_name}"
        client_folder = self.base_dir / folder_name
        client_folder.mkdir(parents=True, exist_ok=True)
        return client_folder
    
    def get_kyc_folder(self, client_id: int, business_name: str) -> Path:
        """Get or create client's KYC folder"""
        client_folder = self.get_client_root_folder(client_id, business_name)
        kyc_folder = client_folder / "kyc"
        kyc_folder.mkdir(parents=True, exist_ok=True)
        return kyc_folder
    
    def get_payment_folder(
        self, 
        client_id: int, 
        business_name: str,
        payment_date: Optional[datetime] = None
    ) -> Path:
        """Get or create client's payment folder organized by year/month"""
        client_folder = self.get_client_root_folder(client_id, business_name)
        
        # Use provided date or current date
        date = payment_date or datetime.now()
        year = date.strftime("%Y")
        month_num = date.strftime("%m")
        month_name = date.strftime("%B").lower()
        
        # Structure: payments/2025/01_january/
        payment_folder = client_folder / "payments" / year / f"{month_num}_{month_name}"
        payment_folder.mkdir(parents=True, exist_ok=True)
        return payment_folder
    
    def get_receipts_issued_folder(
        self,
        client_id: int,
        business_name: str,
        receipt_date: Optional[datetime] = None
    ) -> Path:
        """Get or create folder for receipts issued to client"""
        client_folder = self.get_client_root_folder(client_id, business_name)
        
        date = receipt_date or datetime.now()
        year = date.strftime("%Y")
        month_num = date.strftime("%m")
        month_name = date.strftime("%B").lower()
        
        receipt_folder = client_folder / "payments" / "receipts_issued" / year / f"{month_num}_{month_name}"
        receipt_folder.mkdir(parents=True, exist_ok=True)
        return receipt_folder
    
    def get_quarter_from_month(self, month: int) -> tuple[str, str]:
        """Get quarter folder name from month number"""
        quarters = {
            (1, 2, 3): ("q1_jan_mar", "Q1 (Jan-Mar)"),
            (4, 5, 6): ("q2_apr_jun", "Q2 (Apr-Jun)"),
            (7, 8, 9): ("q3_jul_sep", "Q3 (Jul-Sep)"),
            (10, 11, 12): ("q4_oct_dec", "Q4 (Oct-Dec)")
        }
        
        for months, (folder, display) in quarters.items():
            if month in months:
                return folder, display
        
        return "q1_jan_mar", "Q1 (Jan-Mar)"  # Default
    
    def get_document_folder(
        self,
        client_id: int,
        business_name: str,
        category: str,
        document_date: Optional[datetime] = None
    ) -> Path:
        """
        Get or create document folder organized by year/quarter/category
        
        Structure: documents/2025/q1_jan_mar/bank_statements/
        """
        client_folder = self.get_client_root_folder(client_id, business_name)
        
        date = document_date or datetime.now()
        year = date.strftime("%Y")
        month = date.month
        quarter, _ = self.get_quarter_from_month(month)
        
        # Structure: documents/year/quarter/category/
        doc_folder = client_folder / "documents" / year / quarter / category
        doc_folder.mkdir(parents=True, exist_ok=True)
        return doc_folder
    
    def generate_unique_filename(
        self,
        original_filename: str,
        prefix: Optional[str] = None
    ) -> str:
        """Generate unique filename with timestamp and random token"""
        # Get file extension
        file_ext = Path(original_filename).suffix
        
        # Generate timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate random token
        token = secrets.token_hex(4)
        
        # Build filename
        if prefix:
            sanitized_prefix = self.sanitize_name(prefix)
            return f"{sanitized_prefix}_{timestamp}_{token}{file_ext}"
        else:
            # Use sanitized original name (without extension)
            name_without_ext = Path(original_filename).stem
            sanitized_name = self.sanitize_name(name_without_ext)
            return f"{sanitized_name}_{timestamp}_{token}{file_ext}"
    
    def save_kyc_document(
        self,
        client_id: int,
        business_name: str,
        document_type: str,
        original_filename: str,
        file_contents: bytes
    ) -> tuple[Path, str]:
        """
        Save KYC document and return (full_path, relative_path)
        """
        folder = self.get_kyc_folder(client_id, business_name)
        filename = self.generate_unique_filename(original_filename, prefix=document_type)
        full_path = folder / filename
        
        # Write file
        full_path.write_bytes(file_contents)
        
        # Return both full path and relative path from base_dir
        relative_path = full_path.relative_to(self.base_dir)
        return full_path, str(relative_path)
    
    def save_payment_receipt(
        self,
        client_id: int,
        business_name: str,
        original_filename: str,
        file_contents: bytes,
        payment_date: Optional[datetime] = None
    ) -> tuple[Path, str]:
        """
        Save payment receipt and return (full_path, relative_path)
        """
        folder = self.get_payment_folder(client_id, business_name, payment_date)
        filename = self.generate_unique_filename(original_filename, prefix="payment")
        full_path = folder / filename
        
        full_path.write_bytes(file_contents)
        relative_path = full_path.relative_to(self.base_dir)
        return full_path, str(relative_path)
    
    def save_receipt_issued(
        self,
        client_id: int,
        business_name: str,
        receipt_number: str,
        original_filename: str,
        file_contents: bytes,
        receipt_date: Optional[datetime] = None
    ) -> tuple[Path, str]:
        """
        Save receipt issued to client
        """
        folder = self.get_receipts_issued_folder(client_id, business_name, receipt_date)
        filename = self.generate_unique_filename(original_filename, prefix=f"receipt_{receipt_number}")
        full_path = folder / filename
        
        full_path.write_bytes(file_contents)
        relative_path = full_path.relative_to(self.base_dir)
        return full_path, str(relative_path)
    
    def save_document(
        self,
        client_id: int,
        business_name: str,
        category: str,
        original_filename: str,
        file_contents: bytes,
        document_date: Optional[datetime] = None
    ) -> tuple[Path, str]:
        """
        Save general document organized by category and quarter
        """
        folder = self.get_document_folder(client_id, business_name, category, document_date)
        filename = self.generate_unique_filename(original_filename)
        full_path = folder / filename
        
        full_path.write_bytes(file_contents)
        relative_path = full_path.relative_to(self.base_dir)
        return full_path, str(relative_path)
    
    def get_client_folder_structure(self, client_id: int, business_name: str) -> dict:
        """Get the folder structure for a client (for display purposes)"""
        client_folder = self.get_client_root_folder(client_id, business_name)
        
        structure = {
            "root": str(client_folder),
            "kyc": str(client_folder / "kyc"),
            "payments": str(client_folder / "payments"),
            "receipts_issued": str(client_folder / "payments" / "receipts_issued"),
            "documents": str(client_folder / "documents"),
            "categories": {
                "bank_statements": FileCategory.BANK_STATEMENTS,
                "tax_filings": FileCategory.TAX_FILINGS,
                "payroll": FileCategory.PAYROLL,
                "invoices": FileCategory.INVOICES,
                "receipts": FileCategory.RECEIPTS,
                "contracts": FileCategory.CONTRACTS,
                "audit_reports": FileCategory.AUDIT_REPORTS,
                "financial_statements": FileCategory.FINANCIAL_STATEMENTS,
                "correspondence": FileCategory.CORRESPONDENCE,
                "other": FileCategory.OTHER,
            }
        }
        
        return structure
    
    def list_client_files(
        self,
        client_id: int,
        business_name: str,
        folder_type: str = "all"
    ) -> dict:
        """
        List all files for a client, organized by type
        
        folder_type: "all", "kyc", "payments", "documents"
        """
        client_folder = self.get_client_root_folder(client_id, business_name)
        
        result = {}
        
        if folder_type in ["all", "kyc"]:
            kyc_folder = client_folder / "kyc"
            if kyc_folder.exists():
                result["kyc"] = [
                    {
                        "filename": f.name,
                        "path": str(f.relative_to(self.base_dir)),
                        "size": f.stat().st_size,
                        "modified": datetime.fromtimestamp(f.stat().st_mtime)
                    }
                    for f in kyc_folder.glob("*") if f.is_file()
                ]
        
        if folder_type in ["all", "payments"]:
            payments_folder = client_folder / "payments"
            if payments_folder.exists():
                result["payments"] = []
                for payment_file in payments_folder.rglob("*"):
                    if payment_file.is_file() and "receipts_issued" not in str(payment_file):
                        result["payments"].append({
                            "filename": payment_file.name,
                            "path": str(payment_file.relative_to(self.base_dir)),
                            "size": payment_file.stat().st_size,
                            "modified": datetime.fromtimestamp(payment_file.stat().st_mtime)
                        })
        
        if folder_type in ["all", "documents"]:
            docs_folder = client_folder / "documents"
            if docs_folder.exists():
                result["documents"] = []
                for doc_file in docs_folder.rglob("*"):
                    if doc_file.is_file():
                        # Extract category from path
                        parts = doc_file.relative_to(docs_folder).parts
                        category = parts[2] if len(parts) > 2 else "other"
                        
                        result["documents"].append({
                            "filename": doc_file.name,
                            "path": str(doc_file.relative_to(self.base_dir)),
                            "category": category,
                            "quarter": parts[1] if len(parts) > 1 else "unknown",
                            "year": parts[0] if len(parts) > 0 else "unknown",
                            "size": doc_file.stat().st_size,
                            "modified": datetime.fromtimestamp(doc_file.stat().st_mtime)
                        })
        
        return result


# Singleton instance
file_storage_service = FileStorageService()
