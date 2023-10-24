from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from datetime import datetime
import pymongo

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["banking_system"]
accounts_collection = db["accounts"]
transactions_collection = db["transactions"]

# FastAPI app
app = FastAPI()

# Pydantic models
class AccountCreate(BaseModel):
    holder_name: str
    initial_balance: float | int

class TransactionCreate(BaseModel):
    account_number: str
    transaction_type: str
    amount: float

class Account(BaseModel):
    account_number: str
    holder_name: str
    balance: float

class Transaction(BaseModel):
    transaction_id: str
    account_number: str
    transaction_type: str
    amount: float
    timestamp: datetime
class TradingTransactionCreate(BaseModel):
    account_number: str
    indices: List[str]
    option: str
    strike_price: int
    buy_sell: str

class TradingTransaction(Transaction):
    indices: List[str]
    option: str
    strike_price: int
    buy_sell: str
# Function to create a new account
# Function to create a new account
@app.post("/accounts/create", response_model=Account)
async def create_account(account_data: AccountCreate):
    account_number = datetime.now().strftime("%Y%m%d%H%M%S%f")
    account = {
        "account_number": account_number,
        "holder_name": account_data.holder_name,
        "balance": account_data.initial_balance
    }
    accounts_collection.insert_one(account)
    
    # Retrieve the updated account details from the database
    created_account = accounts_collection.find_one({"account_number": account_number})
    
    if created_account:
        return {**created_account}
    else:
        raise HTTPException(status_code=404, detail=f"Account {account_number} not found.")


# Function to get account details
@app.get("/accounts/{account_number}", response_model=Account)
async def get_account(account_number: str):
    account = accounts_collection.find_one({"account_number": account_number})
    if account:
        return {**account}
    else:
        raise HTTPException(status_code=404, detail=f"Account {account_number} not found.")

# Function to list all accounts
@app.get("/accounts", response_model=list[Account])
async def list_accounts():
    accounts = accounts_collection.find()
    return [{**account} for account in accounts]

# Function to create a transaction
@app.post("/transactions/create", response_model=Transaction)
async def create_transaction(transaction_data: TransactionCreate):
    account = accounts_collection.find_one({"account_number": transaction_data.account_number})
    if account:
        account_balance = account["balance"]
        if transaction_data.transaction_type == "Deposit":
            new_balance = account_balance + transaction_data.amount
        elif transaction_data.transaction_type == "Withdrawal":
            if account_balance >= transaction_data.amount:
                new_balance = account_balance - transaction_data.amount
            else:
                raise HTTPException(status_code=400, detail=f"Insufficient funds in account {transaction_data.account_number}.")
        else:
            raise HTTPException(status_code=400, detail="Invalid transaction type.")

        # Update account balance
        accounts_collection.update_one(
            {"account_number": transaction_data.account_number},
            {"$set": {"balance": new_balance}}
        )

        # Create a transaction record
        transaction_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
        transaction = {
            "transaction_id": transaction_id,
            **transaction_data.dict(),
            "timestamp": datetime.now()
        }
        transactions_collection.insert_one(transaction)
        return {**transaction}
    else:
        raise HTTPException(status_code=404, detail=f"Account {transaction_data.account_number} not found.")

# Function to list all transactions for an account
@app.get("/transactions/{account_number}", response_model=list[Transaction])
async def list_transactions(account_number: str):
    transactions = transactions_collection.find({"account_number": account_number})
    return [{**transaction} for transaction in transactions]

# Function to send money from one account to another
@app.post("/transactions/send_money", response_model=Transaction)
async def send_money(transaction_data: TransactionCreate, recipient_account_number: str):
    sender_account = accounts_collection.find_one({"account_number": transaction_data.account_number})
    recipient_account = accounts_collection.find_one({"account_number": recipient_account_number})
    
    if sender_account and recipient_account:
        sender_balance = sender_account["balance"]
        amount = transaction_data.amount

        if sender_balance >= amount:
            new_sender_balance = sender_balance - amount
            new_recipient_balance = recipient_account["balance"] + amount

            # Update sender's balance
            accounts_collection.update_one(
                {"account_number": transaction_data.account_number},
                {"$set": {"balance": new_sender_balance}}
            )

            # Update recipient's balance
            accounts_collection.update_one(
                {"account_number": recipient_account_number},
                {"$set": {"balance": new_recipient_balance}}
            )

            # Create a transaction record with sender and receiver information
            transaction_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
            transaction = {
                "transaction_id": transaction_id,
                "account_number": transaction_data.account_number,
                "transaction_type": "Send Money",
                "amount": amount,
                "sender_account_number": transaction_data.account_number,
                "recipient_account_number": recipient_account_number,
                "timestamp": datetime.now()
            }
            transactions_collection.insert_one(transaction)
            
            return {**transaction}
        else:
            raise HTTPException(status_code=400, detail=f"Insufficient funds in account {transaction_data.account_number}.")
    else:
        raise HTTPException(status_code=404, detail="One or both accounts not found.")


@app.post("/transactions/trading/create", response_model=TradingTransaction)
async def create_trading_transaction(trading_data: TradingTransactionCreate):
    # Validate account existence
    account = accounts_collection.find_one({"account_number": trading_data.account_number})
    if not account:
        raise HTTPException(status_code=404, detail=f"Account {trading_data.account_number} not found.")

    # Record the trading transaction
    transaction_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
    transaction = {
        "transaction_id": transaction_id,
        **trading_data.dict(),
        "timestamp": datetime.now()
    }
    transactions_collection.insert_one(transaction)

    return {**transaction}

# Function to list all trading transactions for an account
@app.get("/transactions/trading/{account_number}", response_model=list[TradingTransaction])
async def list_trading_transactions(account_number: str):
    transactions = transactions_collection.find({
        "account_number": account_number,
        "transaction_type": "Trading"
    })

    return [{**transaction} for transaction in transactions]