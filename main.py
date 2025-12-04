"""
Main Execution Script
CLI interface for PDF Data Extraction & Validation Engine
"""
import argparse
import logging
import sys
from pathlib import Path
from datetime import datetime
from uuid import uuid4
from typing import List, Dict, Any

# Import project modules
import config
from extractor.text_extractor import TextExtractor
from extractor.field_extractor import FieldExtractor
from normalizer.cleaner import DataCleaner
from validator.rules import ValidationEngine
from storage.json_writer import JSONWriter
from storage.excel_writer import ExcelWriter
from storage.deduplicator import Deduplicator


def setup_logging(log_level: str = "INFO", debug: bool = False):
    """Setup logging configuration"""
    if debug:
        log_level = "DEBUG"
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=config.LOG_CONFIG["log_format"],
        datefmt=config.LOG_CONFIG["date_format"],
        handlers=[
            logging.FileHandler(config.LOG_CONFIG["processing_log"]),
            logging.StreamHandler(sys.stdout)
        ]
    )


def process_single_pdf(pdf_path: Path, dry_run: bool = False) -> Dict[str, Any]:
    """
    Process a single PDF file
    
    Args:
        pdf_path: Path to PDF file
        dry_run: If True, only simulate processing
        
    Returns:
        Dictionary with extracted and validated data
    """
    logger = logging.getLogger(__name__)
    
    if dry_run:
        logger.info(f"[DRY RUN] Would process: {pdf_path.name}")
        return {}
    
    try:
        logger.info(f"Processing PDF: {pdf_path.name}")
        
        # Step 1: Extract text
        text_extractor = TextExtractor(pdf_path)
        extracted_text = text_extractor.extract()
        
        if not extracted_text:
            logger.warning(f"No text extracted from {pdf_path.name}")
            return {
                "document_id": str(uuid4()),
                "source_file_name": pdf_path.name,
                "processed_timestamp": datetime.now().isoformat(),
                "validation_status": config.VALIDATION_STATUS["FAILED"],
                "validation_score": 0.0,
                "error": "No text extracted from PDF"
            }
        
        # Step 2: Extract fields
        field_extractor = FieldExtractor(text_extractor)
        extracted_fields = field_extractor.extract_all_fields()
        
        # Step 3: Clean and normalize
        cleaner = DataCleaner()
        cleaned_fields = cleaner.clean_all_fields(extracted_fields)
        
        # Step 4: Validate
        validator = ValidationEngine()
        validation_results = validator.validate_all(cleaned_fields)
        
        # Step 5: Combine all data
        document_data = {
            "document_id": str(uuid4()),
            "source_file_name": pdf_path.name,
            "processed_timestamp": datetime.now().isoformat(),
            **cleaned_fields,
            **validation_results
        }
        
        logger.info(
            f"Successfully processed {pdf_path.name}: "
            f"Status={validation_results['validation_status']}, "
            f"Score={validation_results['validation_score']}"
        )
        
        return document_data
        
    except Exception as e:
        error_logger = logging.getLogger("extraction_errors")
        error_logger.error(f"Error processing {pdf_path.name}: {str(e)}", exc_info=True)
        
        return {
            "document_id": str(uuid4()),
            "source_file_name": pdf_path.name,
            "processed_timestamp": datetime.now().isoformat(),
            "validation_status": config.VALIDATION_STATUS["FAILED"],
            "validation_score": 0.0,
            "error": str(e)
        }


