from fastapi import FastAPI 
import uvicorn
from pydantic import BaseModel


app = FastAPI()


class Book(BaseModel):
    Book_title: str
    Author: str
    Year: str
    Available: bool


books = {
    1: {
        
        "Book_title": "Harry Potter och de vise sten",
        "Author": "J.K Rowling",
        "Year": "1997",
        "Available": True,
        "Book-ID": 1
        
    },

    2: {
        
        "Book_title": "Kafta på stranden",
        "Author": "Haruki Murakami",
        "Year": "2002",
        "Available": True,
        "Book_ID": 2
        
    },

    3: {
        
        "Book_title": "Sagan om ringen",
        "Author": "J.R.R. Tolkien",
        "Year": "1959",
        "Available": True,
        "Book_ID": 3
        
    }


}


@app.get("/")
def main_page():
    return {"message": "Welcome to the main page!"}


@app.get("/show-library")
def show_library():
    return books

@app.get("/get-book/{book_title}")
def get_book(book_title: str):
    for book_id, book in books.items():
        if book_title.lower() == book["Book_title"].lower():
            return (f"{book_title} is available!")
        
    return (f"We dont have that book!")

@app.post("/add-book")
def add_book(book: Book): 
    book_id = len(books) + 1

    book_data = book.model_dump()
    book_data["Book_ID"] = book_id
    books[book_id] = book_data

    return book_data
    


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port= 5000)    
