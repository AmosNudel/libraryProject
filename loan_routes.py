from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request
from models import db, Loan, Book, Customer

# Create a Blueprint for the loan routes
loan_bp = Blueprint('loan', __name__)

# Helper function to parse date from string (YYYY-MM-DD)
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None

# Helper function to format a date into the desired string format (YYYY-MM-DD)
def format_date(date):
    return date.strftime("%Y-%m-%d") if date else None

# Read all loans
@loan_bp.route('/loans', methods=['GET'])
def get_loans():
    loans = Loan.query.all()
    loans_list = [
        {
            "id": loan.id,
            "book_id": loan.book_id,
            "book_title": loan.book.title,  # Include book title
            "customer_id": loan.customer_id,
            "customer_name": loan.customer.name,  # Include customer name
            "loan_date": format_date(loan.loan_date),
            "return_date": format_date(loan.return_date),
            "active": loan.active,
        }
        for loan in loans
    ]
    return jsonify(loans_list)

# Get loan by ID
@loan_bp.route('/loans/<int:id>', methods=['GET'])
def get_loan_by_id(id):
    loan = Loan.query.get(id)
    if not loan:
        return jsonify({"message": "Loan not found"}), 404

    # Use the format_date function to format the dates
    loan_date = format_date(loan.loan_date)
    return_date = format_date(loan.return_date)

    return jsonify({
        "id": loan.id,
        "book_id": loan.book_id,
        "customer_id": loan.customer_id,
        "loan_date": loan_date,
        "return_date": return_date,
        "active": loan.active
    })

# Read active loans only
@loan_bp.route('/loans/only_active', methods=['GET'])
def get_active_loans():
    # Filter loans where active is True
    active_loans = Loan.query.filter_by(active=True).all()
    
    # Prepare the response with only active loans
    active_loans_list = [
        {
            "id": loan.id,
            "book_id": loan.book_id,
            "book_title": loan.book.title,  # Include book title
            "customer_id": loan.customer_id,
            "customer_name": loan.customer.name,  # Include customer name
            "loan_date": format_date(loan.loan_date),
            "return_date": format_date(loan.return_date),
            "active": loan.active,
        }
        for loan in active_loans
    ]
    
    return jsonify(active_loans_list)

# Read active loans for customers by name (with spaces allowed)
@loan_bp.route('/loans/active/<name>', methods=['GET'])
def get_active_loans_by_customer(name):
    # Query all customers with the given name
    customers = Customer.query.filter(Customer.name.ilike(f"%{name}%")).all()
    if not customers:
        return jsonify({"message": f"No customers found with name '{name}'"}), 404

    # Prepare a response for all matching customers
    response = []
    for customer in customers:
        # Get active loans for this customer
        active_loans = Loan.query.filter_by(customer_id=customer.id, active=True).all()
        loans_list = [
            {
                "id": loan.id,
                "book_id": loan.book_id,
                "book_title": loan.book.title,
                "loan_date": format_date(loan.loan_date),  # Format loan_date
                "return_date": format_date(loan.return_date),  # Format return_date
                "active": loan.active,
                "customer_name": customer.name  # Include customer name in each loan
            }
            for loan in active_loans
        ]

        response.append({
            "customer_id": customer.id,
            "customer_name": customer.name,
            "customer_city": customer.city,
            "customer_email": customer.email,
            "active_loans": loans_list,
        })

    return jsonify(response)

# Read all loans (active and inactive) for a customer by name
@loan_bp.route('/loans/history/<name>', methods=['GET'])
def get_all_loans_by_customer(name):
    # Query all customers with the given name
    customers = Customer.query.filter(Customer.name.ilike(f"%{name}%")).all()
    if not customers:
        return jsonify({"message": f"No customers found with name '{name}'"}), 404

    # Prepare a response for all matching customers
    response = []
    for customer in customers:
        # Get all loans (active and inactive) for this customer
        all_loans = Loan.query.filter_by(customer_id=customer.id).all()
        loans_list = [
            {
                "id": loan.id,
                "book_id": loan.book_id,
                "book_title": loan.book.title,
                "loan_date": format_date(loan.loan_date),  # Format loan_date
                "return_date": format_date(loan.return_date),  # Format return_date
                "active": loan.active,
                "customer_name": customer.name  # Include customer name in each loan
            }
            for loan in all_loans
        ]

        response.append({
            "customer_id": customer.id,
            "customer_name": customer.name,
            "customer_city": customer.city,
            "customer_email": customer.email,
            "all_loans": loans_list,
        })

    return jsonify(response)

