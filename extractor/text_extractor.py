"""
Text Extractor Module
Wrapper for PDF text extraction with error handling
"""
import logging
from pathlib import Path
from typing import Optional
from .pdf_reader import PDFReader

logger = logging.getLogger(__name__)


class TextExtractor:
    """Handles text extraction from PDF files with error handling"""
    
    def __init__(self, pdf_path: Path):
        """
        Initialize text extractor
        
        Args:
            pdf_path: Path to the PDF file
        """
        self.pdf_path = pdf_path
        self.reader: Optional[PDFReader] = None
        self.extracted_text: Optional[str] = None
        self.extraction_successful: bool = False
        self.error_message: Optional[str] = None
    
    def extract(self) -> str:
        """
        Extract text from PDF
        
        Returns:
            Extracted text, empty string if extraction fails
        """
        try:
            if not self.pdf_path.exists():
                raise FileNotFoundError(f"PDF file not found: {self.pdf_path}")
            
            if not self.pdf_path.suffix.lower() == '.pdf':
                raise ValueError(f"File is not a PDF: {self.pdf_path}")
            
            self.reader = PDFReader(self.pdf_path)
            self.extracted_text = self.reader.extract_all_text()
            self.extraction_successful = True
            
            if not self.extracted_text or len(self.extracted_text.strip()) < 10:
                logger.warning(f"Extracted text is too short for {self.pdf_path.name}")
                self.extracted_text = ""
                self.extraction_successful = False
                self.error_message = "Insufficient text extracted (possibly scanned PDF)"
            
            return self.extracted_text
            
        except Exception as e:
            error_msg = f"Text extraction failed for {self.pdf_path.name}: {str(e)}"
            logger.error(error_msg)
            self.error_message = str(e)
            self.extraction_successful = False
            self.extracted_text = ""
            return ""
    
    def get_text_snapshot(self, max_length: int = 2000) -> str:
        """
        Get text snapshot for audit purposes
        
        Args:
            max_length: Maximum length of snapshot
            
        Returns:
            Text snapshot
        """
        if not self.extracted_text:
            self.extract()
        
        if not self.reader:
            return ""
        
        return self.reader.get_text_snapshot(max_length)
    
    def is_text_based(self) -> Optional[bool]:
        """
        Check if PDF is text-based
        
        Returns:
            True if text-based, False if scanned, None if not yet determined
        """
        if not self.reader:
            self.extract()
        
        if self.reader:
            return self.reader.is_text_based
        
        return None

