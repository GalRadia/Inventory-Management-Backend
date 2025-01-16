# auth.py
from datetime import datetime, timedelta
import os
from functools import wraps

import jwt
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from models.user import User
from models.audit import Audit
from dal import UserDAO, AuditDAO, TransactionDAO, ItemDAO
from mongoDB_manager import MongoConnectionHolder

load_dotenv()

auth_bp = Blueprint('auth', __name__)

SECRET_KEY = os.getenv("SECRET_KEY")

db = MongoConnectionHolder.get_db()

user_dao = UserDAO(db)
item_dao = ItemDAO(db)
transaction_dao = TransactionDAO(db)
audit_dao = AuditDAO(db)
@auth_bp.route('/login', methods=['GET'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Check if user exists in the database
    user = user_dao.get_by_username(username)
    timestamp = datetime.utcnow() + timedelta(hours=1)

    if user and check_password_hash(user.password, password):
        # Generate JWT token
        token = jwt.encode(
            {'username': username, 'exp': timestamp, 'role': user.role},
            SECRET_KEY,
            algorithm='HS256'
        )

        # Log the audit
        audit = Audit(username=username, timestamp=timestamp, role=user.role)
        audit_dao.create(audit)
        return jsonify({'token': token}), 200

    return jsonify({'message': 'Invalid credentials'}), 401


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')
    role = data.get('role')

    # Check if user already exists in the database
    if user_dao.get_by_username(username):
        return jsonify({'message': 'User already exists'}), 400

    # Hash the password and save the user to the database
    hashed_password = generate_password_hash(password)
    user = User(username=username, password=hashed_password, role=role)
    user_dao.create(user)

    return jsonify({'message': 'User registered successfully'}), 201


@auth_bp.route('/refresh-token', methods=['PUT'])
def refresh_token():
    current_user = request.current_user  # Assumes 'current_user' is set by 'manager_required' decorator
    timestamp = datetime.utcnow() + timedelta(hours=1)

    token = jwt.encode(
        {'username': current_user.username, 'exp': timestamp, 'role': current_user.role},
        SECRET_KEY,
        algorithm='HS256'
    )

    # Update the audit record
    audit = audit_dao.get_by_username(current_user.username)
    if audit:
        audit.update(timestamp=timestamp)

    response = jsonify({'message': 'Token refreshed'})
    response.headers['Authorization'] = f'Bearer {token}'
    return response, 200


def manager_required(f):
    """Decorator to check if the current user is a manager."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract token from Authorization header
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]

        if not token:
            return jsonify({'message': 'Token is missing or improperly formatted!'}), 403

        try:
            # Decode the token
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            current_user = user_dao.get_by_username(data['username'])
            if not current_user:
                return jsonify({'message': 'User does not exist!'}), 404

            # Check if the user is a manager
            if current_user.role != 'manager':
                return jsonify({'message': 'You must be a manager to access this resource!'}), 403

            # Store current_user in request context for later use
            request.current_user = current_user

        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token has expired!'}), 403
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token is invalid!'}), 403

        # Call the original function if everything is fine
        return f(*args, **kwargs)

    return decorated_function
