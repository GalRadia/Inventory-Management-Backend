from api.auth import auth_bp
from api.inventory import inventory_bp, transaction_bp
from dotenv import load_dotenv
from flask import Flask
from flask_mongoengine import MongoEngine

from config import Config


load_dotenv()

# Initialize the MongoEngine extension
db = MongoEngine()

def create_app():
    app = Flask(__name__)

    # MongoDB configuration
    app.config.from_object(Config)

    # Initialize MongoEngine with the app
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(inventory_bp, url_prefix='/inventory')
    app.register_blueprint(transaction_bp, url_prefix='/transaction')

    return app
