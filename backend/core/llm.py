# core/llm.py
from langchain_groq import ChatGroq
from core.config import settings

MODEL = "llama-3.3-70b-versatile"

def get_llm():
    return ChatGroq(
        model=MODEL,
        api_key=settings.GEMINI_API_KEY,  # variable kept, but now holds Groq key
        temperature=0
    )