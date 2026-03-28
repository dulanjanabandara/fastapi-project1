from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import Annotated
from starlette import status
from database import SessionLocal
from models import Users
from .auth import get_current_user

router = APIRouter(
  prefix="/users/me",
  tags=["users"]
)

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()    

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserVerification(BaseModel):
  password: str
  new_password: str = Field(min_length=6)


@router.get("", status_code=status.HTTP_200_OK)
async def get_users(db: db_dependency, user: user_dependency):
  if user is None or user.get("role") != "admin":
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
  
  return db.query(Users).filter(Users.id != user.get("id")).first()


@router.put("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user_verification: UserVerification, db: db_dependency, user: user_dependency):
  if user is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
  
  user = db.query(Users).filter(Users.id == user.get("id")).first()
  
  if not bcrypt_context.verify(user_verification.password, user.password):
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Error on password change")
  
  user.password = bcrypt_context.hash(user_verification.new_password)
  db.add(user)
  db.commit()


@router.put("/phonenumber/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
async def change_phone_number( db: db_dependency, user: user_dependency, phone_number: str):
  if user is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication failed")
  
  user = db.query(Users).filter(Users.id == user.get("id")).first()
  user.phone_number = phone_number
  db.add(user)
  db.commit()