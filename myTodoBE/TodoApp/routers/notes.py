from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

try:
    from ..dependencies import db_dependency, get_current_user
    from ..models import Note, User
    from ..schemas import NoteCreate, NoteResponse, NoteUpdate
except ImportError:
    from dependencies import db_dependency, get_current_user
    from models import Note, User
    from schemas import NoteCreate, NoteResponse, NoteUpdate

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("", response_model=list[NoteResponse], status_code=status.HTTP_200_OK)
async def read_notes(db: db_dependency, current_user: Annotated[User, Depends(get_current_user)]):
    return db.query(Note).filter(Note.user_id == current_user.id).all()


@router.get("/{note_id}", response_model=NoteResponse, status_code=status.HTTP_200_OK)
async def read_note(
    db: db_dependency,
    note_id: int = Path(gt=0),
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    note_model = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if note_model is not None:
        return note_model
    raise HTTPException(status_code=404, detail="Note not found")


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    db: db_dependency,
    note_request: NoteCreate,
    current_user: Annotated[User, Depends(get_current_user)],
):
    note_model = Note(
        title=note_request.title,
        content=note_request.content,
        todo_id=note_request.todo_id,
        user_id=current_user.id,
    )
    db.add(note_model)
    db.commit()
    db.refresh(note_model)
    return note_model


@router.put("/{note_id}", response_model=NoteResponse, status_code=status.HTTP_200_OK)
async def update_note(
    db: db_dependency,
    note_request: NoteUpdate,
    note_id: int = Path(gt=0),
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    note_model = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if note_model is None:
        raise HTTPException(status_code=404, detail="Note not found.")

    note_model.title = note_request.title
    note_model.content = note_request.content
    db.add(note_model)
    db.commit()
    return note_model


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    db: db_dependency,
    note_id: int = Path(gt=0),
    current_user: Annotated[User, Depends(get_current_user)] = None,
):
    note_model = db.query(Note).filter(Note.id == note_id, Note.user_id == current_user.id).first()
    if note_model is None:
        raise HTTPException(status_code=404, detail="Note not found.")

    db.delete(note_model)
    db.commit()
    return None
