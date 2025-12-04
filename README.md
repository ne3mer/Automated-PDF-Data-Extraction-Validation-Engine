# Automated PDF Data Extraction & Validation Engine

A production-grade Python system for processing large volumes of PDF documents, extracting structured business data, validating extracted fields, and exporting clean datasets to JSON and Excel formats.

## 🎯 Project Overview

This system automates the extraction of structured data from PDF documents (invoices, purchase orders, contracts, financial reports, etc.), validates the extracted information using rule-based logic, and generates comprehensive reports for auditing and quality assurance.

## ✨ Features

- **Batch Processing**: Process hundreds or thousands of PDF files automatically
- **Smart PDF Detection**: Automatically detects text-based vs scanned/image-based PDFs
- **Comprehensive Field Extraction**: Extracts 15+ structured fields including:
  - Invoice numbers, dates, amounts
  - Vendor/client names
  - Payment terms, reference numbers
  - Currency codes
- **Robust Validation**: Rule-based validation engine with:
  - Required field checks
  - Format validation (dates, currency, numbers)
  - Business logic validation (due date > issue date, total > tax)
  - Confidence scoring (0.0 to 1.0)
- **Multiple Output Formats**: 
  - Structured JSON datasets
  - Formatted Excel spreadsheets
  - Detailed validation reports
- **Error Handling**: Never crashes on single document errors, continues processing
- **Deduplication**: Detects and handles duplicate documents
- **Comprehensive Logging**: Separate logs for processing, validation errors, and extraction errors

## 🏗️ Architecture

```
PDF Input Folder
        ↓
PDF Loader
        ↓
Text Extraction Layer
        ↓
Field Extraction Engine (Regex + Layout Parsing)
        ↓
Data Normalization Layer
        ↓
Validation Engine
        ↓
Deduplication Engine
        ↓
Structured Data Builder
        ↓
JSON & Excel Exporter
        ↓
Logs + Validation Report
```

## 📁 Project Structure

```
pdf_data_engine/
│
├── input_pdfs/          # Place your PDF files here
├── output/
│   ├── json/           # JSON output files
│   ├── excel/          # Excel output files
│   └── reports/        # Validation reports
│
├── extractor/
│   ├── pdf_reader.py   # PDF reading with pdfplumber/PyMuPDF
│   ├── text_extractor.py  # Text extraction wrapper
│   └── field_extractor.py # Field extraction engine
│
├── validator/
│   ├── rules.py        # Main validation engine
│   ├── date_validator.py   # Date validation logic
│   └── numeric_validator.py # Numeric validation logic
│
├── normalizer/
│   └── cleaner.py      # Data cleaning and normalization
│
├── storage/
│   ├── json_writer.py  # JSON export functionality
│   ├── excel_writer.py # Excel export functionality
│   └── deduplicator.py # Duplicate detection
│
├── logs/               # Log files
├── config.py           # Configuration settings
├── main.py             # Main execution script
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## 🚀 Installation

### Prerequisites

- Python 3.12 or higher
- pip (Python package manager)

### Setup Steps

1. **Clone or download this repository**

2. **Create a virtual environment (recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   python3 -m pip install -r requirements.txt
   ```
   
   **Note**: Use `python3` and `python3 -m pip` to ensure you're using the correct Python version.

## 📖 Usage

### Basic Usage

1. **Place PDF files in the `input_pdfs/` directory**

2. **Run the extraction engine**
   ```bash
   python3 main.py
   ```

3. **Find results in the `output/` directory:**
   - `output/json/extracted_data.json` - All extracted data
   - `output/excel/extracted_data.xlsx` - Excel spreadsheet
   - `output/reports/validation_report.json` - Validation summary
   - `output/reports/validation_report.xlsx` - Validation report (Excel)

### Advanced Usage

**Custom input/output directories:**
```bash
python3 main.py --input /path/to/pdfs --output /path/to/output
```

**Dry-run mode (simulate without writing files):**
```bash
python3 main.py --dry-run
```

**Debug mode (verbose logging):**
```bash
python3 main.py --debug
```

**Skip deduplication:**
```bash
python3 main.py --no-deduplication
```

**Combine options:**
```bash
python3 main.py --input ./my_pdfs --output ./results --debug
```

## 📊 Extracted Fields

The system extracts the following structured fields from each PDF:

