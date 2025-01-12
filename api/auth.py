from _datetime import datetime, timedelta
import os
from functools import wraps

import jwt
from dotenv import load_dotenv
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from models.user import User

load_dotenv()

auth_bp = Blueprint('auth', __name__)

# Secret key for JWT
SECRET_KEY = os.getenv("SECRET_KEY")


@auth_bp.route('/login', methods=['GET'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Check if user exists in the database
    user = User.objects(username=username).first()
    if user and check_password_hash(user.password, password):
        # Generate JWT token
        token = jwt.encode(
            {'username': username, 'exp': datetime.utcnow() + timedelta(hours=1)},
            SECRET_KEY,
            algorithm='HS256'
        )
        return jsonify({'token': token}), 200

    return jsonify({'message': 'Invalid credentials'}), 401


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    username = data.get('username')
    password = data.get('password')

    # Check if user already exists in the database
    if User.objects(username=username).first():
        return jsonify({'message': 'User already exists'}), 400

    # Hash the password and save the user to the database
    hashed_password = generate_password_hash(password)
    user = User(username=username, password=hashed_password)
    user.save()

    return jsonify({'message': 'User registered successfully'}), 201


def token_required(pass_user=False):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = None
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                if auth_header.startswith("Bearer "):
                    token = auth_header.split(" ")[1]

            if not token:
                return jsonify({'message': 'Token is missing or improperly formatted!'}), 403

            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                if pass_user:
                    current_user = User.objects(username=data['username']).first()
                    if not current_user:
                        return jsonify({'message': 'User does not exist!'}), 404
                    kwargs['current_user'] = current_user
            except jwt.ExpiredSignatureError:
                return jsonify({'message': 'Token has expired!'}), 403
            except jwt.InvalidTokenError:
                return jsonify({'message': 'Token is invalid!'}), 403

            return f(*args, **kwargs)

        return decorated_function
    return decorator


@auth_bp.route('/refresh-token', methods=['POST'])
@token_required(pass_user=True)
def refresh_token(current_user):
    token = jwt.encode(
        {'username': current_user.username, 'exp': datetime.utcnow() + timedelta(hours=1)},
        SECRET_KEY,
        algorithm='HS256'
    )
    response = jsonify({'message': 'Token refreshed'})
    response.headers['Authorization'] = f'Bearer {token}'
    return response, 200
