import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine, text
from app.main import app
from app.db import get_session
from app.models.history_models import Message
from app.schemas.ai_schemas import AIRequest, AIResponse  # Import your AI schemas

# Create SQLite database for testing
SQLITE_URL = "sqlite:///./test.db"
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})

# Override the get_session function to use the test SQLite database
def override_get_session():
    session = Session(engine)
    try:
        yield session
    finally:
        session.close()

app.dependency_overrides[get_session] = override_get_session

@pytest.fixture(scope="module")
def client():
    # Set up a FastAPI TestClient and initialize the database
    with TestClient(app) as client:
        SQLModel.metadata.create_all(engine)
        yield client
        SQLModel.metadata.drop_all(engine)

# Fixture to clean up the database between tests
@pytest.fixture(autouse=True)
def clean_db():
    """Clean the database between tests."""
    yield
    with Session(engine) as session:
        session.exec(text("DELETE FROM user"))
        session.exec(text("DELETE FROM conversation"))
        session.exec(text("DELETE FROM message"))
        session.commit()

@pytest.fixture
def access_token(client):
    # Signup a new user and retrieve access token
    response = client.post(
        "/auth/signup",
        json={"username": "testuser", "email": "testuser@example.com", "password": "testpassword"}
    )
    assert response.status_code == 200

    # Login to get access token
    login_response = client.post(
        "/auth/login",
        data={"username": "testuser@example.com", "password": "testpassword"}
    )
    assert login_response.status_code == 200
    token_data = login_response.json()
    return token_data["access_token"]

def test_ai_route(client, access_token):
    # Define the query for the AI
    ai_request_data = {"query": "hi how are you?"}

    # Send a request to the AI route
    response = client.post(
        "/ai/call_agent",
        json=ai_request_data,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # Assert the response status code
    assert response.status_code == 200

    # Parse the response
    response_data = response.json()

    # Assert the response structure
    assert "messages" in response_data
    assert isinstance(response_data["messages"], list)

    # Validate the structure of the first message
    assert len(response_data["messages"]) > 0  # Ensure there are messages in the response
    first_message = response_data["messages"][0]
    assert "role" in first_message
    assert "content" in first_message
    assert "created_at" in first_message
    assert "id" in first_message

    # You can also assert specific values for the first message if necessary
    assert first_message["role"] == "human"  # or whatever expected role
    assert isinstance(first_message["created_at"], str)  # Check that created_at is a string
