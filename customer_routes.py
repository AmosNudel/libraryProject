from flask import Blueprint, jsonify, request
from models import db, Customer
from datetime import datetime

# Create a Blueprint for the customer routes
customer_bp = Blueprint('customer', __name__)

# Helper function to format a date into the desired string format (YYYY-MM-DD)
def format_date(date):
    return date.strftime("%Y-%m-%d") if date else None

# Read all customers
@customer_bp.route('/customers', methods=['GET'])
def get_customers():
    customers = Customer.query.all()
    customers_list = [{
        "id": customer.id,
        "name": customer.name,
        "city": customer.city,
        "age": customer.age,
        "join_date": format_date(customer.join_date),  
        "email": customer.email,
        "active": customer.active
    } for customer in customers]
    return jsonify(customers_list)

# Find a customer by ID
@customer_bp.route('/customers/<int:id>', methods=['GET'])
def get_customer_by_id(id):
    customer = Customer.query.get(id) 
    if not customer:
        return jsonify({"message": "Customer not found"}), 404

    customer_data = {
        "id": customer.id,
        "name": customer.name,
        "city": customer.city,
        "age": customer.age,
        "email": customer.email,
        "join_date": format_date(customer.join_date),  
        "active": customer.active
    }
    
    return jsonify(customer_data)

# Find active customer by name
@customer_bp.route('/customers/name/<name>', methods=['GET'])
def search_customer_by_name(name): 
    customers = Customer.query.filter(
    Customer.name.ilike(f"%{name}%"),
    Customer.active == True 
).all()
    
    if not customers:
        return jsonify({"message": "No customers found with that name"}), 404
    
    customers_list = [{
        "id": customer.id,
        "name": customer.name,
        "city": customer.city,
        "age": customer.age,
        "email": customer.email,
        "join_date": format_date(customer.join_date), 
        "active": customer.active
    } for customer in customers]
    return jsonify(customers_list)

# Find a customer by email
@customer_bp.route('/customers/email/<email>', methods=['GET'])
def search_customer_by_email(email): 
    customers = Customer.query.filter(Customer.email.ilike(f"%{email}%")).all()
    if not customers:
        return jsonify({"message": "No customers found with that email"}), 404
    
    customers_list = [{
        "id": customer.id,
        "name": customer.name,
        "city": customer.city,
        "age": customer.age,
        "email": customer.email,
        "join_date": format_date(customer.join_date),  
        "active": customer.active
    } for customer in customers]
    return jsonify(customers_list)

# Create a new customer
@customer_bp.route('/customers', methods=['POST'])
def add_customer():
    data = request.get_json()
    name = data.get('name')
    city = data.get('city')
    age = data.get('age')
    join_date_str = data.get('join_date')

    if not name or not city or not age or not join_date_str:
        return jsonify({"message": "Name, city, age, and join date are required"}), 400

    try:
        join_date = datetime.strptime(join_date_str, "%Y-%m-%d")
    except ValueError:
        return jsonify({"message": "Invalid join_date format. Use YYYY-MM-DD."}), 400

    new_customer = Customer(name=name, city=city, age=age, join_date=join_date, email=data.get('email'))
    db.session.add(new_customer)
    db.session.commit()

    return jsonify({"message": "Customer created", "id": new_customer.id}), 201

# Update a customer by ID
@customer_bp.route('/customers/update/id/<int:id>', methods=['PUT'])
def update_customer(id):
    customer = Customer.query.get(id)  
    if not customer:
        return jsonify({"message": "Customer not found"}), 404

    data = request.get_json()

    customer.name = data.get('name', customer.name)
    customer.city = data.get('city', customer.city)
    customer.age = data.get('age', customer.age)

    join_date_str = data.get('join_date')
    if join_date_str:
        try:
            join_date = datetime.strptime(join_date_str, "%Y-%m-%d")
            customer.join_date = join_date
        except ValueError:
            return jsonify({"message": "Invalid join_date format. Use YYYY-MM-DD."}), 400

    customer.email = data.get('email', customer.email)
    
    db.session.commit()
    return jsonify({"message": "Customer updated", "id": customer.id})

# Deactivate a customer
@customer_bp.route('/customers/<int:id>', methods=['PATCH'])
def deactivate_customer(id):
    customer = Customer.query.get(id)
    if not customer:
        return jsonify({"message": "Customer not found"}), 404
    customer.active = False
    db.session.commit()
    return jsonify({"message": "Customer deactivated", "id": customer.id})
