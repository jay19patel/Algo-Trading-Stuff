import streamlit as st
import pymongo

# Connect to MongoDB
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["banking_system"]
accounts_collection = db["accounts"]
transactions_collection = db["transactions"]
trading_collection = db["trading_transactions"]

# Streamlit app
st.title("Banking and Trading Dashboard")

# Sidebar
st.sidebar.header("Options")
option = st.sidebar.selectbox("Select an option", ["Home","View All Accounts" ,"View All Transactions", "View Withdrawal Data", "View Deposit Data", "Withdraw", "Deposit", "Trading", "View Trading Data"])


# Account selection dropdown in the sidebar
# account_numbers = [account["account_number"] for account in accounts_collection.find()]
# selected_account = st.sidebar.selectbox("Select an account number", account_numbers, index=0) if account_numbers else None
selected_account = "20230920085954897518"
# Home page (unchanged)
if option == "Home":
    st.header("Total Balance")
    if selected_account:
        account = accounts_collection.find_one({"account_number": selected_account})
        if account:
            st.subheader(f"${account['balance']:.2f}")
        else:
            st.warning("Account not found.")
    else:
        st.warning("Please select an account from the sidebar.")


elif option == "View All Accounts":
    st.header("All Accounts")
    all_accounts = accounts_collection.find()
    account_data = [{"Account Number": account["account_number"], "Account Holder": account["holder_name"]} for account in all_accounts]
    
    if account_data:
        st.table(account_data)
    else:
        st.info("No accounts found.")

# View All Transactions page (unchanged)
elif option == "View All Transactions":
    st.header("All Transactions")
    all_transactions = transactions_collection.find()
    transaction_data = []
    for transaction in all_transactions:
        transaction_data.append(transaction)
    st.table(transaction_data)

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
        st.table(withdrawal_data)
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
        st.table(deposit_data)
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

# Trading page (unchanged)
# Trading page
elif option == "Trading":
    st.header("Trading")

    # Dropdown for selecting a single index to trade
    selected_index = st.selectbox("Select an index to trade", ["NIFTY50", "BANKNIFTY"])
    selected_option = st.radio("Select PUT or CALL", ["PUT", "CALL"])
    strike_price = st.selectbox("Select Strike Price", [19500, 20000, 20500, 21000])
    buy_sell = st.radio("Select BUY or SELL", ["BUY", "SELL"])
    
    # Input fields for buying and selling prices
    buy_price = st.number_input("Enter Buying Price", min_value=0.01)
    sell_price = st.number_input("Enter Selling Price", min_value=0.01)
    
    if st.button("Submit"):
        # Calculate profit or loss with 8% tax deduction
        profit_or_loss = 0
        if buy_sell == "BUY":
            profit_or_loss = (sell_price - buy_price) * 0.92  # 8% tax deduction for profit
        elif buy_sell == "SELL":
            profit_or_loss = (buy_price - sell_price) * 0.92  # 8% tax deduction for profit
        
        # Record the trading transaction
        transaction = {
            "account_number": selected_account,
            "indices": [selected_index],  # Store the selected index as a list
            "option": selected_option,
            "strike_price": strike_price,
            "buy_sell": buy_sell,
            "buying_price": buy_price,
            "selling_price": sell_price,
            "profit_or_loss": profit_or_loss
        }
        trading_collection.insert_one(transaction)
        
        st.success(f"Trading transaction recorded successfully!\nProfit/Loss after tax: ${profit_or_loss:.2f}")

# View Trading Data page
elif option == "View Trading Data":
    st.header("View Trading Data")

    # Display all trading transactions
    all_trading_transactions = trading_collection.find()
    trading_data = []

    for transaction in all_trading_transactions:
        profit_or_loss = transaction.get("profit_or_loss", 0)  # Get profit/loss from the transaction
        # Add profit/loss to the transaction data
        transaction["Profit/Loss"] = f"${profit_or_loss:.2f}"
        trading_data.append(transaction)

    # Display the trading data including profit/loss
    st.table(trading_data)

# Close the MongoDB connection
client.close()
