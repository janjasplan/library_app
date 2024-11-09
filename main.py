from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel
import os, json
from datetime import datetime

app = FastAPI()


class User( BaseModel ):
	"""
	En klass för att definera en användare. Vi använder oss av Basemodel från modulen pydantic för att validera indata. 
	Vi har två attribut här. Ett för användarnamn och ett för lösenordet. Detta för att användaren ska kunna logga in och låna böcker.

	"""
	username: str
	password: str

class Book( BaseModel ):
	"""
	En klass för att definera våra böcker. Här använder vi oss också av Basemodel för att validera indata.
	Här har vi fem attribut. Attributen är id-nummer, bokens titel, författare, året boken publicerades samt vem som har lånat boken. 
	Attributet renter sätts som default till None då boken till en början inte har någon ägare. 

	"""
	id: int
	title: str
	author: str
	year: int
	renter: User | None




#Vi ser efter filen books.json i vår nuvarande directory. 
#Vi öppnar upp den i läsläge, kodar av den samt skapar ett filobjekt (f) som refererar till filen.
#Sedan konverterar vi datan till json och lagrar det i variabeln Books.
#Ifall ingen fil finns så används ett lokalt dictionary med några förskapade böcker. 
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
	"""
	Här har vi en funktion för att spara ändringar som görs i vår variabel "Books" till en extern fil i vår nuvarande directory.
	Funktionen anropas i andra funktioner beroende på vilka ändringar som görs. 
	Vi ser först ifall filen finns och öppnar upp den i write läge. Detta för att skriva över allt innehåll ifall det finns något. 
	Annars skapas filen på nytt och allt uppdaterat innehåll i Books förs över. 
	
	"""
	with open('books.json', 'w', encoding='utf-8') as f:
		json.dump(Books, f, ensure_ascii=False, indent=4)

# Book rental
@app.get("/books")
def all_books():
	return Books

# Admin stuff.
@app.get("/get-book-by-title/{book_title}")
def get_book_by_title(book_title: str):
    for book_id, book in Books.items():
        if book_title.lower() == book["title"].lower():
            return book
        
    raise HTTPException(status_code = 404, detail = "Book not found")

@app.post("/add-book")
def add_book(book: Book):
    """
    Add a new book to the library.
    Args:
        book (Book): Pydantic model containing book details
    Returns:
        dict: Added book's details including assigned ID
    Raises:
        HTTPException: 400 if publication year is in the future
    """
    cur_year = datetime.now().year
    if book.year > cur_year:
        raise HTTPException(status_code=400, detail="Year is in the future")
    
    book_id = len(Books) + 1
    book_data = book.model_dump()
    book_data["id"] = book_id
    Books[book_id] = book_data
    save_books()  # Persist changes to storage
    return book_data

@app.delete("/delete-book")
def delete_book(book_id: int):
    """
    Delete a book from the library.
    Args:
        book_id (int): ID of the book to delete
    Returns:
        dict: Success message
    Raises:
        HTTPException: 404 if book not found
    """
    book_id_str = str(book_id)
    if Books.get(book_id_str) == None:
        raise HTTPException(status_code=404, detail="Book not found")
    del Books[book_id_str]
    save_books()  # Persist changes to storage
    return {"message": "Book deleted"}

@app.get("/books/{book_id}")
def get_book(book_id: str):
    """
    Get details of a specific book by ID.
    Args:
        book_id (str): ID of the book to retrieve
    Returns:
        dict: Book details
    Raises:
        HTTPException: 404 if book not found
    """
    book = Books.get(book_id)
    if book == None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.post("/books/{book_id}/rent")
def rent_book(book_id: str, renter: str):
    """
    Rent a book to a user.
    Args:
        book_id (str): ID of the book to rent
        renter (str): Name/ID of the person renting the book
    Returns:
        dict: Updated book details or error message if already rented
    Raises:
        HTTPException: 404 if book not found
    """
    book = Books.get(book_id)
    if book == None:
        raise HTTPException(status_code=404, detail="Book not found")
    
    if book['renter'] != None:
        return {"error": "Book is already rented"}
    
    Books[book_id]['renter'] = renter
    save_books()  # Persist changes to storage
    return book
 
@app.post("/books/{book_id}/return")
def return_book(book_id: str, renter: str):
    """
    Process a book return.
    Args:
        book_id (str): ID of the book being returned
        renter (str): Name/ID of the person returning the book
    Returns:
        dict: Updated book details or error message if return conditions not met
    Raises:
        HTTPException: 404 if book not found
    """
    book = Books.get(book_id)
    if book == None:
        raise HTTPException(status_code=404, detail="Book not found")
    if book['renter'] != renter:
        return {"error": "Book is not rented by you"}
    Books[book_id]['renter'] = None
    save_books()  # Persist changes to storage
    return book

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port = 8000)    
