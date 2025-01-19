import os

import jwt
from werkzeug.security import generate_password_hash

from api.auth import auth_bp
from api.inventory import inventory_bp, transaction_bp
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_mongoengine import MongoEngine
from config import Config
from models.user import User

load_dotenv()

# Initialize the MongoEngine extension
db = MongoEngine()

# Create the Flask app instance
app = Flask(__name__)

# MongoDB configuration
app.config.from_object(Config)

# Initialize MongoEngine with the app
db.init_app(app)

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(inventory_bp, url_prefix='/inventory')
app.register_blueprint(transaction_bp, url_prefix='/transaction')

@app.route('/')
def home():
    return jsonify({'message': 'Welcome to the Inventory Management System!','db':os.getenv('MONGO_URI')})

@app.before_request
def require_token():
    exempt_routes = [
        "/auth/login",
        "/auth/register",
        "/auth/refresh-token",  # Add any routes that do not require token
        "/",
        "/register"
    ]
    if request.path in exempt_routes:
        return  # Skip token validation for exempt routes

    token = None
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        return jsonify({'message': 'Token is missing or improperly formatted!'}), 403

    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        current_user = User.objects(username=data['username']).first()
        if not current_user:
            return jsonify({'message': 'User does not exist!'}), 404
        # Store current_user in request context for later use
        request.current_user = current_user
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired!'}), 403
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Token is invalid!'}), 403

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    role = data.get('role')
    # Check if user already exists in the database
    if User.objects(username=username).first():
        return jsonify({'message': 'User already exists'}), 400

    # Hash the password and save the user to the database
    hashed_password = generate_password_hash(password)
    user = User(username=username, password=hashed_password, role=role)
    user.save()

    return jsonify({'message': 'User registered successfully'}), 201

if __name__ == '__main__':
    app.run(debug=True)