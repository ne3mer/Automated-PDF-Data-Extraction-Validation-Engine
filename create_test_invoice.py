"""
Create a test invoice PDF for testing the extraction engine
"""
import fitz  # PyMuPDF
from datetime import datetime, timedelta

def create_test_invoice():
    """Create a test invoice PDF with all required fields"""
    
    # Create a new PDF document
    doc = fitz.open()
    page = doc.new_page()
    
    # Set up text
    text_content = """
INVOICE

Invoice Number: INV-2025-001
Issue Date: 2025-01-15
Due Date: 2025-02-15

From:
ABC Supplies Ltd
123 Business Street
New York, NY 10001
United States

Bill To:
XYZ Corporation
456 Corporate Avenue
Los Angeles, CA 90001
United States

Description                    Amount
----------------------------------------
Product A - Quantity: 10       $500.00
Product B - Quantity: 5        $250.00
Service Fee                    $100.00
----------------------------------------
Subtotal:                      $850.00
Tax (VAT):                     $102.00
----------------------------------------
TOTAL:                         $952.00

Payment Terms: Net 30
Reference Number: PO-12345
Currency: USD

Thank you for your business!
"""
    
    # Insert text
    rect = fitz.Rect(50, 50, 550, 750)
    page.insert_text(rect.tl, text_content, fontsize=11)
    
    # Save the PDF
    output_path = "input_pdfs/test_invoice.pdf"
    doc.save(output_path)
    doc.close()
    
    print(f"✓ Test invoice PDF created: {output_path}")
    print("\nInvoice contains:")
    print("  - Invoice Number: INV-2025-001")
    print("  - Issue Date: 2025-01-15")
    print("  - Due Date: 2025-02-15")
    print("  - Vendor: ABC Supplies Ltd")
    print("  - Client: XYZ Corporation")
    print("  - Total Amount: $952.00")
    print("  - Tax Amount: $102.00")
    print("  - Currency: USD")
    print("  - Payment Terms: Net 30")
    print("  - Reference: PO-12345")

if __name__ == "__main__":
    create_test_invoice()

