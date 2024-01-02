import streamlit as st
import pymongo
from datetime import datetime
import pandas as pd

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["banking_system"]
accounts_collection = db["accounts"]
transactions_collection = db["transactions"]
trading_collection = db["trading_transactions"]

brokerage_charge = 50
selected_account = "123456789"

# Streamlit app
st.title("Banking and Trading Dashboard")


st.sidebar.header("Total Balance")
if selected_account:
    account = accounts_collection.find_one({"account_number": selected_account})
    if account:
        st.sidebar.subheader(f"${account['balance']:.2f}")
    else:
        st.sidebar.warning("Account not found.")


# Sidebar
st.sidebar.header("Options")

option = st.sidebar.selectbox("Select an option", ["Home", "View Withdrawal Data", "View Deposit Data", "Withdraw", "Deposit", "Trading", "View Trading Data", "Open Positions"])

# Account selection dropdown in the sidebar


# Function to update a pending trading transaction to "Done" status with exit time and price in the database
def update_to_done(transaction_id, exit_time, exit_price,exit_qnt,pnl,entry_buy_sell):
    trading_collection.update_one(
        {"_id": transaction_id},
        {"$set": {
            "exit_time": exit_time,
            "exit_price": exit_price,
            "Status": "Done",  # Update the "Status" to "Done" in the database
            "Exit_quantity": exit_qnt , # Update the "Status" to "Done" in the database
            "Profit/Loss": pnl ,
            "Exit_buy_sell":entry_buy_sell # Update the "Status" to "Done" in the database
        }}
    )

# Home page
if option == "Home":
    st.header("Total Balance")
    if selected_account:
        account = accounts_collection.find_one({"account_number": selected_account})
        if account:
            st.subheader(f"${account['balance']:.2f}")
        else:
            st.warning("Account not found.")

# View Withdrawal Data page (unchanged)
elif option == "View Withdrawal Data":
    st.header("Withdrawal Data")
    if selected_account:
        withdrawal_transactions = transactions_collection.find({
            "account_number": selected_account,
            "transaction_type": "Withdrawal"
        })
        withdrawal_data = []
        for transaction in withdrawal_transactions:
            withdrawal_data.append(transaction)
        st.dataframe(pd.DataFrame(withdrawal_data))
    else:
        st.warning("Please select an account from the sidebar.")

# View Deposit Data page (unchanged)
elif option == "View Deposit Data":
    st.header("Deposit Data")
    if selected_account:
        deposit_transactions = transactions_collection.find({
            "account_number": selected_account,
            "transaction_type": "Deposit"
        })
        deposit_data = []
        for transaction in deposit_transactions:
            deposit_data.append(transaction)
        st.dataframe(pd.DataFrame(deposit_data))
    else:
        st.warning("Please select an account from the sidebar.")

# Withdraw page (unchanged)
elif option == "Withdraw":
    st.header("Withdraw Money")
    if selected_account:
        account = accounts_collection.find_one({"account_number": selected_account})
        if account:
            st.subheader("Account Details")
            st.write(f"Account Number: {account['account_number']}")
            st.write(f"Current Balance: ${account['balance']}")
            withdraw_amount = st.number_input("Enter the amount to withdraw", min_value=0.01)
            if st.button("Withdraw"):
                if account["balance"] >= withdraw_amount:
                    new_balance = account["balance"] - withdraw_amount
                    accounts_collection.update_one(
                        {"account_number": selected_account},
                        {"$set": {"balance": new_balance}}
                    )
                    transaction = {
                        "account_number": selected_account,
                        "transaction_type": "Withdrawal",
                        "amount": withdraw_amount
                    }
                    transactions_collection.insert_one(transaction)
                    st.success(f"Withdrew ${withdraw_amount}. New balance: ${new_balance}")
                else:
                    st.error("Insufficient funds for withdrawal")
        else:
            st.warning("Account not found.")
    else:
        st.warning("Please select an account from the sidebar.")

# Deposit page (unchanged)
elif option == "Deposit":
    st.header("Deposit Money")
    if selected_account:
        account = accounts_collection.find_one({"account_number": selected_account})
        if account:
            st.subheader("Account Details")
            st.write(f"Account Number: {account['account_number']}")
            st.write(f"Current Balance: ${account['balance']}")
            deposit_amount = st.number_input("Enter the amount to deposit", min_value=0.01)
            if st.button("Deposit"):
                new_balance = account["balance"] + deposit_amount
                accounts_collection.update_one(
                    {"account_number": selected_account},
                    {"$set": {"balance": new_balance}}
                )
                transaction = {
                    "account_number": selected_account,
                    "transaction_type": "Deposit",
                    "amount": deposit_amount
                }
                transactions_collection.insert_one(transaction)
                st.success(f"Deposited ${deposit_amount}. New balance: ${new_balance}")
        else:
            st.warning("Account not found.")
    else:
        st.warning("Please select an account from the sidebar.")

