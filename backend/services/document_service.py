# services/document_service.py
# Business logic for document processing
# Connects AI classification directly to database persistence

import uuid
from sqlalchemy.orm import Session

from models import (
    Company,
    Document,
    Invoice,
    FinancialStatement,
    TaxDocument,
    BankStatement,
    Anomaly
)
from services.ai_service import classify_document, detect_anomalies
from core.models import DocumentClassification


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extracts raw text from a PDF file.
    Uses pdfplumber — reliable for text-based PDFs.
    For scanned/image PDFs, OCR would be needed (future improvement).
    """
    import pdfplumber
    import io

    text = ""
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def process_document(
    document_id: str,
    file_bytes: bytes,
    db: Session
) -> None:
    """
    Full document processing pipeline — runs in background after upload.

    Steps:
    1. Extract text from PDF
    2. Classify document with AI
    3. Save classification to correct child table
    4. Detect anomalies and save them
    5. Update processing status

    This function is called by the background task in the documents router.
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        return

    try:
        # Step 1 — Mark as processing so frontend knows work is in progress
        document.processing_status = "processing"
        db.commit()

        # Step 2 — Extract raw text from PDF
        extracted_text = extract_text_from_pdf(file_bytes)
        document.extracted_text = extracted_text
        db.commit()

        # Step 3 — Classify with AI
        classification = classify_document(extracted_text)
        document.category = classification.category
        db.commit()

        # Step 4 — Save to the correct child table based on classification
        _save_to_child_table(db, document, classification)

        # Step 5 — Detect and save anomalies
        _detect_and_save_anomalies(db, document)

        # Step 6 — Mark as complete
        document.processing_status = "processed"
        db.commit()

    except Exception as e:
        # If anything fails, mark as failed so the user knows
        document.processing_status = "failed"
        db.commit()
        print(f"Document processing failed for {document_id}: {e}")


def _save_to_child_table(
    db: Session,
    document: Document,
    classification: DocumentClassification
) -> None:
    """
    Routes the AI classification result to the correct child table.
    Each document type has its own table with specific fields.
    """
    if classification.category == "audit":

        if classification.type == "invoice":
            invoice = Invoice(
                id=str(uuid.uuid4()),
                document_id=document.id,
                vendor=classification.vendor,
                amount=classification.amount,
                invoice_number=classification.invoice_number,
                direction=classification.direction,
                is_paid=False
            )
            db.add(invoice)

        elif classification.type == "bank_statement":
            statement = BankStatement(
                id=str(uuid.uuid4()),
                document_id=document.id,
                period=classification.period,
            )
            db.add(statement)

        # contract, receipt, payslip — stored as document only, no child table needed

    elif classification.category == "financial_statement":
        statement = FinancialStatement(
            id=str(uuid.uuid4()),
            document_id=document.id,
            type=classification.type,    # PnL | balance_sheet | cash_flow | budget
            period=classification.period,
        )
        db.add(statement)

    elif classification.category == "tax":
        tax = TaxDocument(
            id=str(uuid.uuid4()),
            document_id=document.id,
            type=classification.type,    # TVA | IS | CNSS | IR
            period=classification.period,
            amount_due=classification.amount,
            status="unpaid"
        )
        db.add(tax)

    db.commit()


def _detect_and_save_anomalies(
    db: Session,
    document: Document
) -> None:
    """
    Runs AI anomaly detection on the document and saves results.
    Anomalies are things an auditor would flag — duplicates,
    unusually high amounts, overdue payments etc.
    """
    if not document.extracted_text:
        return

    # Get company name for context in the AI prompt
    company = db.query(Company).filter(
        Company.id == document.company_id
    ).first()
    company_name = company.name if company else "Unknown Company"

    # Run anomaly detection
    anomalies = detect_anomalies(
        documents_context=document.extracted_text,
        company_name=company_name
    )

    # Save each anomaly to the database
    for anomaly_item in anomalies:
        anomaly = Anomaly(
            id=str(uuid.uuid4()),
            company_id=document.company_id,
            document_id=document.id,
            description=anomaly_item.description,
            severity=anomaly_item.severity,
            resolved=False
        )
        db.add(anomaly)

    db.commit()