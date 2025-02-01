# auth.py
from datetime import datetime, timedelta
import os
from functools import wraps
import pytz
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


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Check if user exists in the database
    user = user_dao.get_by_username(username)
    timestamp = datetime.now(pytz.utc) + timedelta(hours=1)

    if user and check_password_hash(user.password, password):
        # Generate JWT token
        token = jwt.encode(
            {'username': username, 'exp': timestamp, 'role': user.role},
            SECRET_KEY,
            algorithm='HS256'
        )

        # Log the audit
        audit = audit_dao.get_by_username(username)
        if audit:
            audit_dao.update(audit.id, Audit(username=username, timestamp=timestamp, role=user.role))
        else:
            audit = Audit(username=username, timestamp=timestamp, role=user.role)
            audit_dao.create(audit)
        return jsonify({'message': 'Login successful', 'token': token, 'role': user.role}), 200
    return jsonify({'message': 'Invalid credentials'}), 401


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    user = User.from_dict(data)

    # Check if user already exists in the database
    if user_dao.get_by_username(user.username):
        return jsonify({'message': 'User already exists'}), 400

    # Hash the password and save the user to the database
    hashed_password = generate_password_hash(user.password)
    user = User(username=user.username, password=hashed_password, role=user.role)
    user_dao.create(user)

    return jsonify({'message': 'User registered successfully'}), 201


@auth_bp.route('/active', methods=['GET'])
def get_active_users():
    audits = audit_dao.get_all()
    users = []

    for audit in audits:
    # Example: Making audit.timestamp timezone-aware
        if audit.timestamp.tzinfo is None:  # Check if it's naive
            audit.timestamp = audit.timestamp.replace(tzinfo=pytz.utc)
        if audit.timestamp > datetime.now(pytz.utc):
            user = user_dao.get_by_username(audit.username)
            if user:
                users.append(user.to_dict())
    return jsonify(users), 200


@auth_bp.route('/users', methods=['GET'])
@manager_required
def get_all_users():
    users = user_dao.get_all()
    return jsonify([user.to_dict() for user in users]), 200


@auth_bp.route('/users/<username>', methods=['GET'])
def get_user(username):
    user = user_dao.get_by_username(username)
    if user:
        return jsonify(user.to_dict()), 200
    return jsonify({'message': 'User not found'}), 404


@auth_bp.route('/users/<username>', methods=['DELETE'])
@manager_required
def delete_user(username):
    user = user_dao.get_by_username(username)
    if user:
        user_dao.delete(username)
        return jsonify({'message': 'User deleted successfully'}), 200
    return jsonify({'message': 'User not found'}), 404


@auth_bp.route('/refresh-token', methods=['PUT'])
def refresh_token():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 403
    try:
        data = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=['HS256'])
        timestamp = datetime.now(pytz.utc) + timedelta(hours=1)
        new_token = jwt.encode(
            {'username': data['username'], 'exp': timestamp, 'role': data['role']},
            SECRET_KEY,
            algorithm='HS256'
        )
        audit = audit_dao.get_by_username(data['username'])
        audit_dao.update(audit.id, Audit(username=data['username'], timestamp=timestamp, role=data['role']))
        return jsonify({'message': 'Token refreshed successfully', 'token': new_token}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 403


@auth_bp.route('/audit/exp', methods=['GET'])
def get_exp():
    token = request.headers.get('Authorization')
    if not token:
        return jsonify({'message': 'Token is missing'}), 403
    try:
        timestamp = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=['HS256'])['exp']
        if timestamp:
            return jsonify({'exp': timestamp}), 200
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired'}), 403
