# services/document_service.py
# Business logic for document processing
# Connects AI classification directly to database persistence

import uuid
import pdfplumber
import io
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
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        print(f"ERROR: Document {document_id} not found")
        return

    try:
        # Step 1 — Mark as processing
        document.processing_status = "processing"
        db.commit()
        print(f"STEP 1: Processing started for {document.filename}")

        # Step 2 — Extract text from PDF
        extracted_text = extract_text_from_pdf(file_bytes)
        print(f"STEP 2: Extracted {len(extracted_text)} characters")
        document.extracted_text = extracted_text
        db.commit()

        # Step 3 — Classify with AI
        classification = classify_document(extracted_text)
        print(f"STEP 3: Classification — category={classification.category} | type={classification.type} | revenue={classification.revenue} | expenses={classification.expenses} | net_profit={classification.net_profit}")
        document.category = classification.category
        db.commit()

        # Step 4 — Save to correct child table
        _save_to_child_table(db, document, classification)
        print(f"STEP 4: Saved to child table")

        # Step 5 — Detect and save anomalies
        _detect_and_save_anomalies(db, document)
        print(f"STEP 5: Anomaly detection complete")

        # Step 6 — Mark as complete
        document.processing_status = "processed"
        db.commit()
        print(f"STEP 6: Done — {document.filename} processed successfully")

    except Exception as e:
        import traceback
        print(f"PROCESSING FAILED: {e}")
        print(traceback.format_exc())
        document.processing_status = "failed"
        db.commit()


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
               closing_balance=classification.closing_balance,
    )
            db.add(statement)

        # contract, receipt, payslip — stored as document only

    elif classification.category == "financial_statement":
        # Single block with ALL financial fields
        statement = FinancialStatement(
            id=str(uuid.uuid4()),
            document_id=document.id,
            type=classification.type,
            period=classification.period,
            revenue=classification.revenue,
            expenses=classification.expenses,
            net_profit=classification.net_profit,
            total_assets=classification.total_assets,
            total_liabilities=classification.total_liabilities,
        )
        db.add(statement)

    elif classification.category == "tax":
        tax = TaxDocument(
            id=str(uuid.uuid4()),
            document_id=document.id,
            type=classification.type,
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

    company = db.query(Company).filter(
        Company.id == document.company_id
    ).first()
    company_name = company.name if company else "Unknown Company"

    anomalies = detect_anomalies(
        documents_context=document.extracted_text,
        company_name=company_name
    )

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