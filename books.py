from fastapi import Body,FastAPI

app = FastAPI()

BOOKS = [
    {'title': 'Title One', 'author': 'Author One', 'category': 'science'},
    {'title': 'Title Two', 'author': 'Author Two', 'category': 'science'},
    {'title': 'Title Three', 'author': 'Author Three', 'category': 'history'},
    {'title': 'Title Four', 'author': 'Author Four', 'category': 'math'},
    {'title': 'Title Five', 'author': 'Author Five', 'category': 'math'},
    {'title': 'Title Six', 'author': 'Author Two', 'category': 'math'}
]


@app.get("/books")
async def get_all_books():
    return BOOKS


@app.get("/books/{book_title}")
async def get_book(book_title: str):
    for book in BOOKS:
        if book.get('title').casefold() == book_title.casefold():
            return book
    return {"message": "Book not found"}


@app.get("/books/")
async def get_books_by_category(category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return


@app.get("/books/author/")
async def get_books_by_author_query(author: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == author.casefold():
            books_to_return.append(book)
    return books_to_return


@app.get("/books/{author_name}/")
async def get_books_by_author(author_name: str, category: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == author_name.casefold() and book.get('category').casefold() == category.casefold():
            books_to_return.append(book)
    return books_to_return


@app.get("/books/author/{author_name}")
async def get_books_by_author_path(author_name: str):
    books_to_return = []
    for book in BOOKS:
        if book.get('author').casefold() == author_name.casefold():
            books_to_return.append(book)
    return books_to_return


@app.post("/books")
async def create_book(new_book=Body()):
    BOOKS.append(new_book)
    return {"message": "Book added successfully", "data": new_book}


@app.put("/books/{book_title}")
async def update_book(book_title: str, update_book=Body()):
    for book in BOOKS:
        if book.get('title').casefold() == book_title.casefold():
            book.update(update_book)
            return {"message": "Book updated successfully", "data": book}
    return {"message": "Book not found"}


@app.delete("/books")
async def delete_book(book_title: str):
    for book in BOOKS:
        if book.get('title').casefold() == book_title.casefold():
            BOOKS.remove(book)
            return {"message": "Book deleted successfully"}
    return {"message": "Book not found"}
