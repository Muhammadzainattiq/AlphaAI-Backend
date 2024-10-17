from fastapi import HTTPException
from sqlmodel import Session, select
from app.models.history_models import Conversation, Message
from app.models.user_models import User

def create_conversation(session: Session, user_id: int) -> Conversation:
    # Check if the user exists before creating the conversation
    user = session.get(User, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Proceed to create the conversation if the user exists
    conversation = Conversation(user_id=user_id)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    
    return conversation


def add_message_to_conversation(session: Session, conversation_id: str, role: str, content: str):
    # Check if the conversation exists
    conversation = session.get(Conversation, conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Add the message to the conversation if it exists
    message = Message(conversation_id=conversation_id, role=role, content=content)
    session.add(message)
    session.commit()
    session.refresh(message)
    return message

def get_conversation_by_id(session: Session, conversation_id: str):
    conversation = session.exec(select(Conversation).where(Conversation.id == conversation_id)).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation


# Delete conversation handler
def delete_conversation(session: Session, conversation_id: str):
    conversation = session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    session.delete(conversation)
    session.commit()

# Get all conversations by user handler
def get_all_user_conversations(session: Session, user_id: int):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    conversations = session.exec(select(Conversation).where(Conversation.user_id == user_id)).all()
    return conversations


def mark_conversation_as_inactive(session: Session, conversation_id: str):
    # Fetch the conversation by ID
    conversation = session.get(Conversation, conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Mark the conversation as inactive
    conversation.is_active = False
    session.commit()
    
    return {"message": "Conversation marked as inactive"}


def mark_conversation_as_active(session: Session, conversation_id: str):
    # Fetch the conversation by ID
    conversation = session.get(Conversation, conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Mark the conversation as active
    conversation.is_active = True
    session.commit()
    
    return {"message": "Conversation marked as active"}



def update_message_handler(session: Session, message_id: int, new_content: str):
    # Fetch the message by its ID
    message = session.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Update only the message content
    message.content = new_content
    
    # Commit the changes
    session.commit()
    session.refresh(message)
    
    return message