# Create new loan by customer and book names
@loan_bp.route('/loans/name/', methods=['POST'])
def add_loan_by_name():
    data = request.get_json()
    book_name = data.get('book_name')  # Use book name instead of book_id
    customer_name = data.get('customer_name')  # Use customer name instead of customer_id
    loan_date_str = data.get('loan_date')  # Should be in the format "YYYY-MM-DD"

    # Validate required fields
    if not book_name or not customer_name or not loan_date_str:
        return jsonify({"message": "Book name, Customer name, and Loan Date are required"}), 400

    # Look up the book by name
    book = Book.query.filter_by(title=book_name).first()
    if not book:
        return jsonify({"message": f"Book with name '{book_name}' does not exist"}), 400

    # Look up the customers by name
    customers = Customer.query.filter(Customer.name.ilike(f"%{customer_name}%")).all()
    if not customers:
        return jsonify({"message": f"No customer found with name '{customer_name}'"}), 400

    # If multiple customers are found, return a list of customer IDs to help the user choose
    if len(customers) > 1:
        return jsonify({
            "message": "Multiple customers found with that name. Please use customer ID instead.",
            "customers": [{"id": c.id, "name": c.name} for c in customers]
        }), 400

    # Only one customer found, proceed with the loan creation
    customer = customers[0]

    # Parse the loan_date
    loan_date = parse_date(loan_date_str)
    if not loan_date:
        return jsonify({"message": "Invalid loan_date format. Use YYYY-MM-DD."}), 400

    # Determine the return_date based on the book type
    if book.type == 1:
        return_date = loan_date + timedelta(days=10)
    elif book.type == 2:
        return_date = loan_date + timedelta(days=5)
    elif book.type == 3:
        return_date = loan_date + timedelta(days=2)
    else:
        return jsonify({"message": "Invalid book type. Cannot calculate return date."}), 400

    # Create and save the new loan
    new_loan = Loan(book_id=book.id, customer_id=customer.id, loan_date=loan_date, return_date=return_date)
    db.session.add(new_loan)
    db.session.commit()

    return jsonify({
        "message": "Loan created successfully",
        "id": new_loan.id,
        "loan_date": format_date(new_loan.loan_date),  # Format loan_date for HTML input compatibility
        "return_date": format_date(new_loan.return_date)  # Format return_date for HTML input compatibility
    }), 201

# Update loan by ID
@loan_bp.route('/loans/update/<int:id>', methods=['PUT'])
def update_loan(id):
    loan = Loan.query.get(id)
    if not loan:
        return jsonify({"message": "Loan not found"}), 404

    data = request.get_json()
    book_id = data.get('book_id')
    customer_id = data.get('customer_id')

    # Validate book_id and customer_id if provided
    if book_id and not Book.query.get(book_id):
        return jsonify({"message": f"Book with ID {book_id} does not exist"}), 400
    if customer_id and not Customer.query.get(customer_id):
        return jsonify({"message": f"Customer with ID {customer_id} does not exist"}), 400

    # Update fields
    loan.book_id = book_id or loan.book_id
    loan.customer_id = customer_id or loan.customer_id

    # Handle loan_date and return_date with YYYY-MM-DD format
    loan_date_str = data.get('loan_date')
    return_date_str = data.get('return_date')

    if loan_date_str:
        loan_date = parse_date(loan_date_str)
        if not loan_date:
            return jsonify({"message": "Invalid loan_date format. Use YYYY-MM-DD."}), 400
        loan.loan_date = loan_date

    if return_date_str:
        return_date = parse_date(return_date_str)
        if not return_date:
            return jsonify({"message": "Invalid return_date format. Use YYYY-MM-DD."}), 400
        loan.return_date = return_date

    db.session.commit()
    return jsonify({"message": "Loan updated", "id": loan.id})

# Read overdue loans
@loan_bp.route('/loans/overdue', methods=['GET'])
def get_overdue_loans():
    today = datetime.utcnow()
    overdue_loans = Loan.query.filter(Loan.return_date < today, Loan.active == True).all()

    overdue_list = [
        {
            "id": loan.id,
            "book_id": loan.book_id,
            "book_title": loan.book.title,  # Assuming the `Book` model has a `title` field
            "customer_id": loan.customer_id,
            "customer_name": loan.customer.name,  # Assuming the `Customer` model has a `name` field
            "loan_date": format_date(loan.loan_date),
            "return_date": format_date(loan.return_date),
            "active": loan.active
        }
        for loan in overdue_loans
    ]
    
    return jsonify(overdue_list)

# Return a loan
@loan_bp.route('/loans/return/<int:id>', methods=['PATCH'])
def return_loan(id):
    loan = Loan.query.get(id)
    if not loan:
        return jsonify({"message": "Loan not found"}), 404

    if not loan.active:
        return jsonify({"message": "Loan is already marked as returned"}), 400

    loan.active = False
    db.session.commit()
    return jsonify({"message": f"Loan {id} marked as returned"}), 200
