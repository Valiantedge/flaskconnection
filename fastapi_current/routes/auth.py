from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import User
from config import SessionLocal
from pydantic import BaseModel

router = APIRouter()

class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

@router.post("/register")
def register_user(user: UserRegister):
    db: Session = SessionLocal()
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    new_user = User(username=user.username, password=user.password)
    db.add(new_user)
    db.commit()
    db.close()
    return {"status": "created"}

@router.post("/login")
def login_user(user: UserLogin):
    db: Session = SessionLocal()
    db_user = db.query(User).filter(User.username == user.username, User.password == user.password).first()
    db.close()
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    # For demo, return a dummy token
    return {"token": "jwt_token_here"}
