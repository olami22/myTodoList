from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

try:
    from ..dependencies import db_dependency, get_current_user
    from ..models import Todo, User
    from ..schemas import TodoRequest, TodoResponse
except ImportError:
    from dependencies import db_dependency, get_current_user
    from models import Todo, User
    from schemas import TodoRequest, TodoResponse

router = APIRouter(tags=["todo"])


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[TodoResponse])
async def read_all(
    db: db_dependency,
    current_user: Annotated[User, Depends(get_current_user)],
):
    return db.query(Todo).filter(Todo.user_id == current_user.id).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK, response_model=TodoResponse)
async def read_todo(
    db: db_dependency,
    todo_id: int = Path(gt=0),
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    todo_model = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == current_user.id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")


@router.post("/todo", status_code=status.HTTP_201_CREATED, response_model=TodoResponse)
async def create_todo(
    db: db_dependency,
    todo_request: TodoRequest,
    current_user: Annotated[User, Depends(get_current_user)],
):
    todo_model = Todo(task=todo_request.task, completed=todo_request.completed, user_id=current_user.id)
    db.add(todo_model)
    db.commit()
    db.refresh(todo_model)
    return todo_model


@router.put("/todo/{todo_id}", status_code=status.HTTP_200_OK, response_model=TodoResponse)
async def update_todo(
    db: db_dependency,
    todo_request: TodoRequest,
    todo_id: int = Path(gt=0),
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    todo_model = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == current_user.id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found.")

    todo_model.completed = todo_request.completed
    if todo_request.task is not None:
        todo_model.task = todo_request.task

    db.add(todo_model)
    db.commit()
    return todo_model


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    db: db_dependency,
    todo_id: int = Path(gt=0),
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    todo_model = db.query(Todo).filter(Todo.id == todo_id, Todo.user_id == current_user.id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found.")

    db.delete(todo_model)
    db.commit()
    return None
