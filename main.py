from fastapi import FastAPI, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
import uvicorn
from passlib.context import CryptContext

app = FastAPI(title="User Service")

# DB Setup
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/happypaws_users"
try:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base = declarative_base()

    class User(Base):
        __tablename__ = "users"
        id = Column(Integer, primary_key=True, index=True)
        email = Column(String, unique=True, index=True)
        hashed_password = Column(String)
        role = Column(String, default="user")

    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"DB Connection failed, ensure PostgreSQL is running and DB 'happypaws_users' exists. Error: {e}")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserCreate(BaseModel):
    email: str
    password: str
    role: str = "user"

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"service": "User Service"}

@app.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = pwd_context.hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"msg": "User registered successfully"}

@app.post("/login")
def login(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not pwd_context.verify(user.password, db_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    # Simplistic JWT placeholder
    return {"access_token": "fake-jwt-token", "token_type": "bearer", "role": db_user.role}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=True)
