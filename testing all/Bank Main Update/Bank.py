import pymongo
from datetime import datetime

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["banking_system"]
accounts_collection = db["accounts"]
transactions_collection = db["transactions"]

# Account class to represent user accounts
class Account:
    def __init__(self, account_number, holder_name, balance):
        self.account_number = account_number
        self.holder_name = holder_name
        self.balance = balance

# Transaction class to represent transactions
class Transaction:
    def __init__(self, account_number, transaction_type, amount):
        self.transaction_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        self.account_number = account_number
        self.transaction_type = transaction_type
        self.amount = amount
        self.timestamp = datetime.now()

# Function to create a new account
def create_account(account_number, holder_name, initial_balance):
    account = Account(account_number, holder_name, initial_balance)
    accounts_collection.insert_one(account.__dict__)
    print(f"Account created for {holder_name} with account number: {account_number}")

# Function to deposit funds into an account
def deposit(account_number, amount):
    account = accounts_collection.find_one({"account_number": account_number})
    if account:
        account_balance = account["balance"]
        new_balance = account_balance + amount
        accounts_collection.update_one(
            {"account_number": account_number},
            {"$set": {"balance": new_balance}}
        )
        transaction = Transaction(account_number, "Deposit", amount)
        transactions_collection.insert_one(transaction.__dict__)
        print(f"Deposited ${amount} into account {account_number}. New balance: ${new_balance}")
    else:
        print(f"Account {account_number} not found.")

# Function to withdraw funds from an account
def withdraw(account_number, amount):
    account = accounts_collection.find_one({"account_number": account_number})
    if account:
        account_balance = account["balance"]
        if account_balance >= amount:
            new_balance = account_balance - amount
            accounts_collection.update_one(
                {"account_number": account_number},
                {"$set": {"balance": new_balance}}
            )
            transaction = Transaction(account_number, "Withdrawal", amount)
            transactions_collection.insert_one(transaction.__dict__)
            print(f"Withdrew ${amount} from account {account_number}. New balance: ${new_balance}")
        else:
            print(f"Insufficient funds in account {account_number}.")
    else:
        print(f"Account {account_number} not found.")

# Function to check the balance of an account
def check_balance(account_number):
    account = accounts_collection.find_one({"account_number": account_number})
    if account:
        account_balance = account["balance"]
        print(f"Account {account_number} balance: ${account_balance}")
    else:
        print(f"Account {account_number} not found.")

# Example usage
create_account("12345", "John Doe", 1000)
deposit("12345", 500)
withdraw("12345", 200)
check_balance("12345")

# Close the MongoDB connection
client.close()