"""
Configuration file for PDF Data Extraction & Validation Engine
"""
import os
from pathlib import Path
from typing import List, Dict, Any

# Base paths
BASE_DIR = Path(__file__).parent
INPUT_DIR = BASE_DIR / "input_pdfs"
OUTPUT_DIR = BASE_DIR / "output"
JSON_OUTPUT_DIR = OUTPUT_DIR / "json"
EXCEL_OUTPUT_DIR = OUTPUT_DIR / "excel"
REPORTS_OUTPUT_DIR = OUTPUT_DIR / "reports"
LOGS_DIR = BASE_DIR / "logs"

# Ensure directories exist
for directory in [INPUT_DIR, JSON_OUTPUT_DIR, EXCEL_OUTPUT_DIR, REPORTS_OUTPUT_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Field extraction schema
EXTRACTION_SCHEMA = {
    "document_id": None,  # Will be generated as UUID
    "document_type": None,
    "vendor_name": None,
    "client_name": None,
    "invoice_number": None,
    "contract_number": None,
    "issue_date": None,
    "due_date": None,
    "total_amount": None,
    "tax_amount": None,
    "currency": None,
    "payment_terms": None,
    "reference_number": None,
    "raw_text_snapshot": None,  # First 2000 chars
    "source_file_name": None,
    "processed_timestamp": None,
}

# Required fields for validation
REQUIRED_FIELDS = [
    "invoice_number",
    "issue_date",
    "total_amount",
    "currency",
]

# Validation rules
VALIDATION_RULES = {
    "date_format": "YYYY-MM-DD",  # ISO format
    "valid_currencies": ["USD", "EUR", "GBP", "CAD", "AUD", "JPY", "CHF", "CNY", "INR", "BRL"],
    "min_confidence_score": 0.0,
    "max_confidence_score": 1.0,
}

# Validation statuses
VALIDATION_STATUS = {
    "PASSED": "PASSED",
    "PARTIAL": "PARTIAL",
    "FAILED": "FAILED",
}

# Logging configuration
LOG_CONFIG = {
    "processing_log": LOGS_DIR / "processing.log",
    "validation_errors_log": LOGS_DIR / "validation_errors.log",
    "extraction_errors_log": LOGS_DIR / "extraction_errors.log",
    "log_level": "INFO",
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "date_format": "%Y-%m-%d %H:%M:%S",
}

# Text extraction settings
TEXT_EXTRACTION = {
    "max_raw_text_length": 2000,  # Characters for snapshot
    "min_text_length": 10,  # Minimum text to consider valid
}

# Date patterns for extraction
DATE_PATTERNS = [
    r"\d{4}-\d{2}-\d{2}",  # YYYY-MM-DD
    r"\d{2}/\d{2}/\d{4}",  # MM/DD/YYYY
    r"\d{2}-\d{2}-\d{4}",  # MM-DD-YYYY
    r"\d{1,2}\s+\w{3,9}\s+\d{4}",  # DD Month YYYY
]

# Currency patterns
CURRENCY_PATTERNS = [
    r"\$\s*[\d,]+\.?\d*",  # USD format
    r"€\s*[\d,]+\.?\d*",  # EUR format
    r"£\s*[\d,]+\.?\d*",  # GBP format
    r"[\d,]+\.?\d*\s*(USD|EUR|GBP|CAD|AUD|JPY|CHF|CNY|INR|BRL)",
]

# Invoice number patterns
INVOICE_NUMBER_PATTERNS = [
    r"INV[-\s]?\d+",
    r"INVOICE[-\s]?#?\s*[\w\d-]+",
    r"#\s*[\w\d-]+",
]

# Amount patterns
AMOUNT_PATTERNS = [
    r"TOTAL[:\s]+[\$€£]?\s*[\d,]+\.?\d*",
    r"AMOUNT[:\s]+[\$€£]?\s*[\d,]+\.?\d*",
    r"[\$€£]\s*[\d,]+\.?\d*",
]

