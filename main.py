from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
import os, json
from datetime import datetime

app = FastAPI()

# Modell för användare
class User( BaseModel ):
    username: str
    password: str

class Book( BaseModel ):
    id: int
    title: str
    author: str
    year: int
    renter: User | None

# Load saved state
# or setup initial state
if os.path.exists('books.json'):
	with open('books.json', 'r', encoding='utf-8') as f:
		Books: dict[str, Book] = json.load(f)
else:
	Books: dict[str, Book] = {
		"1": {"id": 1, "title": "Harry Potter och de vise sten", "author": "J.K Rowling", "year": 1997, "renter": None},
		"2": {"id": 2, "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "year": 1925, "renter": None},
		"3": {"id": 3, "title": "Kafta på stranden", "author": "Haruki Murakami", "year": 2002, "renter": None},
		"4": {"id": 4, "title": "Sagan om ringen", "author": "J.R.R. Tolkien", "year": 1959, "renter": None},
		"5": {"id": 5, "title": "Holes", "author": "Louis Sachar", "year": 1998, "renter": None},
	}

def save_books():
	with open('books.json', 'w', encoding='utf-8') as f:
		json.dump(Books, f, ensure_ascii=False, indent=4)

# Admin stuff.
@app.get("/get-book-by-title/{book_title}")
def get_book_by_title(book_title: str):
    for book_id, book in Books.items():
        if book_title.lower() == book["title"].lower():
            return book
        
    raise HTTPException(status_code = 404, detail = "Book not found")

@app.post("/add-book")
def add_book(book: Book):

	cur_year = datetime.now().year
	if book.year > cur_year:
		raise HTTPException(status_code = 400, detail = "Year is in the future")

	book_id = len(Books) + 1
	book_data = book.model_dump()
	book_data["id"] = book_id
	Books[book_id] = book_data
	save_books()

	return book_data

@app.post("/delete-book/{book_id}")
def delete_book(book_id: int):
	book_id_str = str( book_id )
	if Books.get( book_id_str ) == None:
		raise HTTPException(status_code = 404, detail = "Book not found")

	del Books[book_id_str]
	save_books()
	return {"message": "Book deleted"}

# Book rental
@app.get("/books")
def read_root():
	return Books

@app.get("/books/{book_id}")
def get_book(book_id: str):
	book = Books.get( book_id )
	if book == None:
		raise HTTPException(status_code = 404, detail = "Book not found")

	return book

@app.post("/books/{book_id}/rent")
def rent_book(book_id: str, renter: str):
	book = Books.get( book_id )
	if book == None:
		raise HTTPException(status_code = 404, detail = "Book not found")
	
	if book['renter'] != None:
		return {"error": "Book is already rented"}
	
	Books[book_id]['renter'] = renter
	save_books()
	return book

@app.post("/books/{book_id}/return")
def return_book(book_id: str, renter: str):
	book = Books.get( book_id )
	if book == None:
		raise HTTPException(status_code = 404, detail = "Book not found")

	if book['renter'] != renter:
		return {"error": "Book is not rented by you"}

	Books[book_id]['renter'] = None
	save_books()
	return book


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port = 8000)    
