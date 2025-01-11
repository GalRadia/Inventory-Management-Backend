from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import pytz
import datetime
from dotenv import load_dotenv
import os

from models.user import User

load_dotenv()

auth_bp = Blueprint('auth', __name__)

# Secret key for JWT
SECRET_KEY = os.getenv("SECRET_KEY")

@auth_bp.route('/login', methods=['GET'])
def login():
    username = request.args.get('username')
    password = request.args.get('password')

    # Check if user exists in the database
    user = User.objects(username=username).first()
    if user and check_password_hash(user.password, password):
        # Generate JWT token
        token = jwt.encode(
            {'username': username, 'exp': datetime.utcnow()+ datetime.timedelta(hours=1)},
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
