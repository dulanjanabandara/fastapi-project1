from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Annotated
from starlette import status
from database import SessionLocal
from models import Todos
from .auth import get_current_user

router = APIRouter(
  prefix="/admin/todos",
  tags=["admin"]
)

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()    

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("", status_code=status.HTTP_200_OK)
async def get_todos(user: user_dependency, db: db_dependency):
  if user is None or user.get("role") != "admin":
    raise HTTPException(status_code=401, detail="Authentication failed")
  
  return db.query(Todos).all()


@router.delete("/{todos_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todos_id: Annotated[int, Path(gt=0)]):
  if user is None or user.get("role") != "admin":
    raise HTTPException(status_code=401, detail="Authentication failed")
  
  todo = db.query(Todos).filter(Todos.id == todos_id).first()

  if todo is None:
    raise HTTPException(status_code=404, detail="Todo not found")
  
  db.query(Todos).filter(Todos.id == todos_id).delete()
  db.commit()