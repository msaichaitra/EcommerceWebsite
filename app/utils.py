from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app import schemas
from app.database import get_session
from app.schemas.sql_models import User
import jwt
from jwt import PyJWTError
from passlib.context import CryptContext

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Secret key and JWT algorithm
SECRET_KEY = "your_secret_key_here"
JWT_ALGORITHM = "HS256"

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_username(db: Session, username: str):
    return db.query(schemas.sql_models.User).filter(schemas.sql_models.User.username == username).first()

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
        # Perform additional checks or database queries to validate the user
    except PyJWTError:
        # Token verification failed
        raise HTTPException(status_code=401, detail="Invalid token")
