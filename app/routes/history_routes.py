from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Conversation, Message
from app.schemas import ConversationResponse, MessageCreate
from app.db import get_session
from app.history_handlers import create_conversation, add_message_to_conversation, get_conversation_by_id
from app.auth import get_current_user
from app.models.user_models import User
router = APIRouter()

# Create a new conversation
@router.post("/conversations/", response_model=ConversationResponse)
def start_conversation(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    conversation = create_conversation(session, current_user.id)
    return conversation

# Add a message to an existing conversation
@router.post("/conversations/{conversation_id}/messages/", response_model=MessageCreate)
def send_message(conversation_id: str, message: MessageCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    add_message_to_conversation(session, conversation_id, message.role, message.content)
    return message

# Get a conversation by its ID (with history)
@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    conversation = get_conversation_by_id(session, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation
