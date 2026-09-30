import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy.orm import Session

try:
    from .database import SessionLocal
    from .models import User
except ImportError:
    from database import SessionLocal
    from models import User

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    vercel_environment = os.getenv("VERCEL_ENV", "").lower()
    is_deployed = os.getenv("VERCEL") == "1" or vercel_environment in {"production", "preview"}
    is_production = os.getenv("ENVIRONMENT", "").lower() == "production"
    if is_deployed or is_production:
        raise RuntimeError("SECRET_KEY must be set for deployed environments.")
    SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
AUTH_COOKIE_NAME = os.getenv("AUTH_COOKIE_NAME", "todo_access_token")
AUTH_COOKIE_SECURE = os.getenv("AUTH_COOKIE_SECURE", "true").lower() == "true"
AUTH_COOKIE_SAMESITE = os.getenv("AUTH_COOKIE_SAMESITE", "lax").lower()
if AUTH_COOKIE_SAMESITE not in {"lax", "strict", "none"}:
    raise ValueError("AUTH_COOKIE_SAMESITE must be lax, strict, or none")
if AUTH_COOKIE_SAMESITE == "none" and not AUTH_COOKIE_SECURE:
    raise ValueError("AUTH_COOKIE_SECURE must be true when AUTH_COOKIE_SAMESITE is none")

DEFAULT_CORS_ORIGINS = (
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
)


def _load_cors_origins() -> tuple[str, ...]:
    configured_origins = os.getenv("CORS_ORIGINS")
    if configured_origins is None:
        origins = [] if os.getenv("VERCEL_ENV") else list(DEFAULT_CORS_ORIGINS)
    else:
        origins = [origin.strip() for origin in configured_origins.split(",") if origin.strip()]

    for variable in ("VERCEL_URL", "VERCEL_PROJECT_PRODUCTION_URL"):
        host = os.getenv(variable, "").strip().rstrip("/")
        if host:
            origins.append(host if "://" in host else f"https://{host}")

    return tuple(dict.fromkeys(origins))


CORS_ORIGINS = _load_cors_origins()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login", auto_error=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(user: User) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": user.username, "user_id": user.id, "exp": expires}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    db: db_dependency,
    request: Request,
    bearer_token: Annotated[str | None, Depends(oauth2_scheme)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
    )

    token = bearer_token or request.cookies.get(AUTH_COOKIE_NAME)
    if token is None:
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("user_id")

        if username is None or user_id is None:
            raise credentials_exception

        user = db.query(User).filter(User.id == user_id, User.username == username).first()
        if user is None:
            raise credentials_exception

        return user
    except jwt.PyJWTError as exc:
        raise credentials_exception from exc
