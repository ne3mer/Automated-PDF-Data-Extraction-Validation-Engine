"""
Field Extraction Engine
Extracts structured fields from PDF text using regex patterns and layout parsing
"""
import re
import logging
from datetime import datetime
from typing import Dict, Optional, List, Any
from .text_extractor import TextExtractor
import config

logger = logging.getLogger(__name__)


class FieldExtractor:
    """Extracts structured fields from extracted PDF text"""
    
    def __init__(self, text_extractor: TextExtractor):
        """
        Initialize field extractor
        
        Args:
            text_extractor: TextExtractor instance with extracted text
        """
        self.text_extractor = text_extractor
        self.extracted_text = text_extractor.extracted_text or ""
        self.extracted_fields: Dict[str, Any] = {}
    
    def extract_invoice_number(self) -> Optional[str]:
        """Extract invoice number from text"""
        text = self.extracted_text.upper()
        
        # Common words that shouldn't be considered invoice numbers
        excluded_words = {
            "OMSCHRIJVING", "DESCRIPTION", "BESCHRIJVING", "ARTIKEL", "ARTICLE",
            "ITEM", "PRODUCT", "PRODUKT", "NAAM", "NAME", "TITEL", "TITLE"
        }
        
        for pattern in config.INVOICE_NUMBER_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                invoice_num = match.group(0).strip()
                # Clean up common prefixes/suffixes
                invoice_num = re.sub(r'^(INVOICE|INV)[\s\-:#]+', '', invoice_num, flags=re.IGNORECASE)
                invoice_num = re.sub(r'^#\s*', '', invoice_num)
                
                # Skip if it's a common excluded word
                if invoice_num.upper() in excluded_words:
                    continue
                
                # Must contain at least one digit or be a valid format
                if invoice_num and (re.search(r'\d', invoice_num) or len(invoice_num) > 3):
                    logger.debug(f"Found invoice number: {invoice_num}")
                    return invoice_num.strip()
        
        return None
    
    def extract_dates(self) -> Dict[str, Optional[str]]:
        """Extract issue date and due date from text"""
        dates = {"issue_date": None, "due_date": None}
        text = self.extracted_text
        
        # Common date label patterns
        issue_date_patterns = [
            r"(?:issue|invoice|date|dated|issued)[\s:]+(\d{4}[-/]\d{2}[-/]\d{2})",
            r"(?:issue|invoice|date|dated|issued)[\s:]+(\d{2}[-/]\d{2}[-/]\d{4})",
            r"(?:issue|invoice|date|dated|issued)[\s:]+(\d{1,2}\s+\w{3,9}\s+\d{4})",
        ]
        
        due_date_patterns = [
            r"(?:due|payment\s+due|due\s+date)[\s:]+(\d{4}[-/]\d{2}[-/]\d{2})",
            r"(?:due|payment\s+due|due\s+date)[\s:]+(\d{2}[-/]\d{2}[-/]\d{4})",
            r"(?:due|payment\s+due|due\s+date)[\s:]+(\d{1,2}\s+\w{3,9}\s+\d{4})",
        ]
        
        # Try to find issue date
        for pattern in issue_date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                dates["issue_date"] = self._normalize_date(match.group(1))
                if dates["issue_date"]:
                    break
        
        # Try to find due date
        for pattern in due_date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                dates["due_date"] = self._normalize_date(match.group(1))
                if dates["due_date"]:
                    break
        
        # If no labeled dates found, try to extract first date as issue date
        if not dates["issue_date"]:
            for pattern in config.DATE_PATTERNS:
                match = re.search(pattern, text)
                if match:
                    dates["issue_date"] = self._normalize_date(match.group(0))
                    if dates["issue_date"]:
                        break
        
        return dates
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """Normalize date string to ISO format (YYYY-MM-DD)"""
        if not date_str:
            return None
        
        date_str = date_str.strip()
        
        # Try different date formats
        date_formats = [
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%m/%d/%Y",
            "%m-%d-%Y",
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%d %B %Y",
            "%d %b %Y",
            "%B %d, %Y",
            "%b %d, %Y",
        ]
        
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date: {date_str}")
        return None
    
    def extract_amounts(self) -> Dict[str, Optional[float]]:
        """Extract total amount and tax amount from text"""
        amounts = {"total_amount": None, "tax_amount": None}
        text = self.extracted_text.upper()
        
        # Total amount patterns
        total_patterns = [
            r"TOTAL[:\s]+[\$€£]?\s*([\d,]+\.?\d*)",
            r"AMOUNT[:\s]+[\$€£]?\s*([\d,]+\.?\d*)",
            r"GRAND\s+TOTAL[:\s]+[\$€£]?\s*([\d,]+\.?\d*)",
            r"TOTAL\s+DUE[:\s]+[\$€£]?\s*([\d,]+\.?\d*)",
        ]
        
        # Tax amount patterns
        tax_patterns = [
            r"TAX[:\s]+[\$€£]?\s*([\d,]+\.?\d*)",
            r"VAT[:\s]+[\$€£]?\s*([\d,]+\.?\d*)",
            r"GST[:\s]+[\$€£]?\s*([\d,]+\.?\d*)",
            r"TAX\s+AMOUNT[:\s]+[\$€£]?\s*([\d,]+\.?\d*)",
        ]
        
        # Extract total amount
        for pattern in total_patterns:
            match = re.search(pattern, text)
            if match:
                amount_str = match.group(1).replace(",", "")
                try:
                    amounts["total_amount"] = float(amount_str)
                    logger.debug(f"Found total amount: {amounts['total_amount']}")
                    break
                except ValueError:
                    continue
        
        # Extract tax amount
        for pattern in tax_patterns:
            match = re.search(pattern, text)
            if match:
                amount_str = match.group(1).replace(",", "")
                try:
                    amounts["tax_amount"] = float(amount_str)
                    logger.debug(f"Found tax amount: {amounts['tax_amount']}")
                    break
                except ValueError:
                    continue
        
        return amounts
    
    def extract_currency(self) -> Optional[str]:
        """Extract currency code from text"""
        text = self.extracted_text
        text_upper = text.upper()
        
        # Priority: Check for currency symbols first (most reliable)
        if "€" in text or "EUR" in text_upper or "EURO" in text_upper:
            logger.debug("Found currency: EUR")
            return "EUR"
        elif "$" in text or "USD" in text_upper:
            logger.debug("Found currency: USD")
            return "USD"
        elif "£" in text or "GBP" in text_upper:
            logger.debug("Found currency: GBP")
            return "GBP"
        
        # Check for other currency codes (case-insensitive)
        currency_codes = ["CAD", "AUD", "JPY", "CHF", "CNY", "INR", "BRL"]
        for code in currency_codes:
            pattern = r"\b" + code + r"\b"
            if re.search(pattern, text_upper):
                logger.debug(f"Found currency code: {code}")
                return code
        
        return None
    
    def extract_vendor_name(self) -> Optional[str]:
        """Extract vendor/supplier name from text"""
        text = self.extracted_text
        
        # Common vendor label patterns
        vendor_patterns = [
            r"(?:from|vendor|supplier|seller|company)[\s:]+([A-Z][A-Za-z\s&.,]+?)(?:\n|$|Invoice|Date|Total)",
            r"^([A-Z][A-Za-z\s&.,]{3,50}?)(?:\n|$|Invoice|Address)",
        ]
        
        for pattern in vendor_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                vendor = match.group(1).strip()
                # Clean up common suffixes
                vendor = re.sub(r'\s+(LTD|LLC|INC|CORP|CORPORATION|CO)\.?$', '', vendor, flags=re.IGNORECASE)
                if len(vendor) > 3 and len(vendor) < 100:
                    logger.debug(f"Found vendor name: {vendor}")
                    return vendor
        
        return None
    
    def extract_client_name(self) -> Optional[str]:
        """Extract client/customer name from text"""
        text = self.extracted_text
        
        # Common client label patterns
        client_patterns = [
            r"(?:to|bill\s+to|customer|client|buyer)[\s:]+([A-Z][A-Za-z\s&.,]+?)(?:\n|$|Invoice|Date|Total)",
            r"BILL\s+TO[:\s]+([A-Z][A-Za-z\s&.,]+?)(?:\n|$)",
        ]
        
        for pattern in client_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                client = match.group(1).strip()
                if len(client) > 3 and len(client) < 100:
                    logger.debug(f"Found client name: {client}")
                    return client
        
        return None
    
    def extract_payment_terms(self) -> Optional[str]:
        """Extract payment terms from text"""
        text = self.extracted_text.upper()
        
        payment_patterns = [
            r"PAYMENT\s+TERMS[:\s]+([^\n]+)",
            r"TERMS[:\s]+([^\n]+)",
            r"(NET\s+\d+)",
            r"(\d+\s+DAYS)",
        ]
        
        for pattern in payment_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                terms = match.group(1).strip()
                if len(terms) < 100:
                    logger.debug(f"Found payment terms: {terms}")
                    return terms
        
        return None
    
    def extract_reference_number(self) -> Optional[str]:
        """Extract reference number (PO number, etc.) from text"""
        text = self.extracted_text.upper()
        
        ref_patterns = [
            r"PO[-\s]?#?\s*([\w\d-]+)",
            r"PURCHASE\s+ORDER[-\s]?#?\s*([\w\d-]+)",
            r"REF[-\s]?#?\s*([\w\d-]+)",
            r"REFERENCE[-\s]?#?\s*([\w\d-]+)",
        ]
        
        for pattern in ref_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                ref = match.group(1).strip()
                logger.debug(f"Found reference number: {ref}")
                return ref
        
        return None
    
    def extract_contract_number(self) -> Optional[str]:
        """Extract contract number from text"""
        text = self.extracted_text.upper()
        
        contract_patterns = [
            r"CONTRACT[-\s]?#?\s*([\w\d-]+)",
            r"CONTRACT\s+NUMBER[-\s]?#?\s*([\w\d-]+)",
        ]
        
        for pattern in contract_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                contract = match.group(1).strip()
                logger.debug(f"Found contract number: {contract}")
                return contract
        
        return None
    
    def extract_document_type(self) -> str:
        """Detect document type from text"""
        text = self.extracted_text.upper()
        
        if re.search(r"\bINVOICE\b", text):
            return "invoice"
        elif re.search(r"\bPURCHASE\s+ORDER\b", text):
            return "purchase_order"
        elif re.search(r"\bCONTRACT\b", text):
            return "contract"
        elif re.search(r"\bSTATEMENT\b", text):
            return "statement"
        elif re.search(r"\bREPORT\b", text):
            return "report"
        else:
            return "unknown"
    
    def extract_all_fields(self) -> Dict[str, Any]:
        """Extract all fields from the PDF text"""
        logger.info("Starting field extraction...")
        
        # Extract all fields
        self.extracted_fields = {
            "document_type": self.extract_document_type(),
            "vendor_name": self.extract_vendor_name(),
            "client_name": self.extract_client_name(),
            "invoice_number": self.extract_invoice_number(),
            "contract_number": self.extract_contract_number(),
            "payment_terms": self.extract_payment_terms(),
            "reference_number": self.extract_reference_number(),
            "currency": self.extract_currency(),
        }
        
        # Extract dates
        dates = self.extract_dates()
        self.extracted_fields.update(dates)
        
        # Extract amounts
        amounts = self.extract_amounts()
        self.extracted_fields.update(amounts)
        
        # Add text snapshot
        self.extracted_fields["raw_text_snapshot"] = self.text_extractor.get_text_snapshot(
            config.TEXT_EXTRACTION["max_raw_text_length"]
        )
        
        logger.info(f"Field extraction completed. Extracted {len([v for v in self.extracted_fields.values() if v])} fields")
        
        return self.extracted_fields

