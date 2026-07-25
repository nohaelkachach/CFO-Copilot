# tests/test_document_service.py
import pytest
from unittest.mock import patch, MagicMock
from services.document_service import (
    extract_text_from_pdf,
    process_document,
    _save_to_child_table,
    _detect_and_save_anomalies
)
from core.models import DocumentClassification, AnomalyItem


def test_extract_text_from_pdf_returns_string():
    """
    Confirms extract_text_from_pdf returns a string.
    Mocks pdfplumber.open to avoid needing a real PDF file.
    """
    with patch("pdfplumber.open") as mock_open:
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Invoice from Atlas SARL"
        mock_open.return_value.__enter__.return_value.pages = [mock_page]

        result = extract_text_from_pdf(b"fake pdf bytes")

        assert isinstance(result, str)
        assert "Atlas SARL" in result


def test_process_document_marks_failed_on_error(db):
    """
    If AI processing fails, document status must be 'failed'.
    Never leave a document stuck in 'processing' forever.
    """
    from models import Document, Company
    import uuid

    company = Company(id=str(uuid.uuid4()), name="Test Company")
    db.add(company)
    db.commit()

    document = Document(
        id=str(uuid.uuid4()),
        company_id=company.id,
        filename="test.pdf",
        category="unknown",
        processing_status="pending"
    )
    db.add(document)
    db.commit()

    with patch("services.document_service.extract_text_from_pdf") as mock_extract:
        mock_extract.side_effect = Exception("PDF corrupted")

        process_document(
            document_id=document.id,
            file_bytes=b"fake bytes",
            db=db
        )

    db.refresh(document)
    assert document.processing_status == "failed"


def test_process_document_marks_processed_on_success(db):
    """
    If processing succeeds, document status must be 'processed'.
    """
    from models import Document, Company
    import uuid

    company = Company(id=str(uuid.uuid4()), name="Test Company")
    db.add(company)
    db.commit()

    document = Document(
        id=str(uuid.uuid4()),
        company_id=company.id,
        filename="invoice.pdf",
        category="unknown",
        processing_status="pending"
    )
    db.add(document)
    db.commit()

    with patch("services.document_service.extract_text_from_pdf") as mock_extract, \
         patch("services.document_service.classify_document") as mock_classify, \
         patch("services.document_service.detect_anomalies") as mock_anomalies:

        mock_extract.return_value = "Invoice text here"
        mock_classify.return_value = DocumentClassification(
            category="audit",
            type="invoice",
            vendor="Atlas SARL",
            amount=5000.0,
            confidence=0.95
        )
        mock_anomalies.return_value = []

        process_document(
            document_id=document.id,
            file_bytes=b"fake bytes",
            db=db
        )

    db.refresh(document)
    assert document.processing_status == "processed"
    assert document.extracted_text == "Invoice text here"
    assert document.category == "audit"


def test_save_to_child_table_creates_invoice(db):
    """
    When AI classifies as invoice, an Invoice record must be created.
    """
    from models import Document, Company, Invoice
    import uuid

    company = Company(id=str(uuid.uuid4()), name="Test Company")
    db.add(company)
    db.commit()

    document = Document(
        id=str(uuid.uuid4()),
        company_id=company.id,
        filename="invoice.pdf",
        category="audit",
        processing_status="processed"
    )
    db.add(document)
    db.commit()

    classification = DocumentClassification(
        category="audit",
        type="invoice",
        vendor="Atlas SARL",
        amount=5000.0,
        direction="received",
        invoice_number="FAC-001",
        confidence=0.95
    )

    _save_to_child_table(db, document, classification)

    invoice = db.query(Invoice).filter(
        Invoice.document_id == document.id
    ).first()

    assert invoice is not None
    assert invoice.vendor == "Atlas SARL"
    assert invoice.amount == 5000.0
    assert invoice.is_paid == False


def test_detect_and_save_anomalies(db):
    """
    Detected anomalies must be saved to the database.
    """
    from models import Document, Company, Anomaly
    import uuid

    company = Company(id=str(uuid.uuid4()), name="Test Company")
    db.add(company)
    db.commit()

    document = Document(
        id=str(uuid.uuid4()),
        company_id=company.id,
        filename="invoice.pdf",
        category="audit",
        processing_status="processed",
        extracted_text="Invoice content here"
    )
    db.add(document)
    db.commit()

    with patch("services.document_service.detect_anomalies") as mock_detect:
        mock_detect.return_value = [
            AnomalyItem(
                description="Invoice amount is 40% above average",
                severity="high"
            )
        ]

        _detect_and_save_anomalies(db, document)

    anomalies = db.query(Anomaly).filter(
        Anomaly.document_id == document.id
    ).all()

    assert len(anomalies) == 1
    assert anomalies[0].severity == "high"
    assert "40%" in anomalies[0].description