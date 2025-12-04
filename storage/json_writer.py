"""
JSON Writer Module
Handles writing extracted data to JSON files
"""
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import config

logger = logging.getLogger(__name__)


class JSONWriter:
    """Handles writing data to JSON format"""
    
    def __init__(self, output_dir: Path = None):
        """
        Initialize JSON writer
        
        Args:
            output_dir: Output directory for JSON files
        """
        self.output_dir = output_dir or config.JSON_OUTPUT_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def write_document(self, document_data: Dict[str, Any], filename: str = None) -> Path:
        """
        Write a single document to JSON file
        
        Args:
            document_data: Document data dictionary
            filename: Optional custom filename (without extension)
            
        Returns:
            Path to written JSON file
        """
        if filename is None:
            doc_id = document_data.get("document_id", "unknown")
            filename = f"document_{doc_id}.json"
        
        if not filename.endswith(".json"):
            filename += ".json"
        
        output_path = self.output_dir / filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(document_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Wrote JSON file: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error writing JSON file {output_path}: {str(e)}")
            raise
    
    def write_batch(self, documents: List[Dict[str, Any]], filename: str = "batch_output.json") -> Path:
        """
        Write multiple documents to a single JSON file
        
        Args:
            documents: List of document data dictionaries
            filename: Output filename (without extension)
            
        Returns:
            Path to written JSON file
        """
        if not filename.endswith(".json"):
            filename += ".json"
        
        output_path = self.output_dir / filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(documents, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Wrote batch JSON file with {len(documents)} documents: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error writing batch JSON file {output_path}: {str(e)}")
            raise
    
    def write_report(self, report_data: Dict[str, Any], filename: str = "validation_report.json") -> Path:
        """
        Write validation report to JSON
        
        Args:
            report_data: Report data dictionary
            filename: Output filename
            
        Returns:
            Path to written JSON file
        """
        if not filename.endswith(".json"):
            filename += ".json"
        
        output_path = config.REPORTS_OUTPUT_DIR / filename
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"Wrote validation report: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error writing validation report {output_path}: {str(e)}")
            raise

