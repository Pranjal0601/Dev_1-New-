#import all comps
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException
from passlib.context import CryptContext
from sqlmodel import SQLModel, Field, create_engine, Session, select
from pydantic import BaseModel

app = FastAPI()

#gets databse session
def get_session():
    with Session(engine) as session:
        yield session

#hashing passwords
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#datbase connection
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

#Request models- to structure the data correctly 
class UserCreate (BaseModel):
    first_name: str
    last_name: str
    email_id: str
    password: str

class UserProfileCreate(BaseModel):
    user_id: UUID
    phone: Optional[str] = None
    age: Optional[int] = None
    occupation: Optional[str] = None
    gender: Optional[str] = None

# launching the tables on startup = startup tells the API which defined function to run when the application starts
@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

#API endpoints- to create and retrieve users and profiles
@app.post("/users/", response_model=UserSignUp, status_code=201)
#hash the password
def create_user(user: UserCreate, session: Session = Depends(get_session)):
     hashed_password = pwd_context.hash(user.password)

#create a new user
     db_user = UserSignUp(
         first_name=user.first_name,
         last_name=user.last_name,
         email_id=user.email_id,
         password=hashed_password)
     session.add(db_user)
     session.commit()
     session.refresh(db_user)
     return db_user

#reading users
@app.get("/users/",response_model=list[UserSignUp])
def read_users(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    users = session.exec(select(UserSignUp).offset(skip).limit(limit)).all()
    return users

#creating a profile
@app.get("/users/",response_model=UserSignUp)
def read_user(user_id: UUID, session: Session = Depends(get_session)):
    user = session.get(UserSignUp, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user 

#reading user profile
@app.post("/user_profile/", response_model=UserProfile, status_code=201)
def create_user_profile(profile: UserProfileCreate, session: Session = Depends(get_session)):
    db_profile = UserProfile(**profile.dict())
    session.add(db_profile)
    session.commit()
    session.refresh(db_profile)
    return db_profile

#checks if user found and returns profile
@app.get("/user_profile/{user_id}", response_model=UserProfile)
def read_user_profile(user_id: UUID, session: Session = Depends(get_session)):
    profile = session.exec(select(UserProfile).where(UserProfile.user_id == user_id)).first()
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")
    return profile  

# Main function to run
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0", port=8000)
