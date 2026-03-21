from typing import Optional, Annotated
from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, Field
from starlette import status

app = FastAPI()

class Book:
  id: int
  title: str
  author: str
  description: str
  rating: float
  published_date: int
  
  def __init__(self, id, title, author, description, rating, published_date):
    self.id = id
    self.title = title
    self.author = author
    self.description = description
    self.rating = rating
    self.published_date = published_date


class BookRequest(BaseModel):
  # id: Optional[int] = None
  id: Optional[int] = Field(default=None, description="ID is not needed on create")
  title: str = Field(min_length=3)
  author: str = Field(min_length=1)
  description: str = Field(min_length=1,max_length=100)
  rating: float = Field(ge=0.0, le=5.0)
  published_date: int = Field(gt=1999, lt=2031)

  model_config = {
    "json_schema_extra": {
      "example": {
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "description": "A novel about the American dream.",
        "rating": 4.5,
        "published_date": 2025
      }
    } 
  }


BOOKS = [
  Book(1, "The Great Gatsby", "F. Scott Fitzgerald", "A novel about the American dream.", 4.5, 2025),
  Book(2, "To Kill a Mockingbird", "Harper Lee", "A novel about racial injustice in the Deep South.", 4.8, 2020),
  Book(3, "1984", "George Orwell", "A dystopian novel about totalitarianism.", 4.7, 2019),
  Book(4, "The Catcher in the Rye", "J.D. Salinger", "A coming-of-age novel about teenage angst.", 4.8, 2021),
  Book(5, "Pride and Prejudice", "Jane Austen", "A classic novel about love and society.", 4.9, 2021)
]

@app.get("/books/", status_code=status.HTTP_200_OK)
def get_all_books(book_rating: Annotated[Optional[float], Query(ge=0, le=5)] = None, published_date: Annotated[Optional[int], Query(gt=1999, lt=2031)] = None):
  results = BOOKS
  if book_rating is not None:
    results = [book for book in results if book.rating == book_rating]
  if published_date is not None:
    results = [book for book in results if book.published_date == published_date]
  return results


@app.get(
  "/books/{book_id}",
  status_code=status.HTTP_200_OK,
  responses={
    404: {
      "description": "Book not found",
      "content": {
        "application/json": {
          "example": {"message": "Book not found"}
        }
      }
    }
  }
)
async def get_book(book_id: Annotated[int, Path(gt=0)]):
  for book in BOOKS:
    if book.id == book_id:
      return {"message": "Book found", "data": book}
  raise HTTPException(status_code=404, detail="Book not found")


@app.post("/books", status_code=status.HTTP_201_CREATED)
async def create_book(book_request: BookRequest):
  new_book = Book(**book_request.model_dump())
  BOOKS.append(find_book_id(new_book))
  return {"message": "Book added successfully", "data": new_book} 


@app.put(
  "/books/{book_id}",
  status_code=status.HTTP_200_OK,
  responses={
    404: {
      "description": "Book not found",
      "content": {
        "application/json": {
          "example": {"message": "Book not found"}
        }
      }
    }
  }
)
async def update_book(book_id: Annotated[int, Path(gt=0)], book_request: BookRequest):
  for book in BOOKS:
    if book.id == book_id:
      book.title = book_request.title
      book.author = book_request.author
      book.description = book_request.description
      book.rating = book_request.rating
      return {"message": "Book updated successfully", "data": book}
  raise HTTPException(status_code=404, detail="Book not found")


@app.delete(
  "/books/{book_id}",
  status_code=status.HTTP_204_NO_CONTENT,
  responses={
    404: {
      "description": "Book not found",
      "content": {
        "application/json": {
          "example": {"message": "Book not found"}
        }
      }
    }
  }
)
async def delete_book(book_id: Annotated[int, Path(gt=0)]):
  for book in BOOKS:
    if book.id == book_id:
      BOOKS.remove(book)
      return {"message": "Book deleted successfully"}
  raise HTTPException(status_code=404, detail="Book not found")


def find_book_id(book: Book):
  book.id = 1 if len(BOOKS) == 0 else BOOKS[-1].id + 1
  # if len(BOOKS) > 0:
  #   book.id = BOOKS[-1].id + 1
  # else:    
  #   book.id = 1
  return book

