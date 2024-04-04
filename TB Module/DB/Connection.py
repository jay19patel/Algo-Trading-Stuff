from pymongo import MongoClient

import os
from dotenv import load_dotenv
load_dotenv()


class MongoDBConnection:
    def __init__(self, host='localhost', port=27017):
        self.host = host
        self.port = port
        self.client = None
        self.connectionString = os.getenv("MONGODB_STRING")
        self.verion = 2
        self.db = None
    
    def connect(self):
        try:
            self.client = MongoClient(self.connectionString)
            print("Connected to MongoDB")
            self.db = self.client[f'TradBuddy_V{self.verion}_Worker_1']
            return self.db
        except Exception as e:
            print(f"Connection failed: {e}")
    
    def disconnect(self):
        try:
            if self.client:
                self.client.close()
                print("Disconnected from MongoDB")
        except Exception as e:
            print(f"Disconnection failed: {e}")

    def get_collection(self, collection_name):
        if self.db is None:
            print("Connecting to MongoDB...")
            self.connect()

        if self.db is not None:  # Check if db is not None explicitly
            print(f"Already connected to MongoDB {collection_name}")
            return self.db[collection_name]
        else:
            print("Failed to connect to MongoDB")
            return None

