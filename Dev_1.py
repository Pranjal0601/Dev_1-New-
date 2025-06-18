
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime
from pydantic import BaseModel, EmailStr
import os
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from passlib.context import CryptContext

DATABASE_URL = "postgresql://username:password@localhost/dbname"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)
Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated ="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)



class User(Base):
    __tablename__= "users"
    userid = Column(Integer, primary_key = True, index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email_id = Column(String(100), unique = True, index = True)
    password = Column(String(150))
    

class SignupRequest(BaseModel):
    first_name: str
    last_name: str
    email_id: EmailStr
    password: str

class LoginRequest(BaseModel):
    email_id: EmailStr
    password: str

class ProfileSchema(BaseModel):
    phone: int
    address: str
    age: int
    occupation: str
    gender: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI()

@app.post("/signup")
def signup(user: SignupRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email_id == user.email_id).first()
    if existing_user:
       raise HTTPException(status_code=400, detail = "Email already registered")
    
    hashed_pw = hash_password(user.password)
    new_user = User(
        first_name=user.first_name,
        last_name=user.last_name,
        email_ID=user.email_id,
        password=hashed_pw
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User created", "user_id": new_user.userid}


