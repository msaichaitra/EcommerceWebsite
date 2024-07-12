from fastapi import Depends, HTTPException, status, APIRouter
from sqlmodel import Session
from app.schemas.sql_models import  User
from app.schemas.user_schema import UserCreate, UserBase, UserResponse, UserLogin
from app.database import get_session
from app.utils import hash_password, verify_password
from typing import List
from app import schemas

router = APIRouter(tags=["User"])


@router.post("/register/", response_model=schemas.user_schema.UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user_create: UserCreate, db: Session = Depends(get_session)):
    # Check if the user already exists
    existing_user = db.query(User).filter(User.username == user_create.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")

    # Hash the user's password before storing it
    hashed_password = hash_password(user_create.password)

    # Create a new user instance
    new_user = User(
        username=user_create.username,
        email=user_create.email,
        password=hashed_password
    )

    # Add the new user to the database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Return UserResponse with the registered user details
    return schemas.user_schema.UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email
    )


@router.post("/login/", response_model=UserResponse)
def login_user(user_login: UserLogin, db: Session = Depends(get_session)):
    # Retrieve the user by username
    db_user = db.query(User).filter(User.username == user_login.username).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Verify the password
    if not verify_password(user_login.password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    # User authenticated successfully, return user details as UserResponse
    return UserResponse(id=db_user.id, username=db_user.username, email=db_user.email)


@router.get("/users/", response_model=List[UserResponse])
def get_all_users(db: Session = Depends(get_session)):
    # Retrieve all users from the database
    users = db.query(User).all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_session)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return db_user



@router.delete("/users/{user_id}", response_model=UserResponse)
def delete_user(user_id: int, db: Session = Depends(get_session)):
    # Retrieve the user from the database
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Delete the user from the database
    db.delete(db_user)
    db.commit()

    # Return the deleted user details as UserResponse
    return db_user


