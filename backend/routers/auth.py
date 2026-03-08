import os
import hashlib
import hmac
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from models import Student, Teacher, SuperAdmin, UserRole
from routers._account_messages import AccountMessages
from routers._account_utils import (
    find_user_by_login_identifier,
    find_user_by_name_identifier,
    normalize_username,
)

# Configuration
SECRET_KEY = os.getenv("LAB_JWT_SECRET", "ink_hub_lab_secret_key_change_this_in_production")
ALGORITHM = "HS256"
try:
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("LAB_ACCESS_TOKEN_EXPIRE_MINUTES", "300"))
except ValueError:
    ACCESS_TOKEN_EXPIRE_MINUTES = 300

# Password Context
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256", "bcrypt", "sha256_crypt", "django_pbkdf2_sha256"],
    deprecated="auto",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

router = APIRouter()

# --- Utilities ---
def verify_password(plain_password, hashed_password):
    if not plain_password or not hashed_password:
        return False

    # Modern hashes handled by passlib context.
    try:
        if pwd_context.verify(plain_password, hashed_password):
            return True
    except Exception:
        # Fall through to legacy compatibility checks.
        pass

    # Legacy plaintext compatibility.
    plain = str(plain_password)
    stored = str(hashed_password)
    if hmac.compare_digest(stored, plain):
        return True

    # Legacy digest compatibility.
    digest_candidates = (
        hashlib.md5(plain.encode("utf-8")).hexdigest(),
        hashlib.sha1(plain.encode("utf-8")).hexdigest(),
        hashlib.sha256(plain.encode("utf-8")).hexdigest(),
    )
    stored_lower = stored.lower()
    return any(hmac.compare_digest(stored_lower, digest) for digest in digest_candidates)


def password_hash_needs_upgrade(hashed_password: Optional[str]) -> bool:
    if not hashed_password:
        return True
    if str(hashed_password).startswith(("$pbkdf2-sha256$", "$2a$", "$2b$", "$2y$", "$5$", "pbkdf2_sha256$")):
        return False
    return True

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=AccountMessages.LOGIN_INVALID_CREDENTIALS,
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise credentials_exception
        
        # Verify user exists and get ID
        user = None
        if role == UserRole.STUDENT:
            user = await Student.find_one({"username": username})
        elif role == UserRole.TEACHER:
            user = await Teacher.find_one({"username": username})
        elif role == UserRole.SUPERADMIN:
            user = await SuperAdmin.find_one({"username": username})
            
        if user is None:
            raise credentials_exception
            
        return {"username": username, "role": role, "id": user.id}
    except JWTError:
        raise credentials_exception

# --- Schemas ---
class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str
    user_role: str
    must_change_password: bool = False

class LoginRequest(BaseModel):
    username: str
    password: str
    role: UserRole

# --- Endpoints ---

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: LoginRequest):
    identifier = normalize_username(form_data.username)
    if not identifier or not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=AccountMessages.LOGIN_IDENTIFIER_REQUIRED,
        )

    user = await find_user_by_login_identifier(form_data.role, identifier)
    if not user:
        user, name_duplicated = await find_user_by_name_identifier(form_data.role, identifier)
        if name_duplicated:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=AccountMessages.LOGIN_NAME_DUPLICATE,
            )
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AccountMessages.LOGIN_INVALID_CREDENTIALS,
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Opportunistic migration for legacy password storage.
    if password_hash_needs_upgrade(getattr(user, "password_hash", None)):
        user.password_hash = get_password_hash(form_data.password)
        await user.save()
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": form_data.role},
        expires_delta=access_token_expires
    )
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "role": form_data.role,
        "user_role": user.user_role,
        "must_change_password": bool(getattr(user, "must_change_password", False)),
    }
