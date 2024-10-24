from datetime import datetime
from typing import List
from sqlmodel import SQLModel


class MessageCreate(SQLModel):
    role: str
    content: str

class MessagesResponse(SQLModel):
    message_id: int
    role: str
    content: str
    created_at: datetime


class ConversationCreate(SQLModel):
    is_active: bool = True

class HistoryResponse(SQLModel):
    conversation_id: str
    user_id: int
    created_at: datetime
    is_active: bool
    messages: List[MessagesResponse]

class MessageUpdateContent(SQLModel):
    content: str