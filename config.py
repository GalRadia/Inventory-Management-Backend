import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    MONGODB_SETTINGS = {
        'host': os.getenv('MONGO_URI'),
        'db': "Inventory"
    }
