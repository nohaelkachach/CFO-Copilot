# schemas/chat.py
from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    question: str                      # e.g. "What were my top expenses in June?"
    document_id: Optional[str] = None  # if user wants to ask about a specific document

class ChatResponse(BaseModel):
    answer: str
    sources: list[str] = []           # which documents were used to answer