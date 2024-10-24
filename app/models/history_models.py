
from datetime import datetime
from typing import List
import uuid
from sqlmodel import Field, Relationship, SQLModel


class Conversation(SQLModel, table=True):
    conversation_id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    messages: List["Message"] = Relationship(back_populates="conversation")

class Message(SQLModel, table=True):
    message_id: int = Field(default=None, primary_key=True)
    conversation_id: str = Field(foreign_key="conversation.conversation_id")
    role: str  # 'user' or 'ai'
    content: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    conversation: Conversation | None = Relationship(back_populates="messages")