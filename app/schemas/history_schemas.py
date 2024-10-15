from datetime import datetime
from typing import List
from sqlmodel import SQLModel


class MessageCreate(SQLModel):
    role: str
    content: str

class ConversationCreate(SQLModel):
    is_active: bool = True

class ConversationResponse(SQLModel):
    id: str
    created_at: datetime
    is_active: bool
    messages: List[MessageCreate]