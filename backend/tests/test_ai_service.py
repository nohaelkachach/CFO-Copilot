# tests/test_ai_service.py
from unittest.mock import patch, MagicMock
from services.ai_service import classify_document, answer_financial_question
from core.models import DocumentClassification

def test_classify_document_returns_classification():
    """
    Tests that classify_document returns a DocumentClassification object.
    Mocks the LangChain chain so no real API call is made.
    """
    mock_result = {
        "category": "audit",
        "type": "invoice",
        "period": "2026-06",
        "vendor": "Atlas SARL",
        "amount": 5000.0,
        "currency": "MAD",
        "date": "2026-06-30",
        "due_date": None,
        "invoice_number": "FAC-001",
        "direction": "received",
        "confidence": 0.95
    }

    with patch("services.ai_service.get_llm") as mock_llm:
        # Mock the entire chain so it returns our fake result
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = mock_result
        mock_llm.return_value = MagicMock()

        with patch("services.ai_service.PromptTemplate") as mock_prompt:
            mock_prompt.return_value.__or__ = MagicMock(
                return_value=MagicMock(
                    __or__=MagicMock(return_value=mock_chain)
                )
            )

            result = classify_document("Sample invoice text")
            assert isinstance(result, DocumentClassification)


def test_classify_document_handles_failure_gracefully():
    """
    Tests that classify_document returns safe defaults when AI fails.
    This is the most important test — ensures the app never crashes
    even when the AI returns garbage or the API is down.
    """
    with patch("services.ai_service.get_llm") as mock_llm:
        mock_llm.side_effect = Exception("API unavailable")

        result = classify_document("some text")

        # Should return defaults, not crash
        assert result.category == "audit"
        assert result.type == "other"
        assert result.confidence == 0.0


def test_answer_financial_question_handles_failure():
    """
    Tests that Q&A returns a friendly message when AI fails.
    """
    with patch("services.ai_service.get_llm") as mock_llm:
        mock_llm.side_effect = Exception("API unavailable")

        result = answer_financial_question(
            question="What were my expenses?",
            context="Some document text"
        )

        assert "error" in result.lower()