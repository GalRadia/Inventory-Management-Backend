import os
from pymongo import MongoClient
from dotenv import load_dotenv
from pymongo.server_api import ServerApi

# Load environment variables
load_dotenv()

# Get the MongoDB URI from the environment
MONGO_URI = os.getenv('MONGO_URI')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'Inventory')
SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')


class MongoConnectionHolder:
    __db = None

    @staticmethod
    def initialize_db():
        """
        Initialize the database connection

        :return: MongoDB connection
        :rtype: Database
        """
        if MongoConnectionHolder.__db is None:
            try:
                # Create a new client and connect to the server
                client = MongoClient(MONGO_URI, server_api=ServerApi('1'))

                # Send a ping to confirm a successful connection
                client.admin.command('ping')
                print("Pinged your deployment. You successfully connected to MongoDB!")

                MongoConnectionHolder.__db = client[DATABASE_NAME]
            except Exception as e:
                print(e)
        return MongoConnectionHolder.__db

    @staticmethod
    def get_db():
        """
        Get the database connection

        :return: MongoDB connection
        :rtype: Database
        """
        if MongoConnectionHolder.__db is None:
            MongoConnectionHolder.initialize_db()

        return MongoConnectionHolder.__db
