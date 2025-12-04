"""
Data Normalization and Cleaning Module
Cleans and normalizes extracted field values
"""
import re
import logging
from typing import Any, Optional, Dict

logger = logging.getLogger(__name__)


class DataCleaner:
    """Cleans and normalizes extracted data fields"""
    
    @staticmethod
    def clean_string(value: Any) -> Optional[str]:
        """
        Clean string values
        
        Args:
            value: Value to clean
            
        Returns:
            Cleaned string or None
        """
        if value is None:
            return None
        
        if not isinstance(value, str):
            value = str(value)
        
        # Remove extra whitespace
        value = re.sub(r'\s+', ' ', value.strip())
        
        # Remove special characters that shouldn't be in names/IDs
        value = re.sub(r'[^\w\s\-.,&()]', '', value)
        
        if not value:
            return None
        
        return value
    
    @staticmethod
    def clean_numeric(value: Any) -> Optional[float]:
        """
        Clean and convert numeric values
        
        Args:
            value: Value to clean
            
        Returns:
            Cleaned float or None
        """
        if value is None:
            return None
        
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Remove currency symbols, commas, and whitespace
            cleaned = re.sub(r'[\$€£,\s]', '', value)
            try:
                return float(cleaned)
            except ValueError:
                logger.warning(f"Could not convert to numeric: {value}")
                return None
        
        return None
    
    @staticmethod
    def clean_date(value: Any) -> Optional[str]:
        """
        Clean date values (should already be in ISO format from extractor)
        
        Args:
            value: Date value to clean
            
        Returns:
            Cleaned date string in ISO format or None
        """
        if value is None:
            return None
        
        if isinstance(value, str):
            # Remove extra whitespace
            value = value.strip()
            
            # Check if already in ISO format
            if re.match(r'^\d{4}-\d{2}-\d{2}$', value):
                return value
        
        return None
    
    @staticmethod
    def clean_currency_code(value: Any) -> Optional[str]:
        """
        Clean and validate currency codes
        
        Args:
            value: Currency value to clean
            
        Returns:
            Cleaned currency code (uppercase) or None
        """
        if value is None:
            return None
        
        if isinstance(value, str):
            # Convert to uppercase and remove whitespace
            code = value.strip().upper()
            
            # Valid currency codes
            valid_codes = ["USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF", "CNY", "INR", "BRL"]
            
            if code in valid_codes:
                return code
        
        return None
    
    @staticmethod
    def clean_invoice_number(value: Any) -> Optional[str]:
        """
        Clean invoice number
        
        Args:
            value: Invoice number to clean
            
        Returns:
            Cleaned invoice number or None
        """
        if value is None:
            return None
        
        if isinstance(value, str):
            # Remove common prefixes and normalize
            cleaned = value.strip().upper()
            cleaned = re.sub(r'^(INVOICE|INV)[\s\-:#]+', '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'^#\s*', '', cleaned)
            cleaned = re.sub(r'\s+', '-', cleaned.strip())
            
            if cleaned:
                return cleaned
        
        return None
    
    @staticmethod
    def clean_all_fields(fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean all fields in a dictionary
        
        Args:
            fields: Dictionary of extracted fields
            
        Returns:
            Dictionary with cleaned fields
        """
        cleaned = {}
        
        # String fields
        string_fields = [
            "vendor_name", "client_name", "payment_terms",
            "reference_number", "contract_number", "document_type",
            "raw_text_snapshot", "source_file_name"
        ]
        
        for field in string_fields:
            if field in fields:
                cleaned[field] = DataCleaner.clean_string(fields[field])
        
        # Numeric fields
        numeric_fields = ["total_amount", "tax_amount"]
        for field in numeric_fields:
            if field in fields:
                cleaned[field] = DataCleaner.clean_numeric(fields[field])
        
        # Date fields
        date_fields = ["issue_date", "due_date"]
        for field in date_fields:
            if field in fields:
                cleaned[field] = DataCleaner.clean_date(fields[field])
        
        # Special fields
        if "invoice_number" in fields:
            cleaned["invoice_number"] = DataCleaner.clean_invoice_number(fields["invoice_number"])
        
        if "currency" in fields:
            cleaned["currency"] = DataCleaner.clean_currency_code(fields["currency"])
        
        # Preserve other fields as-is
        for key, value in fields.items():
            if key not in cleaned:
                cleaned[key] = value
        
        return cleaned
    
    @staticmethod
    def remove_empty_fields(fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Remove fields with None or empty values
        
        Args:
            fields: Dictionary of fields
            
        Returns:
            Dictionary with empty fields removed
        """
        return {k: v for k, v in fields.items() if v is not None and v != ""}

