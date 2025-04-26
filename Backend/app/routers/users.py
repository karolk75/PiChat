from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..models import get_db, User
from ..schemas import User as UserSchema
from ..schemas import UserCreate
from ..auth import get_api_key
import uuid

router = APIRouter()

@router.get("/users", response_model=List[UserSchema], dependencies=[Depends(get_api_key)])
async def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return users

@router.post("/users", response_model=UserSchema, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_api_key)])
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user with this username or email already exists
    db_user = db.query(User).filter(
        (User.username == user.username) | (User.email == user.email)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    # Create new user
    db_user = User(
        id=str(uuid.uuid4()),
        username=user.username,
        email=user.email
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.get("/users/{user_id}", response_model=UserSchema, dependencies=[Depends(get_api_key)])
async def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user 