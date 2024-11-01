from fastapi import FastAPI 
import uvicorn
from pydantic import BaseModel


app = FastAPI()


class Book(BaseModel):
   # Book_ID: int = None
    Bookname: str
    Author: str
    Year: str
    Available: bool


books = {
    1: {
        
        "Bookname": "Harry Potter och de vise sten",
        "Author": "J.K Rowling",
        "Year": "1997",
        "Available": True,
        "Book-ID": 1
        
    },

    2: {
        
        "Bookname": "Kafta på stranden",
        "Author": "Haruki Murakami",
        "Year": "2002",
        "Available": False,
        "Book_ID": 2
        
    }

}


@app.get("/show-library")
def show_library():
    return books

@app.get("/get-book/{book_number}")
def get_book(book_number: int):
    return books[book_number]

@app.post("/add-book/")
def add_book(book: Book): 
    book_id = len(books) + 1

    book_data = book.model_dump()
    book_data["Book_ID"] = book_id
    books[book_id] = book_data

    return book_data
    


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port= 8000)    
