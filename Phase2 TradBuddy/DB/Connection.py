import os
import pymongo
from dotenv import load_dotenv
load_dotenv()

def DBConnection_for_Broker():
    try:
        db_client = os.getenv("MONGODB_STRING")
        verion = 2
        mongo_connection = pymongo.MongoClient(db_client)[f'TradBuddy_V{verion}_Worker_1']
        account_collection = mongo_connection.get_collection("Account")
        notifications_collection = mongo_connection.get_collection("Notifications")
        orders_collection = mongo_connection.get_collection("Orders")
        profile_collection = mongo_connection.get_collection("Profile")
        transactions_collection = mongo_connection.get_collection("Transactions")
        profile_collection.find({})
        print("Database connection established successfully")
        return profile_collection, transactions_collection, account_collection, notifications_collection, orders_collection,mongo_connection
    except Exception as e:
        print(f"Failed to establish database connection: {e}")
        return None, None, None, None, None