import os

import jwt
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template

import mongoDB_manager
# Import blueprints
from api import auth_bp, inventory_bp, transaction_bp
from mongoDB_manager import MongoConnectionHolder

# Load environment variables
load_dotenv()
# Import the database connection
MongoConnectionHolder.initialize_db()

# Create the Flask app instance
app = Flask(__name__,static_folder='static', template_folder='templates')

# Secret key for JWT
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(inventory_bp, url_prefix='/inventory')
app.register_blueprint(transaction_bp, url_prefix='/transaction')

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')

@app.route('/site.webmanifest')
def manifest():
    return app.send_static_file('site.webmanifest')

@app.before_request
def require_token():
    exempt_routes = [
        "/auth/login",
        "/auth/register",
        "/auth/refresh-token",  # Add any routes that do not require token
        "/",
        "/favicon.ico",
        "/static/*",
        "/templates/*"
        "/index.html",
        "/favicon.svg",
        "/favicon.png",
        "site.webmanifest",
        "/site.webmanifest",
        "/favicon-96x96.png",
        "/favicon-32x32.png"
    ]
    if request.path in exempt_routes or request.path.startswith('/static/'):
        return  # Skip token validation for exempt routes

    token = None
    if 'Authorization' in request.headers:
        auth_header = request.headers['Authorization']
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        return jsonify({'message': 'Token is missing or improperly formatted!'}), 403

    try:
        # Decode the JWT token
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        username = data['username']
        # Check if user exists in the database
        users_collection = mongoDB_manager.MongoConnectionHolder.get_db()["Users"]
        current_user = users_collection.find_one({"username": username})

        if not current_user:
            return jsonify({'message': 'User does not exist!'}), 404

        # Store current_user in request context for later use
        request.current_user = current_user
    except jwt.ExpiredSignatureError:
        return jsonify({'message': 'Token has expired!'}), 403
    except jwt.InvalidTokenError:
        return jsonify({'message': 'Token is invalid!'}), 403

if __name__ == '__main__':
    app.run(debug=True)
