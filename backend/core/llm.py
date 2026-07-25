# core/llm.py
# LLM client using LangChain with Google Gemini Flash
# Using LangChain allows easy model switching and built-in output parsers

from langchain_google_genai import ChatGoogleGenerativeAI
from core.config import settings

MODEL = "gemini-2.0-flash"

def get_llm():
    """
    Returns a LangChain-wrapped Gemini Flash model.
    temperature=0 ensures deterministic, consistent outputs.
    Called fresh each time to avoid stale connections.
    """
    return ChatGoogleGenerativeAI(
        model=MODEL,
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0
    )