"""
Deduplication Module
Handles detection and removal of duplicate documents
"""
import logging
from typing import List, Dict, Any, Set, Tuple
from hashlib import md5

logger = logging.getLogger(__name__)


class Deduplicator:
    """Handles document deduplication based on key fields"""
    
    def __init__(self, key_fields: List[str] = None):
        """
        Initialize deduplicator
        
        Args:
            key_fields: List of field names to use for deduplication
        """
        self.key_fields = key_fields or [
            "invoice_number",
            "vendor_name",
            "total_amount",
            "issue_date"
        ]
    
    def generate_fingerprint(self, document: Dict[str, Any]) -> str:
        """
        Generate a fingerprint for a document based on key fields
        
        Args:
            document: Document data dictionary
            
        Returns:
            MD5 hash fingerprint
        """
        # Extract key field values
        key_values = []
        for field in self.key_fields:
            value = document.get(field)
            if value is not None:
                key_values.append(str(value).lower().strip())
        
        # Create fingerprint string
        fingerprint_str = "|".join(key_values)
        
        # Generate MD5 hash
        fingerprint = md5(fingerprint_str.encode('utf-8')).hexdigest()
        
        return fingerprint
    
    def find_duplicates(self, documents: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Find and separate duplicate documents
        
        Args:
            documents: List of document data dictionaries
            
        Returns:
            Tuple of (unique_documents, duplicate_documents)
        """
        seen_fingerprints: Set[str] = set()
        unique_docs: List[Dict[str, Any]] = []
        duplicate_docs: List[Dict[str, Any]] = []
        
        for doc in documents:
            fingerprint = self.generate_fingerprint(doc)
            
            if fingerprint in seen_fingerprints:
                duplicate_docs.append(doc)
                logger.debug(f"Found duplicate document: {doc.get('source_file_name', 'unknown')}")
            else:
                seen_fingerprints.add(fingerprint)
                unique_docs.append(doc)
        
        logger.info(
            f"Deduplication complete: {len(unique_docs)} unique, "
            f"{len(duplicate_docs)} duplicates found"
        )
        
        return (unique_docs, duplicate_docs)
    
    def remove_duplicates(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate documents, keeping the first occurrence
        
        Args:
            documents: List of document data dictionaries
            
        Returns:
            List of unique documents
        """
        unique_docs, _ = self.find_duplicates(documents)
        return unique_docs
    
    def mark_duplicates(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Mark duplicate documents with a flag instead of removing them
        
        Args:
            documents: List of document data dictionaries
            
        Returns:
            List of documents with 'is_duplicate' flag added
        """
        seen_fingerprints: Set[str] = set()
        marked_docs: List[Dict[str, Any]] = []
        
        for doc in documents:
            fingerprint = self.generate_fingerprint(doc)
            
            if fingerprint in seen_fingerprints:
                doc["is_duplicate"] = True
                logger.debug(f"Marked duplicate document: {doc.get('source_file_name', 'unknown')}")
            else:
                seen_fingerprints.add(fingerprint)
                doc["is_duplicate"] = False
            
            marked_docs.append(doc)
        
        return marked_docs

