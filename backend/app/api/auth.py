from datetime import datetime, timedelta
from typing import Optional
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.deps import get_db, get_current_user
from app.models import User
from app.schemas import UserCreate, User as UserSchema, Token

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

@router.post("/signup", response_model=UserSchema)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Attempting to create user with email: {user.email}", user.username)
    try:
        db_user = db.query(User).filter(User.email == user.email).first()
        logger.info(f"db_user: {db_user}, with email: {user.email}")
        if db_user:
            logger.warning(f"Email already registered: {user.email}")
            raise HTTPException(status_code=400, detail="Email already registered")
        
        logger.info(f"Hashing password for user: {user.username}")
        hashed_password = get_password_hash(user.password)
        logger.info(f"Hashed password: {hashed_password}")
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password
        )
        logger.info(f"Adding user to database: {db_user}")
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        logger.info(f"Successfully created user with email: {user.email}")
        return db_user
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    logger.info(f"Login attempt for user: {form_data.username}")
    try:
        user = db.query(User).filter(User.email == form_data.username).first()
        if not user or not verify_password(form_data.password, user.hashed_password):
            logger.warning(f"Invalid login attempt for user: {form_data.username}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": str(user.id)}, expires_delta=access_token_expires
        )
        logger.info(f"Successful login for user: {form_data.username}")
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        raise

@router.get("/me", response_model=UserSchema)
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user 