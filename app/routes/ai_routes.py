from fastapi import APIRouter, Depends, HTTPException
from app.auth import get_current_user
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
def call_agent(ai_request: AIRequest, main_agent = Depends(get_main_agent), current_user: User = Depends(get_current_user)):
    thread_id = str(uuid.uuid4())
    response = call_main_agent(query=ai_request.query, thread_id = thread_id, main_agent = main_agent)
    return response

