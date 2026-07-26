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


# services/ai_service.py

def classify_document(extracted_text: str) -> DocumentClassification:
    try:
        llm = get_llm()
        # Use StrOutputParser instead of JsonOutputParser
        # JsonOutputParser's format_instructions confuse the model
        parser = StrOutputParser()

        prompt = PromptTemplate(
            template=CLASSIFY_DOCUMENT_PROMPT,
            input_variables=["text"],
            partial_variables={"format_instructions": ""}  # empty — we handle parsing ourselves
        )

        chain = prompt | llm | parser
        result_text = chain.invoke({"text": extracted_text[:6000]})

        # Clean up response
        result_text = result_text.strip()
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
            result_text = result_text.strip()

        import json
        data = json.loads(result_text)

        print(f">>>>> CATEGORY: {data.get('category')} | TYPE: {data.get('type')} | CONFIDENCE: {data.get('confidence')}")

        return DocumentClassification.model_validate(data)

    except Exception as e:
        print(f"CLASSIFICATION ERROR: {e}")
        return DocumentClassification(
            category="unknown",
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
        llm = get_llm()
        parser = StrOutputParser()

        prompt = PromptTemplate(
            template=DETECT_ANOMALIES_PROMPT,
            input_variables=["company_name", "documents"],
        )

        chain = prompt | llm | parser
        result_text = chain.invoke({
            "company_name": company_name,
            "documents": documents_context
        })

        result_text = result_text.strip()
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
            result_text = result_text.strip()

        import json
        result = json.loads(result_text)
        print(f"ANOMALIES DETECTED: {result}")
        return [AnomalyItem.model_validate(item) for item in result]

    except Exception as e:
        print(f"ANOMALY DETECTION ERROR: {e}")
        return []