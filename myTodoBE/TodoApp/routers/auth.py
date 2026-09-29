from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

try:
    from ..dependencies import (
        ACCESS_TOKEN_EXPIRE_MINUTES,
        AUTH_COOKIE_NAME,
        AUTH_COOKIE_SAMESITE,
        AUTH_COOKIE_SECURE,
        create_access_token,
        db_dependency,
        get_current_user,
        get_password_hash,
        verify_password,
    )
    from ..models import User
    from ..schemas import UserCreate, UserLogin, UserResponse
except ImportError:
    from dependencies import (
        ACCESS_TOKEN_EXPIRE_MINUTES,
        AUTH_COOKIE_NAME,
        AUTH_COOKIE_SAMESITE,
        AUTH_COOKIE_SECURE,
        create_access_token,
        db_dependency,
        get_current_user,
        get_password_hash,
        verify_password,
    )
    from models import User
    from schemas import UserCreate, UserLogin, UserResponse

router = APIRouter(tags=["auth"])


def _secure_cookie_for_request(request: Request) -> bool:
    if request.url.hostname in {"localhost", "127.0.0.1"}:
        return False
    return AUTH_COOKIE_SECURE


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=UserResponse)
async def register_user(db: db_dependency, user: UserCreate):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user is not None:
        raise HTTPException(status_code=400, detail="Username already registered.")

    new_user = User(username=user.username, password_hash=get_password_hash(user.password))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=UserResponse)
async def login_user(
    request: Request,
    response: Response,
    db: db_dependency,
    user_login: UserLogin,
):
    user = db.query(User).filter(User.username == user_login.username).first()
    if user is None or not verify_password(user_login.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    response.set_cookie(
        key=AUTH_COOKIE_NAME,
        value=create_access_token(user),
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=_secure_cookie_for_request(request),
        samesite=AUTH_COOKIE_SAMESITE,
        path="/",
    )
    return user


@router.get("/me", response_model=UserResponse)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@router.post("/logout")
async def logout_user(request: Request, response: Response):
    response.delete_cookie(
        key=AUTH_COOKIE_NAME,
        httponly=True,
        secure=_secure_cookie_for_request(request),
        samesite=AUTH_COOKIE_SAMESITE,
        path="/",
    )
    return {"message": "Logged out."}
