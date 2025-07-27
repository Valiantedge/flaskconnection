from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import User, Customer
from config import SessionLocal, JWT_SECRET_KEY
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta

router = APIRouter()


class SignupRequest(BaseModel):
    customer_name: str
    admin_username: str
    admin_password: str

class UserRegister(BaseModel):
    username: str
    password: str
@router.post("/signup", summary="Customer sign up (creates customer and admin user)")
def signup(signup: SignupRequest):
    db: Session = SessionLocal()
    # Check if customer already exists
    if db.query(Customer).filter(Customer.name == signup.customer_name).first():
        db.close()
        raise HTTPException(status_code=400, detail="Customer already exists")
    # Create customer
    customer = Customer(name=signup.customer_name)
    db.add(customer)
    db.commit()
    db.refresh(customer)
    # Check if admin username exists
    if db.query(User).filter(User.username == signup.admin_username).first():
        db.close()
        raise HTTPException(status_code=400, detail="Username already exists")
    # Create admin user linked to customer
    admin_user = User(username=signup.admin_username, password=signup.admin_password, customer_id=customer.id)
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    db.close()
    return {"customer_id": customer.id, "admin_user_id": admin_user.id, "admin_username": admin_user.username}

class UserLogin(BaseModel):
    username: str
    password: str

def create_access_token(data: dict, expires_delta: timedelta = timedelta(hours=1)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm="HS256")
    return encoded_jwt

@router.post("/register")
def register_user(user: UserRegister):
    db: Session = SessionLocal()
    if db.query(User).filter(User.username == user.username).first():
        db.close()
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
    token = create_access_token({"sub": db_user.username, "user_id": db_user.id})
    return {"token": token}