def generate_validation_report(documents: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate validation report from processed documents
    
    Args:
        documents: List of processed document dictionaries
        
    Returns:
        Validation report dictionary
    """
    total = len(documents)
    passed = sum(1 for d in documents if d.get("validation_status") == config.VALIDATION_STATUS["PASSED"])
    partial = sum(1 for d in documents if d.get("validation_status") == config.VALIDATION_STATUS["PARTIAL"])
    failed = sum(1 for d in documents if d.get("validation_status") == config.VALIDATION_STATUS["FAILED"])
    
    missing_fields_count = sum(1 for d in documents if d.get("missing_fields") and len(d.get("missing_fields", [])) > 0)
    
    date_errors_count = sum(
        1 for d in documents
        if any("date" in str(err).lower() for err in d.get("validation_errors", []))
    )
    
    numeric_errors_count = sum(
        1 for d in documents
        if any("amount" in str(err).lower() or "numeric" in str(err).lower()
               for err in d.get("validation_errors", []))
    )
    
    scores = [d.get("validation_score", 0.0) for d in documents if d.get("validation_score") is not None]
    average_score = sum(scores) / len(scores) if scores else 0.0
    
    # Collect error details
    error_details = []
    for doc in documents:
        if doc.get("validation_errors"):
            error_details.append({
                "source_file_name": doc.get("source_file_name", "unknown"),
                "document_id": doc.get("document_id", "unknown"),
                "errors": doc.get("validation_errors", []),
                "missing_fields": doc.get("missing_fields", [])
            })
    
    report = {
        "total_processed": total,
        "passed": passed,
        "partial": partial,
        "failed": failed,
        "missing_fields_count": missing_fields_count,
        "date_errors_count": date_errors_count,
        "numeric_errors_count": numeric_errors_count,
        "average_score": average_score,
        "error_details": error_details,
        "generated_at": datetime.now().isoformat()
    }
    
    return report


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="PDF Data Extraction & Validation Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--input",
        type=str,
        default="./input_pdfs",
        help="Input directory containing PDF files (default: ./input_pdfs)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        default="./output",
        help="Output directory for results (default: ./output)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run mode - simulate processing without writing files"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--no-deduplication",
        action="store_true",
        help="Skip duplicate detection"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(debug=args.debug)
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 60)
    logger.info("PDF Data Extraction & Validation Engine")
    logger.info("=" * 60)
    
    # Setup paths
    input_dir = Path(args.input)
    if not input_dir.exists():
        logger.error(f"Input directory does not exist: {input_dir}")
        sys.exit(1)
    
    # Find all PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"No PDF files found in {input_dir}")
        sys.exit(0)
    
    logger.info(f"Found {len(pdf_files)} PDF file(s) to process")
    
    # Process each PDF
    processed_documents = []
    for pdf_file in pdf_files:
        document_data = process_single_pdf(pdf_file, dry_run=args.dry_run)
        if document_data:
            processed_documents.append(document_data)
    
    if args.dry_run:
        logger.info(f"[DRY RUN] Would process {len(processed_documents)} documents")
        return
    
    if not processed_documents:
        logger.warning("No documents were successfully processed")
        return
    
    logger.info(f"Successfully processed {len(processed_documents)} document(s)")
    
    # Deduplication
    if not args.no_deduplication:
        logger.info("Running deduplication...")
        deduplicator = Deduplicator()
        unique_documents, duplicates = deduplicator.find_duplicates(processed_documents)
        logger.info(f"Found {len(duplicates)} duplicate(s), keeping {len(unique_documents)} unique document(s)")
        processed_documents = unique_documents
    
    # Generate validation report
    logger.info("Generating validation report...")
    validation_report = generate_validation_report(processed_documents)
    
    # Write outputs
    logger.info("Writing output files...")
    
    # JSON output
    json_writer = JSONWriter()
    json_writer.write_batch(processed_documents, "extracted_data.json")
    json_writer.write_report(validation_report, "validation_report.json")
    
    # Excel output
    excel_writer = ExcelWriter()
    excel_writer.write_documents(processed_documents, "extracted_data.xlsx")
    excel_writer.write_report(validation_report, "validation_report.xlsx")
    
    # Print summary
    logger.info("=" * 60)
    logger.info("PROCESSING COMPLETE")
    logger.info("=" * 60)
    logger.info(f"Total processed: {validation_report['total_processed']}")
    logger.info(f"Passed: {validation_report['passed']}")
    logger.info(f"Partial: {validation_report['partial']}")
    logger.info(f"Failed: {validation_report['failed']}")
    logger.info(f"Average validation score: {validation_report['average_score']:.2f}")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()

