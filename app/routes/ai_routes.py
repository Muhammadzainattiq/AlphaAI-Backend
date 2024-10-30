from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.auth import get_current_user
from app.db import get_session
from app.history_handlers import add_message_to_conversation, create_conversation
from app.models.history_models import Conversation
from app.models.user_models import User
from app.ai.main_agent import call_main_agent
from app.schemas.ai_schemas import AIResponse, AIRequest
import uuid
ai_router = APIRouter(prefix = "/ai")


# Dependency to get the compiled main_agent
def get_main_agent():
    from app.main import main_agent  # Import main_agent locally to avoid circular import
    if main_agent is None:
        raise HTTPException(status_code=500, detail="Main agent is not initialized")
    return main_agent

@ai_router.post("/call_agent", response_model=AIResponse)
def call_agent(ai_request: AIRequest,
               main_agent = Depends(get_main_agent),
                 current_user: User = Depends(get_current_user),
                 session: Session = Depends(get_session)):
    active_conversation = session.exec(
    select(Conversation)
    .where(Conversation.user_id == current_user.id, Conversation.is_active == True)
    .order_by(Conversation.created_at.desc())  # Assuming `id` is the primary key
    ).first()

    if not active_conversation:

        active_conversation = create_conversation(session, current_user.id)
    
    conversation_id = active_conversation.conversation_id

    response = call_main_agent(query=ai_request.query, thread_id = conversation_id, main_agent = main_agent)
    ai_message_content = response["messages"][-1]["content"]
    add_message_to_conversation(session, conversation_id,"human", ai_request.query)
    add_message_to_conversation(session, conversation_id, "ai", ai_message_content)

    return response

