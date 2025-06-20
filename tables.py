#import all comps
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, status
from passlib.context import CryptContext
from sqlmodel import SQLModel, Field, create_engine, Session, select
from pydantic import BaseModel

#hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#datbase connection- check .env file for DATABASE_URL
DATABASE_URL = "postgresql://xcm_u9g4_user:m0TaXIwfrrvii1d1c37rVRLz80wSSPrs@dpg-cu9irh3qf0us73c0e3vg-a.singapore-postgres.render.com/dev_1"
engine = create_engine(DATABASE_URL, echo=True) 

#User sign up table
class UserSignUp(SQLModel, table=True):
    __tablename__ = "users"
    user_id:UUID = Field(
        primary_key=True, 
        default_factory= uuid4,
        nullable = False,
        unique= True
        )
    first_name: str = Field(nullable=False)
    last_name: str = Field(nullable=False)
    email_id: str = Field( 
        unique=True, 
        nullable= False, 
        regex=r".+@.+\..+"
        )
    password: str = Field(max_length=100, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    

#profile table
class UserProfile(SQLModel, table=True):
    __tablename__ = "user_profile"
    address_id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.user_id", nullable=False)
    phone: Optional[str] = Field(max_length=15)
    age: Optional[int] = Field(ge=13, le=120)
    occupation: Optional[str] = Field(max_length=100)
    gender: Optional[str] = Field(max_length=10)
    created_at: datetime = Field(default_factory=datetime, nullable=False)
    updated_at: datetime = Field(default_factory=datetime, nullable=False)

#Address table
class Address(SQLModel, table=True):
    __tablename__ = "address"
    address_id: UUID = Field(default_factory=uuid4, primary_key=True) 
    user_id: UUID = Field(foreign_key="users.user_id", nullable=False)
    address_line1: str = Field(max_length=255, nullable=False)
    address_line2: Optional[str] = Field(max_length=255, nullable=True)
    city: str = Field(nullable=False)
    state: str = Field(nullable=False)
    postal_code: str = Field(nullable=False)
    country: str = Field(nullable=False)

# Create all tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Main function to run
if __name__ == "__main__":
    create_db_and_tables()
    print("Tables created successfully!")
