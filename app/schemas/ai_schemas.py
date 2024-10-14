from sqlmodel import SQLModel

class AIRequest(SQLModel):
    query: str

class AIResponse(SQLModel):
    messages: list