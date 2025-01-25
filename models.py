from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta # timedelta is used for the test functions

# Initialize the database
db = SQLAlchemy()

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    year_published = db.Column(db.Integer, nullable=False)
    type = db.Column(db.Integer, nullable=False)  # 1 = Up to 10 days, 2 = Up to 5 days, 3 = Up to 2 days
    image = db.Column(db.String(255), nullable=True)  # URL or path to the book's image
    active = db.Column(db.Boolean, default=True, nullable=False)  # Indicates if the book is active

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    join_date = db.Column(db.DateTime, nullable=True)  # Set to nullable to allow manual input
    active = db.Column(db.Boolean, default=True, nullable=False)  # Indicates if the customer is active

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)  # Foreign key to Book
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)  # Foreign key to Customer
    loan_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)  # Date when the loan was made
    return_date = db.Column(db.DateTime, nullable=True)  # Date when the book is returned
    active = db.Column(db.Boolean, default=True, nullable=False)  # Indicates if the loan is active

    # Relationships
    book = db.relationship('Book', backref=db.backref('loans', lazy=True))
    customer = db.relationship('Customer', backref=db.backref('loans', lazy=True))





'''Below are test methods for each model'''
# Book moudel test
def test_book():
    new_book = Book(
    title="The Great Gatsby",
    author="F. Scott Fitzgerald",
    year_published=1925,
    type=1,  # Up to 10 days
    image="https://upload.wikimedia.org/wikipedia/commons/7/7a/The_Great_Gatsby_Cover_1925_Retouched.jpg",
    active=True
)
    db.session.add(new_book)
    db.session.commit()
    print("Book added:", new_book)


# Customer moudel test
def test_customer():
    custom_join_date = datetime(2023, 5, 15)  # Manual join date
    new_customer = Customer(
        name="Jane Doe",
        city="New York",
        age=29,
        email="janedoe@example.com",
        join_date=custom_join_date,  # Manually provided date
        active=True
    )
    db.session.add(new_customer)
    db.session.commit()
    print("Customer added:", new_customer)


# # Loan moudel test
def test_loan():
    # Fetch an existing book and customer from the database
    book = Book.query.filter_by(title="The Great Gatsby").first()
    customer = Customer.query.filter_by(email="janedoe@example.com").first()

    # Determine the loan period based on the book type
    loan_period = 10 if book.type == 1 else 5 if book.type == 2 else 2

    # Calculate the return date
    loan_date = datetime(2023, 12, 1)  # Example loan date
    return_date = loan_date + timedelta(days=loan_period)

    # Create a loan for the book and customer
    loan = Loan(
        book_id=book.id,
        customer_id=customer.id,
        loan_date=loan_date,
        return_date=return_date,
        active=True
    )

    db.session.add(loan)
    db.session.commit()
    print("Loan created:", loan)