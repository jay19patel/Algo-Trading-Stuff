from .Connection  import MongoDBConnection


mongo_connection = MongoDBConnection()

account_collection = mongo_connection.get_collection("Account")
notifications_collection = mongo_connection.get_collection("Notifications")
orders_collection = mongo_connection.get_collection("Orders")
profile_collection = mongo_connection.get_collection("Profile")
transactions_collection = mongo_connection.get_collection("Transactions")

