import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine, text
from app.main import app
from app.db import get_session
from app.models.history_models import Conversation, Message

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

@pytest.fixture
def create_conversation_and_message(client, access_token):
    # Create a conversation
    response = client.post(
        "/history/start_new_conversation/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    conversation = response.json()

    # Add a message to the conversation
    message_data = {
        "role": "user",
        "content": "Initial message"
    }
    message_response = client.post(
        f"/history/add_message/{conversation['conversation_id']}/",
        json=message_data,
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert message_response.status_code == 200
    message = message_response.json()

    return conversation, message

def test_start_conversation(client, access_token):
    # Test starting a new conversation
    response = client.post(
        "/history/start_new_conversation/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    conversation_data = response.json()
    assert "conversation_id" in conversation_data
    assert conversation_data["is_active"] is True

def test_start_new_conversation_marks_previous_as_inactive(client, access_token):
    # Create the first conversation
    response = client.post(
        "/history/start_new_conversation/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    first_conversation = response.json()

    # Ensure the first conversation is active
    assert first_conversation["is_active"] is True

    # Create the second conversation
    response = client.post(
        "/history/start_new_conversation/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    second_conversation = response.json()

    # Ensure the second conversation is active
    assert second_conversation["is_active"] is True

    # Fetch the first conversation to check its status
    with Session(engine) as session:
        first_conversation_from_db = session.get(Conversation, first_conversation["conversation_id"])
        assert first_conversation_from_db is not None
        assert first_conversation_from_db.is_active is False  # The first one should now be inactive

    # Fetch the second conversation to check its status
    with Session(engine) as session:
        second_conversation_from_db = session.get(Conversation, second_conversation["conversation_id"])
        assert second_conversation_from_db is not None
        assert second_conversation_from_db.is_active is True  

def test_add_message_to_conversation(client, access_token):
    # Start a conversation first
    response = client.post(
        "/history/start_new_conversation/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    conversation_data = response.json()

    # Add message to the conversation
    response = client.post(
        f"/history/add_message/{conversation_data['conversation_id']}/",
        json={"role": "user", "content": "Hello!"},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    message_data = response.json()
    assert message_data["role"] == "user"
    assert message_data["content"] == "Hello!"


def test_delete_conversation(client, access_token):
    # Start a conversation first
    response = client.post(
        "/history/start_new_conversation/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    conversation_data = response.json()

    # Delete the conversation
    response = client.delete(
        f"/history/delete_conversation/{conversation_data['conversation_id']}/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["detail"] == "Conversation deleted"

def test_get_all_user_conversations(client, access_token):
    # Start two conversations
    response = client.post(
        "/history/start_new_conversation/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    conversation_data = response.json()

    # Print or inspect the response data structure
    print("Response data:", conversation_data)
    
    user_id = conversation_data["user_id"]

    response = client.post(
        "/history/start_new_conversation/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200

    # Get all conversations for the user
    response = client.get(
        f"/history/get_all_user_conversations/{user_id}/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    conversations = response.json()
    assert len(conversations) == 2

def test_mark_conversation_as_active(client, access_token):
    # Start a conversation first
    response = client.post(
        "/history/start_new_conversation/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    conversation_data = response.json()

    # Mark conversation as inactive
    response = client.put(
        f"/history/active_conversation/{conversation_data['conversation_id']}/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["conversation_id"] == conversation_data["conversation_id"]
    assert response.json()["user_id"] == conversation_data["user_id"]
    assert response.json()["is_active"] == True

def test_mark_conversation_as_inactive(client, access_token):
    # Start a conversation first
    response = client.post(
        "/history/start_new_conversation/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    conversation_data = response.json()

    # Mark conversation as inactive
    response = client.put(
        f"/history/inactive_conversation/{conversation_data['conversation_id']}/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    assert response.json()["conversation_id"] == conversation_data["conversation_id"]
    assert response.json()["user_id"] == conversation_data["user_id"]
    assert response.json()["is_active"] == False


def test_update_message(client, access_token, create_conversation_and_message):
    # Get the conversation and message created by the fixture
    conversation, message = create_conversation_and_message

    # Updated content for the message
    updated_content = {"content": "Updated message content"}

    # Perform a PATCH request to update the message content
    response = client.patch(
        f"/history/update_message/{message['message_id']}/",
        json=updated_content,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    # Assert that the request was successful
    assert response.status_code == 200
    assert response.json()["message"]["content"] == updated_content["content"]

    # Fetch the message again to verify it was updated in the database
    with Session(engine) as session:
        updated_message = session.get(Message, message['message_id'])
        assert updated_message.content == updated_content["content"]


def test_get_conversation_history(client, access_token, create_conversation_and_message):
    # Extract the conversation and message from the fixture
    conversation, message = create_conversation_and_message
    
    # Fetch the conversation history using the conversation_id
    response = client.get(
        f"/history/get_conversation_history/{conversation['conversation_id']}/",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    
    # Assert the response status code
    assert response.status_code == 200
    
    # Assert the response data
    history_data = response.json()
    assert history_data["conversation_id"] == conversation["conversation_id"]
    assert history_data["user_id"] == conversation["user_id"]
    assert len(history_data["messages"]) == 1  # We expect one message in the conversation

    # Check that the message details match what was sent
    assert history_data["messages"][0]["message_id"] == message["message_id"]
    assert history_data["messages"][0]["role"] == message["role"]
    assert history_data["messages"][0]["content"] == message["content"]
    assert "created_at" in history_data["messages"][0]  # Check that created_at is present



def test_resume_conversation(client, access_token, create_conversation_and_message):
    # Extract the conversation and message from the fixture
    conversation, message = create_conversation_and_message
    
    # Mark the conversation as inactive
    client.get(f"/history/exit_conversation/{conversation['conversation_id']}/", headers={"Authorization": f"Bearer {access_token}"})

    # Ensure the conversation is inactive now
    response = client.get(f"/history/get_conversation_history/{conversation['conversation_id']}/", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    history_data = response.json()
    assert history_data["is_active"] is False  # Check if it's inactive
    
    # Resume the conversation
    response = client.get(f"/history/resume_old_conversation/{conversation['conversation_id']}/", headers={"Authorization": f"Bearer {access_token}"})
    
    # Assert the response status code
    assert response.status_code == 200
    
    # Assert the response data
    history_data = response.json()
    assert history_data["conversation_id"] == conversation["conversation_id"]
    assert history_data["user_id"] == conversation["user_id"]
    assert len(history_data["messages"]) == 1  # We expect one message in the conversation
    assert history_data["is_active"] is True  # Ensure the conversation is now active


def test_exit_conversation(client, access_token, create_conversation_and_message):
    # Extract the conversation and message from the fixture
    conversation, message = create_conversation_and_message
    
    # Ensure the conversation is initially active
    assert conversation["is_active"] is True

    # Exit the conversation
    response = client.get(f"/history/exit_conversation/{conversation['conversation_id']}/", headers={"Authorization": f"Bearer {access_token}"})
    
    # Assert the response status code
    assert response.status_code == 200
    
    # Assert the response data
    exited_conversation = response.json()
    assert exited_conversation["conversation_id"] == conversation["conversation_id"]
    assert exited_conversation["is_active"] is False  # Ensure the conversation is now inactive
    
    # Fetch the conversation history to ensure its status
    history_response = client.get(f"/history/get_conversation_history/{conversation['conversation_id']}/", headers={"Authorization": f"Bearer {access_token}"})
    assert history_response.status_code == 200
    history_data = history_response.json()
    assert history_data["is_active"] is False  # Confirm it's inactive in the history