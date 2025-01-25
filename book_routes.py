from flask import Blueprint, jsonify, request
from models import db, Book  # Import your `db` and `Book` model from the main app

# Create a Blueprint for the books routes
books_bp = Blueprint('books', __name__)

# Read all books
@books_bp.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    books_list = [{"id": book.id, "title": book.title,
                "author": book.author, 
                "year_published": book.year_published,
                "type": book.type,
                "image": book.image,
                "active": book.active} for book in books]
    return jsonify(books_list)

# Find a book by ID
@books_bp.route('/books/<int:id>', methods=['GET'])
def search_book_by_id(id):
    # Search for the book with the given ID
    book = Book.query.get(id)  # This will fetch the book by its primary key (ID)
    
    if not book:
        return jsonify({"message": "Book not found"}), 404
    
    # Prepare the book data to be returned
    book_data = {
        "id": book.id,
        "title": book.title,
        "author": book.author,
        "year_published": book.year_published,
        "type": book.type,
        "image": book.image,
        "active": book.active
    }
    
    return jsonify(book_data)

# Find a book by name (title)
@books_bp.route('/books/<title>', methods=['GET'])
def search_book_by_name(title):
    # Search for book with the given title
    books = Book.query.filter(Book.title.ilike(f"%{title}%")).all()
    
    if not books:
        return jsonify({"message": "No books found with that title"}), 404
    
    book_display = [{"id": book.id, "title": book.title,
                     "author": book.author, 
                     "year_published": book.year_published,
                     "type": book.type,
                     "image": book.image,
                     "active": book.active} for book in books]
    
    return jsonify(book_display)

# Create a new book
@books_bp.route('/books', methods=['POST'])
def add_book():
    data = request.get_json()
    title = data.get('title')
    author = data.get('author')
    year_published = data.get('year_published')
    type = data.get('type')
    image = data.get('image')
    if not title or not author or not year_published or not type or not image:
        return jsonify({"message": "Tile, Author, Year Published, Type and Image are required"}), 400
    new_book = Book(title=title, author=author, year_published=year_published,type=type,image=image)
    db.session.add(new_book)
    db.session.commit()
    return jsonify({"message": "Book created", "id": new_book.id}), 201

# Update a book by ID
@books_bp.route('/books/<int:book_id>', methods=['PUT'])
def update_book(book_id):
    # Fetch the book with the given ID
    book = Book.query.get(book_id)  # This fetches the book by its ID

    if not book:
        return jsonify({"message": "Book not found"}), 404
    
    # Get the data to update from the request body
    data = request.get_json()

    # Update the book attributes
    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    book.year_published = data.get('year_published', book.year_published)
    book.type = data.get('type', book.type)
    book.image = data.get('image', book.image)  # Update the image URL if provided
    
    # Commit the changes to the database
    db.session.commit()
    
    return jsonify({"message": "Book updated", "id": book.id})

# Deactivate a book
@books_bp.route('/books/<int:id>', methods=['PATCH'])
def deactivate_book(id):
    book = Book.query.get(id)
    if not book:
        return jsonify({"message": "Book not found"}), 404
    book.active = False
    db.session.commit()
    return jsonify({"message": "Book deactivated", "id": book.id})