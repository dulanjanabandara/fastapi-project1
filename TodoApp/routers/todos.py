from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Annotated
from starlette import status
from database import SessionLocal
from models import Todos
from .auth import get_current_user

router = APIRouter(
  prefix="/todos",
  tags=["todos"]
)

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()    

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
  title: str = Field(min_length=3)
  description: str = Field(min_length=3, max_length=100)
  priority: int = Field(gt=0, lt=6)
  complete: bool
  

@router.get("", status_code=status.HTTP_200_OK)
async def get_todos(user: user_dependency, db: db_dependency):
  if user is None:
    raise HTTPException(status_code=401, detail="Authentication failed")
  
  return db.query(Todos).filter(Todos.user_id == user.get("id")).all()


@router.get("/{todos_id}", status_code=status.HTTP_200_OK)
async def get_todo(user: user_dependency, db: db_dependency, todos_id: Annotated[int, Path(gt=0)]):
  if user is None:
    raise HTTPException(status_code=401, detail="Authentication failed")
  
  todo = db.query(Todos).filter(Todos.id == todos_id).filter(Todos.user_id == user.get("id")).first()
  
  if todo is not None:
    return todo
  raise HTTPException(status_code=404, detail="Todo not found")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
  # todo = Todos(
  #   title=todo_request.title,
  #   description=todo_request.description,
  #   priority=todo_request.priority,
  #   complete=todo_request.complete
  # )
  
  if user is None:
    raise HTTPException(status_code=401, detail="Authentication failed")
  
  todo = Todos(**todo_request.model_dump(), user_id=user.get("id"))
  
  db.add(todo)
  db.commit()



@router.put("/{todos_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest, todos_id: Annotated[int, Path(gt=0)]):
  if user is None:
    raise HTTPException(status_code=401, detail="Authentication failed")

  todo = db.query(Todos).filter(Todos.id == todos_id).filter(Todos.user_id == user.get("id")).first()
  if todo is None:
    raise HTTPException(status_code=404, detail="Todo not found")
  
  todo.title = todo_request.title
  todo.description = todo_request.description
  todo.priority = todo_request.priority
  todo.complete = todo_request.complete
  
  db.add(todo)
  db.commit()


@router.delete("/{todos_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todos_id: Annotated[int, Path(gt=0)]):
  if user is None:
    raise HTTPException(status_code=401, detail="Authentication failed")

  todo = db.query(Todos).filter(Todos.id == todos_id).filter(Todos.user_id == user.get("id")).first()

  if todo is None:
    raise HTTPException(status_code=404, detail="Todo not found")
  
  db.query(Todos).filter(Todos.id == todos_id).filter(Todos.user_id == user.get("id")).delete()
  db.commit()
