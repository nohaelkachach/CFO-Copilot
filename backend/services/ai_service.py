# services/ai_service.py
# AI service using LangChain + Gemini Flash
# Each function builds a chain: prompt | llm | parser

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from core.llm import get_llm
from core.models import DocumentClassification, AnomalyItem
from core.prompts import (
    CLASSIFY_DOCUMENT_PROMPT,
    DETECT_ANOMALIES_PROMPT,
    ANSWER_QUESTION_PROMPT
)


def classify_document(extracted_text: str) -> DocumentClassification:
    try:
        llm = get_llm()  # moved inside try
        parser = JsonOutputParser(pydantic_object=DocumentClassification)

        prompt = PromptTemplate(
            template=CLASSIFY_DOCUMENT_PROMPT,
            input_variables=["text"],
            partial_variables={
                "format_instructions": parser.get_format_instructions()
            }
        )

        chain = prompt | llm | parser
        result = chain.invoke({"text": extracted_text[:3000]})
        return DocumentClassification.model_validate(result)

    except Exception:
        return DocumentClassification(
            category="audit",
            type="other",
            confidence=0.0
        )


def answer_financial_question(question: str, context: str) -> str:
    try:
        llm = get_llm()  # moved inside try
        parser = StrOutputParser()

        prompt = PromptTemplate(
            template=ANSWER_QUESTION_PROMPT,
            input_variables=["question", "context"]
        )

        chain = prompt | llm | parser
        return chain.invoke({"question": question, "context": context})

    except Exception:
        return "An error occurred while processing your question. Please try again."


def detect_anomalies(documents_context: str, company_name: str) -> list[AnomalyItem]:
    try:
        llm = get_llm()  # moved inside try
        parser = JsonOutputParser()

        prompt = PromptTemplate(
            template=DETECT_ANOMALIES_PROMPT,
            input_variables=["company_name", "documents"],
            partial_variables={
                "format_instructions": parser.get_format_instructions()
            }
        )

        chain = prompt | llm | parser
        result = chain.invoke({
            "company_name": company_name,
            "documents": documents_context
        })
        return [AnomalyItem.model_validate(item) for item in result]

    except Exception:
        return []