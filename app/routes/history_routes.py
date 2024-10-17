from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlmodel import select
from app.models.history_models import Conversation, Message
from app.schemas.history_schemas import ConversationResponse, MessageCreate, MessageUpdateContent
from app.db import get_session
from app.history_handlers import create_conversation, add_message_to_conversation, delete_conversation, get_all_user_conversations, get_conversation_by_id, mark_conversation_as_active, mark_conversation_as_inactive, update_message_handler
from app.auth import get_current_user
from app.models.user_models import User
history_router = APIRouter(prefix='/history')

# Create a new conversation
@history_router.post("/start_conversation/")
def start_conversation(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    conversation = create_conversation(session, current_user.id)
    return conversation

# Add a message to an existing conversation
@history_router.post("/add_message/{conversation_id}/")
def send_message(conversation_id: str, message: MessageCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    new_message = add_message_to_conversation(session, conversation_id, message.role, message.content)
    print("Returned by handler>>>", new_message)
    return new_message

# Get a conversation by its ID (with history)
@history_router.get("/get_conversation/{conversation_id}", response_model=ConversationResponse)
def get_conversation(conversation_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    conversation = get_conversation_by_id(session, conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


# **New** Route to delete conversation
@history_router.delete("/delete_conversation/{conversation_id}")
def delete_conversation_route(conversation_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    delete_conversation(session, conversation_id)
    return {"detail": "Conversation deleted"}

# **New** Route to get all conversations by user
@history_router.get("/get_user_conversations/{user_id}/")
def get_all_user_conversations_route(user_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return get_all_user_conversations(session, user_id)
                    
@history_router.put("/inactive_conversation/{conversation_id}/")
def mark_conversation_inactive(conversation_id: str, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    return mark_conversation_as_inactive(session, conversation_id)



@history_router.put("/active_conversation/{conversation_id}/")
def mark_conversation_active(conversation_id: str, session: Session = Depends(get_session), 
                             current_user: User = Depends(get_current_user)):
    return mark_conversation_as_active(session, conversation_id)


@history_router.patch("/update_message/{message_id}/")
def update_message_route(message_id: int, updated_message: MessageUpdateContent, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    # Fetch the message by ID and verify ownership
    message = session.get(Message, message_id)
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Verify if the user owns the conversation
    if message.conversation.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this message")

    # Call the handler to update the message content
    updated_message_obj = update_message_handler(session, message_id, updated_message.content)

    return {"detail": "Message content updated", "message": updated_message_obj}