from typing import Optional

from pydantic import BaseModel, Field


class TodoRequest(BaseModel):
    task: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Todo"
    )
    completed: bool = Field(default=False)


class TodoResponse(BaseModel):
    id: int
    task: str
    completed: bool
    user_id: int

    model_config = {"from_attributes": True}


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=128)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    username: str

    model_config = {"from_attributes": True}


class NoteCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    content: str = Field(..., min_length=1, max_length=2000)
    todo_id: Optional[int] = None


class NoteUpdate(BaseModel):
    title: str = Field(..., min_length=1, max_length=120)
    content: str = Field(..., min_length=1, max_length=2000)


class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    user_id: int
    todo_id: Optional[int] = None

    model_config = {"from_attributes": True}