# Trading page
elif option == "Trading":
    st.header("Trading")

    # Dropdown for selecting a single index to trade
    selected_index = st.selectbox("Select an index to trade", ["NIFTY50", "BANKNIFTY"])
    selected_option = st.radio("Select PUT or CALL", ["PUT", "CALL"])
    strike_price = st.number_input("Select Strike Price")
    buy_sell = st.radio("Select BUY or SELL", ["BUY", "SELL"])
    
    # Input fields for buying price and quantity
    buy_price = st.number_input("Enter Buying Price", min_value=0.01)
    quantity = st.number_input("Enter Quantity", min_value=1, value=1)
    current_margin = buy_price*quantity

    st.write("Total Margin :",buy_price*quantity)

    
    if st.button("Submit"):
        entry_time = datetime.now()
        # Record the trading transaction as an open position
        transaction = {
            "account_number": selected_account,
            "indices": [selected_index],  # Store the selected index as a list
            "option": selected_option,
            "strike_price": strike_price,
            "Entry_buy_sell": buy_sell,
            "buying_price": buy_price,
            "Entry_quantity": quantity,
            "entry_time": entry_time,
            "Status": "Pending",
            "Profit/Loss":None # Initialize "Status" as "Pending"
        }
        trading_collection.insert_one(transaction)
        account = accounts_collection.find_one({"account_number": selected_account})
        new_balance = account["balance"] - current_margin
        accounts_collection.update_one(
                        {"account_number": selected_account},
                        {"$set": {"balance": new_balance}}
                    )
        
        st.success(f"Trading transaction (open position) recorded successfully!")

# View Trading Data page
elif option == "View Trading Data":
    st.header("View Trading Data")
    
    remove_all_transactions = st.button("Remove All Transactions")
    
    if remove_all_transactions:
        trading_collection.delete_many({})
        st.success("All trading transactions have been removed.")
    
    # Display all trading transactions
    all_trading_transactions = trading_collection.find()
    trading_data = []
    
    for transaction in all_trading_transactions:
        profit_or_loss = transaction.get("profit_or_loss", None)  # Get profit/loss from the transaction
        entry_time = transaction.get("entry_time", None)  # Get entry time from the transaction
        exit_time = transaction.get("exit_time", None)  # Get exit time from the transaction

        if entry_time and exit_time:
            status = "Done"
        else:
            status = "Pending"
        
        # Add status to the transaction data
        transaction["Status"] = status
                
        trading_data.append(transaction)
    
    # Display the trading data
    st.dataframe(pd.DataFrame(trading_data))

# Open Positions page
elif option == "Open Positions":
    st.header("Open Positions")
    
    # Fetch only pending trading transactions from the database
    pending_trading_transactions = list(trading_collection.find({"Status": "Pending"}))

    if len(pending_trading_transactions) == 0:
        st.warning("No open positions found.")
    else:
        for transaction in pending_trading_transactions:
            st.subheader(f"Open Position ID: {transaction['_id']}")
            st.write(f"Index: {transaction['indices'][0]}")
            st.write(f"Option: {transaction['option']}")
            st.write(f"Strike Price: {transaction['strike_price']}")
            st.write(f"Entry Buy/Sell: {transaction['Entry_buy_sell']}")
            st.write(f"Buying Price: {transaction['buying_price']}")
            st.write(f"Quantity: {transaction['Entry_quantity']}")
            st.write(f"Entry Time: {transaction['entry_time']}")
            
            # Exit button for pending transactions
            entry_buy_sell = "SELL"
            exit_price = st.number_input("Enter Exit Price", min_value=0.01, key=f"exit_price_{transaction['_id']}")
            exit_qnty = st.number_input("Enter Exit Quantity", min_value=1, max_value= transaction['Entry_quantity'] ,key=f"exit_qnty_{transaction['_id']}")
            current_pnl = (exit_price*exit_qnty) - (transaction['buying_price']*transaction['Entry_quantity'])
            st.write(f" P&L : {current_pnl}")

            exit_button = st.button("Exit", key=f"exit_button_{transaction['_id']}, style='background-color: red;'")
            
            if exit_button:
                account = accounts_collection.find_one({"account_number": selected_account})
                new_balance = account["balance"] + current_pnl - brokerage_charge
                accounts_collection.update_one(
                                        {"account_number": selected_account},
                                        {"$set": {"balance": new_balance}}
                                    )
                # Update the transaction to "Done" status in the database
                update_to_done(transaction['_id'], datetime.now(), exit_price,exit_qnty,current_pnl,entry_buy_sell)
                st.success("Transaction marked as 'Done'.")
                st.info("Please refresh the page to see the updated status.")
            

# Close the MongoDB connection
client.close()
