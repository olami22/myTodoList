from typing import Annotated
from fastapi import FastAPI,Depends,HTTPException,Path
from sqlalchemy.orm import Session
from models import Todo
from database import engine, SessionLocal
from starlette import status
from schemas import TodoRequest
import models
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React
        "http://localhost:5173",  # Vite
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# @app.get("/")
# def read_root():
#     return {"My Todo App"}

@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(db:db_dependency ):
    return db.query(Todo).all()


@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db:db_dependency,
                     todo_id:int = Path(gt=0)):
    todo_model = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail ='Todo not found')


@app.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency,
                      todo_request: TodoRequest):
    todo_model = Todo(**todo_request.dict())
    db.add(todo_model)
    db.commit()
    return todo_model

@app.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db:db_dependency,
                      todo_request:TodoRequest,
                      todo_id:int = Path(gt=0)):
    todo_model = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found.')
    todo_model.completed = todo_request.completed
    db.add(todo_model)
    db.commit()
    return todo_model

@app.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency,todo_id:int=Path(gt=0)):
    todo_model = db.query(Todo).filter(Todo.id == todo_id).first()
    if todo_model is None:
            raise HTTPException(status_code=404, detail='Todo not found.')
    db.delete(todo_model)
    db.commit()
    return None  