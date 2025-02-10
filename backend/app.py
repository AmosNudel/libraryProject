from flask import Flask, jsonify
from flask_cors import CORS
import logging
from models import db #, test_book, test_customer, test_loan 
from book_routes import books_bp 
from customer_routes import customer_bp 
from loan_routes import loan_bp

# Initialize the Flask application
app = Flask(__name__)
CORS(app, methods=["GET", "POST", "PUT", "PATCH"]) 

# Configure the SQLite database URI
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///library.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy with the app
db.init_app(app)  

# Set up logging
log_file = 'logger.log'  
logging.basicConfig(level=logging.WARNING,
                    format='%(asctime)s - %(levelname)s - %(message)s',  
                    handlers=[
                        logging.FileHandler(log_file), 
                        logging.StreamHandler()  
                    ])
logger = logging.getLogger(__name__)

# Register the Blueprint
app.register_blueprint(books_bp)  
app.register_blueprint(customer_bp)  
app.register_blueprint(loan_bp)  

@app.route('/')
def hello_world():
    return jsonify({'message': 'server is live'})

if __name__ == '__main__':
    '''Kept as a comment for review purposes'''
    # with app.app_context():
    #     db.create_all()
    #     test_book()
    #     test_customer()
    #     test_loan()
    app.run(debug=True)