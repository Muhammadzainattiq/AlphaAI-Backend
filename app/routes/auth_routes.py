from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from app.schemas.user_schemas import UserCreate, UserResponse, Token
from app.models.user_models import User
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user
from app.db import get_session
from sqlmodel import select
auth_router = APIRouter(prefix = "/auth")

# Signup Endpoint
@auth_router.post("/signup", response_model=UserResponse)
def signup(user_create: UserCreate, session: Session = Depends(get_session)):
    # Check if user already exists
    user_exists = session.exec(select(User).where(User.email == user_create.email)).first()
    if user_exists:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    # Hash the password and create user
    hashed_password = get_password_hash(user_create.password)
    new_user = User(username=user_create.username, email=user_create.email, hashed_password=hashed_password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

# Login Endpoint
#NOTE: You have to tell the frontend developer that he has to send the email in the key of username and should ask from the user the email but put it against the username key in the header.
@auth_router.post("/login", response_model=Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends(OAuth2PasswordRequestForm)], session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.email == form_data.username)).first()
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid credentials")
    
    # Create JWT token
    access_token = create_access_token(data={"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

# Token Refresh Endpoint
@auth_router.post("/token/refresh", response_model=Token)
def refresh_token(current_user: User = Depends(get_current_user)):
    access_token = create_access_token(data={"sub": str(current_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


# Get All Users Endpoint
@auth_router.get("/users", response_model=List[UserResponse])
def get_all_users(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    users = session.exec(select(User)).all()
    return users



# Update User Endpoint
@auth_router.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Update fields
    user.username = user_data.username
    user.email = user_data.email
    user.hashed_password = get_password_hash(user_data.password)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user


# Delete User Endpoint
@auth_router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    session.delete(user)
    session.commit()
    return None


@auth_router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user