# import pytest
# from fastapi.testclient import TestClient
# from sqlmodel import SQLModel, Session, create_engine, text
# from app.main import app
# from app.db import get_session

# # Create SQLite database for testing
# SQLITE_URL = "sqlite:///./test.db"
# engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})

# # Override the get_session function to use the test SQLite database
# def override_get_session():
#     session = Session(engine)
#     try:
#         yield session
#     finally:
#         session.close()

# app.dependency_overrides[get_session] = override_get_session

# @pytest.fixture(scope="module")
# def client():
#     # Set up a FastAPI TestClient and initialize the database
#     with TestClient(app) as client:
#         SQLModel.metadata.create_all(engine)
#         yield client
#         SQLModel.metadata.drop_all(engine)

# # Fixture to clean up the database between tests
# @pytest.fixture(autouse=True)
# def clean_db():
#     """Clean the database between tests."""
#     # Clean the tables after each test to ensure isolation
#     yield
#     with Session(engine) as session:
#         # Clear data from relevant tables, e.g., User table
#         session.exec(text("DELETE FROM user"))
#         session.commit()


# def test_get_all_users(client):
#     # Step 1: First, sign up two users
#     client.post("/auth/signup", json={
#         "username": "user1",
#         "email": "user1@example.com",
#         "password": "password123"
#     })
#     client.post("/auth/signup", json={
#         "username": "user2",
#         "email": "user2@example.com",
#         "password": "password123"
#     })

#     # Step 2: Log in as one of the users to get an access token
#     response = client.post("/auth/login", data={
#         "username": "user1@example.com",
#         "password": "password123"
#     })
#     assert response.status_code == 200
#     access_token = response.json().get("access_token")
#     assert access_token is not None, "Access token is missing"

#     # Step 3: Use the access token to authenticate the request to get all users
#     response = client.get("/user/get_all_users", headers={"Authorization": f"Bearer {access_token}"})
#     assert response.status_code == 200

#     # Step 4: Verify that the response contains the two users
#     data = response.json()
#     assert len(data) == 2  # Ensure there are 2 users
#     assert data[0]["email"] == "user1@example.com"
#     assert data[1]["email"] == "user2@example.com"



# def test_update_user(client):
#     # Step 1: Sign up a user
#     response = client.post("/auth/signup", json={
#         "username": "oldusername",
#         "email": "oldemail@example.com",
#         "password": "oldpassword"
#     })
#     assert response.status_code == 200
#     user_id = response.json()["id"]

#     # Step 2: Log in to get the access token
#     response = client.post("/auth/login", data={
#         "username": "oldemail@example.com",
#         "password": "oldpassword"
#     })
#     assert response.status_code == 200
#     access_token = response.json().get("access_token")
#     assert access_token is not None, "Access token is missing"

#     # Step 3: Update the user details
#     response = client.put(f"/user/update_user/{user_id}", json={
#         "username": "newusername",
#         "email": "newemail@example.com",
#         "password": "newpassword"
#     }, headers={"Authorization": f"Bearer {access_token}"})
#     assert response.status_code == 200

#     # Step 4: Verify the user details are updated
#     updated_user = response.json()
#     assert updated_user["username"] == "newusername"
#     assert updated_user["email"] == "newemail@example.com"


# def test_delete_user(client):
#     # Step 1: Sign up a user
#     response = client.post("/auth/signup", json={
#         "username": "deletetestuser",
#         "email": "deletetestuser@example.com",
#         "password": "password123"
#     })
#     assert response.status_code == 200
#     user_id = response.json()["id"]

#     # Step 2: Log in to get the access token
#     response = client.post("/auth/login", data={
#         "username": "deletetestuser@example.com",
#         "password": "password123"
#     })
#     assert response.status_code == 200
#     access_token = response.json().get("access_token")
#     assert access_token is not None, "Access token is missing"

#     # Step 3: Delete the user
#     response = client.delete(f"/user/delete_user/{user_id}", headers={"Authorization": f"Bearer {access_token}"})
#     assert response.status_code == 204  # No content, successful deletion

#     # Step 4: Verify the token is now invalid (expecting a 401 Unauthorized)
#     response = client.get(f"/user/get_user/{user_id}", headers={"Authorization": f"Bearer {access_token}"})
#     assert response.status_code == 401, "Expected 401 Unauthorized after user deletion"



# def test_get_user(client):
#     # Step 1: Sign up a new user
#     response = client.post("/auth/signup", json={
#         "username": "testgetuser",
#         "email": "testgetuser@example.com",
#         "password": "password123"
#     })
#     assert response.status_code == 200
#     user_data = response.json()
#     user_id = user_data["id"]

#     # Step 2: Log in to get the access token
#     response = client.post("/auth/login", data={
#         "username": "testgetuser@example.com",
#         "password": "password123"
#     })
#     assert response.status_code == 200
#     access_token = response.json().get("access_token")
#     assert access_token is not None, "Access token is missing"

#     # Step 3: Get the user details using the correct user ID
#     response = client.get(f"/user/get_user/{user_id}", headers={"Authorization": f"Bearer {access_token}"})
#     assert response.status_code == 200
#     user_response_data = response.json()
#     assert user_response_data["id"] == user_id
#     assert user_response_data["username"] == "testgetuser"
#     assert user_response_data["email"] == "testgetuser@example.com"

#     # Step 4: Try to get details of a non-existing user (expecting 404)
#     non_existing_user_id = user_id + 1000  # Simulate a non-existing user
#     response = client.get(f"/user/get_user/{non_existing_user_id}", headers={"Authorization": f"Bearer {access_token}"})
#     assert response.status_code == 404
#     assert response.json()["detail"] == "User not found"