- `document_id` - Unique UUID for each document
- `document_type` - Detected type (invoice, purchase_order, contract, etc.)
- `vendor_name` - Vendor/supplier name
- `client_name` - Client/customer name
- `invoice_number` - Invoice or document number
- `contract_number` - Contract number (if available)
- `issue_date` - Issue date (ISO format: YYYY-MM-DD)
- `due_date` - Due date (ISO format: YYYY-MM-DD)
- `total_amount` - Total amount (numeric)
- `tax_amount` - Tax amount (numeric)
- `currency` - Currency code (USD, EUR, GBP, etc.)
- `payment_terms` - Payment terms
- `reference_number` - Reference/PO number
- `raw_text_snapshot` - First 2000 characters for audit
- `source_file_name` - Original PDF filename
- `processed_timestamp` - Processing timestamp

## ✅ Validation Rules

### Required Fields
- `invoice_number` must not be empty
- `issue_date` must be present
- `total_amount` must be present
- `currency` must be detected

### Format Validation
- Dates must match ISO format (YYYY-MM-DD)
- Currency must be a valid ISO code (USD, EUR, GBP, etc.)
- `total_amount` and `tax_amount` must be numeric

### Logical Validation
- `due_date` must be after `issue_date`
- `total_amount` must be greater than `tax_amount`
- Negative values are flagged

### Validation Status
Each document receives:
- **Validation Score**: 0.0 to 1.0 (confidence score)
- **Validation Status**: 
  - `PASSED` - All validations passed
  - `PARTIAL` - Some validations passed
  - `FAILED` - Critical validations failed

## 📤 Output Formats

### JSON Output

```json
{
  "document_id": "uuid",
  "document_type": "invoice",
  "vendor_name": "ABC Supplies Ltd",
  "client_name": "XYZ Corporation",
  "invoice_number": "INV-2025-1021",
  "issue_date": "2025-01-12",
  "due_date": "2025-02-12",
  "total_amount": 1842.75,
  "tax_amount": 312.75,
  "currency": "EUR",
  "payment_terms": "Net 30",
  "reference_number": "PO-88721",
  "validation_status": "PASSED",
  "validation_score": 0.94,
  "missing_fields": [],
  "source_file_name": "invoice_1021.pdf",
  "processed_at": "2025-01-14T10:22:11"
}
```

### Excel Output

The Excel file contains:
- All extracted fields as columns
- Each row represents one document
- Additional columns: `validation_status`, `validation_score`, `missing_fields`
- Formatted headers and auto-adjusted column widths

### Validation Report

The validation report includes:
- Total documents processed
- Successfully validated (PASSED)
- Partially validated (PARTIAL)
- Failed validation (FAILED)
- Documents with missing required fields
- Documents with date or numeric errors
- Average validation score
- Detailed error breakdown

## 🔧 Configuration

Edit `config.py` to customize:
- Field extraction patterns
- Validation rules
- Required fields
- Logging settings
- Output directories

## 📝 Logging

The system generates three types of log files in the `logs/` directory:

- `processing.log` - General processing information
- `validation_errors.log` - Validation failures
- `extraction_errors.log` - Extraction errors

## 🛠️ Error Handling

- The system never crashes due to a single document error
- Failed documents are logged and processing continues
- Each document's error status is included in the output
- Comprehensive error messages help identify issues

## 🧪 Testing

To test the system:

1. Place sample PDF files in `input_pdfs/`
2. Run with `--dry-run` first to verify setup
3. Run normally to process files
4. Check output files and logs

## 🔮 Future Enhancements

Potential future additions:
- OCR support using Tesseract for scanned PDFs
- REST API wrapper using FastAPI
- Web dashboard for document review
- Export to cloud storage (S3, Azure)
- AI-assisted field detection (LLM hybrid mode)
- Multi-schema document classification

## 📄 License

This project is provided as-is for portfolio and demonstration purposes.

## 👤 Author

Built as a portfolio-grade project demonstrating:
- Python Automation Engineering
- Document Processing Expertise
- Data Extraction & Validation
- Production-Ready Code Architecture

## 🤝 Contributing

This is a portfolio project. For questions or suggestions, please open an issue.

---

**Note**: This system is designed for text-based PDFs. For scanned/image-based PDFs, OCR capabilities would need to be added (see Future Enhancements).

