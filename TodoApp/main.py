from typing import Annotated
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends, HTTPException, Path
import models
from models import Todos
from database import SessionLocal, engine
from starlette import status

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()    


db_dependency = Annotated[Session, Depends(get_db)]

class TodoRequest(BaseModel):
  title: str = Field(min_length=3)
  description: str = Field(min_length=3, max_length=100)
  priority: int = Field(gt=0, lt=6)
  complete: bool
  

@app.get("/todos", status_code=status.HTTP_200_OK)
async def get_todos(db: db_dependency):
  return db.query(Todos).all()

@app.get("/todos/{todos_id}", status_code=status.HTTP_200_OK)
async def get_todo(db: db_dependency, todos_id: Annotated[int, Path(gt=0)]):
  todo = db.query(Todos).filter(Todos.id == todos_id).first()
  
  if todo is not None:
    return todo
  raise HTTPException(status_code=404, detail="Todo not found")
  

@app.post("/todos", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
  # todo = Todos(
  #   title=todo_request.title,
  #   description=todo_request.description,
  #   priority=todo_request.priority,
  #   complete=todo_request.complete
  # )
  todo = Todos(**todo_request.model_dump())
  
  db.add(todo)
  db.commit()
  
  
@app.put("/todos/{todos_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, todo_request: TodoRequest, todos_id: Annotated[int, Path(gt=0)]):
  todo = db.query(Todos).filter(Todos.id == todos_id).first()
  print(todo)
  print(todo_request)
  if todo is None:
    raise HTTPException(status_code=404, detail="Todo not found")
  
  todo.title = todo_request.title
  todo.description = todo_request.description
  todo.priority = todo_request.priority
  todo.complete = todo_request.complete
  
  db.add(todo)
  db.commit()
  
  
@app.delete("/todos/{todos_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todos_id: Annotated[int, Path(gt=0)]):
  todo = db.query(Todos).filter(Todos.id == todos_id).first()
  
  if todo is None:
    raise HTTPException(status_code=404, detail="Todo not found")
  
  db.query(Todos).filter(Todos.id == todos_id).delete()
  db.commit()