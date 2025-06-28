from pydantic import BaseModel
from typing import Optional

class ChatMessage(BaseModel):
    session_id: str
    question: str

class ChatResponse(BaseModel):
    session_id: str
    question: str
    answer: str

class SessionResponse(BaseModel):
    session_id: str
    message: str 