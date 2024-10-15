from sqlmodel import Session, select
from app.models import Conversation, Message

def create_conversation(session: Session, user_id: int) -> Conversation:
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation

def add_message_to_conversation(session: Session, conversation_id: str, role: str, content: str):
    message = Message(conversation_id=conversation_id, role=role, content=content)
    session.add(message)
    session.commit()

def get_conversation_by_id(session: Session, conversation_id: str):
    return session.exec(select(Conversation).where(Conversation.id == conversation_id)).first()
