"""
PDF Reader Module
Handles loading and reading PDF files, detecting text-based vs scanned PDFs
"""
import logging
from pathlib import Path
from typing import Optional, Tuple
import pdfplumber
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)


class PDFReader:
    """Handles PDF file reading and text extraction"""
    
    def __init__(self, pdf_path: Path):
        """
        Initialize PDF reader
        
        Args:
            pdf_path: Path to the PDF file
        """
        self.pdf_path = pdf_path
        self.is_text_based: Optional[bool] = None
        self.text_content: Optional[str] = None
        self.page_count: int = 0
        
    def detect_pdf_type(self) -> bool:
        """
        Detect if PDF is text-based or scanned image-based
        
        Returns:
            True if text-based, False if scanned/image-based
        """
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                total_text_length = 0
                self.page_count = len(pdf.pages)
                
                # Check first few pages for text content
                pages_to_check = min(3, self.page_count)
                for i in range(pages_to_check):
                    page = pdf.pages[i]
                    text = page.extract_text() or ""
                    total_text_length += len(text.strip())
                
                # If we have substantial text, it's text-based
                # Threshold: at least 50 characters per page on average
                threshold = 50 * pages_to_check
                self.is_text_based = total_text_length >= threshold
                
                logger.info(
                    f"PDF type detection for {self.pdf_path.name}: "
                    f"{'Text-based' if self.is_text_based else 'Scanned/Image-based'} "
                    f"(text length: {total_text_length})"
                )
                
                return self.is_text_based
                
        except Exception as e:
            logger.error(f"Error detecting PDF type for {self.pdf_path.name}: {str(e)}")
            # Default to text-based and let extraction handle errors
            self.is_text_based = True
            return True
    
    def extract_text_pdfplumber(self) -> str:
        """
        Extract text using pdfplumber (best for text-based PDFs)
        
        Returns:
            Extracted text content
        """
        full_text = []
        
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                self.page_count = len(pdf.pages)
                
                for page_num, page in enumerate(pdf.pages, 1):
                    try:
                        text = page.extract_text()
                        if text:
                            full_text.append(text)
                        logger.debug(f"Extracted text from page {page_num}/{self.page_count}")
                    except Exception as e:
                        logger.warning(f"Error extracting text from page {page_num}: {str(e)}")
                        continue
                        
        except Exception as e:
            logger.error(f"Error reading PDF with pdfplumber: {str(e)}")
            raise
            
        return "\n\n".join(full_text)
    
    def extract_text_pymupdf(self) -> str:
        """
        Extract text using PyMuPDF (fallback method)
        
        Returns:
            Extracted text content
        """
        full_text = []
        
        try:
            doc = fitz.open(self.pdf_path)
            self.page_count = len(doc)
            
            for page_num in range(self.page_count):
                try:
                    page = doc[page_num]
                    text = page.get_text()
                    if text:
                        full_text.append(text)
                    logger.debug(f"Extracted text from page {page_num + 1}/{self.page_count} using PyMuPDF")
                except Exception as e:
                    logger.warning(f"Error extracting text from page {page_num + 1}: {str(e)}")
                    continue
                    
            doc.close()
            
        except Exception as e:
            logger.error(f"Error reading PDF with PyMuPDF: {str(e)}")
            raise
            
        return "\n\n".join(full_text)
    
    def extract_all_text(self) -> str:
        """
        Extract all text from PDF, trying multiple methods
        
        Returns:
            Complete extracted text
        """
        # First, detect PDF type
        self.detect_pdf_type()
        
        # Try pdfplumber first (better for structured text)
        try:
            self.text_content = self.extract_text_pdfplumber()
            if self.text_content and len(self.text_content.strip()) > 10:
                logger.info(f"Successfully extracted text using pdfplumber ({len(self.text_content)} chars)")
                return self.text_content
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {str(e)}, trying PyMuPDF...")
        
        # Fallback to PyMuPDF
        try:
            self.text_content = self.extract_text_pymupdf()
            if self.text_content and len(self.text_content.strip()) > 10:
                logger.info(f"Successfully extracted text using PyMuPDF ({len(self.text_content)} chars)")
                return self.text_content
        except Exception as e:
            logger.error(f"PyMuPDF extraction also failed: {str(e)}")
            raise
        
        # If we get here, extraction failed
        logger.warning(f"No text extracted from {self.pdf_path.name}")
        return ""
    
    def get_text_snapshot(self, max_length: int = 2000) -> str:
        """
        Get a snapshot of the extracted text (first N characters)
        
        Args:
            max_length: Maximum length of snapshot
            
        Returns:
            Text snapshot
        """
        if not self.text_content:
            self.extract_all_text()
        
        if not self.text_content:
            return ""
        
        snapshot = self.text_content[:max_length]
        if len(self.text_content) > max_length:
            snapshot += "..."
        
        return snapshot

