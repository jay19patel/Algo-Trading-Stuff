import streamlit as st
import pymongo
import datetime

# Initialize MongoDB connection
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["my_database"]
holding_collection = db["holding_collection"]
order_collection = db["order_collection"]

# Streamlit sidebar with options
selected_option = st.sidebar.selectbox("Select an option:", ['Banknifty', 'Nifty 50'])

# Display the selected option in the blue box
st.title(f"Selected Option: {selected_option}")

# Create a form to add a new stock
stock_name = st.text_input("Enter Stock Name:")
strike_price = st.number_input("Enter Strike Price:")
option_type = st.selectbox("Select Option Type:", ["Call", "Put"])
buy_or_sell = st.selectbox("Select Buy or Sell:", ["Buy", "Sell"])

if st.button("Add"):
    # Add the stock to the holding_collection
    holding_collection.insert_one({
        "stock_name": stock_name,
        "strike_price": strike_price,
        "option_type": option_type,
        "buy_or_sell": buy_or_sell,
        "timestamp": datetime.datetime.now()
    })

# Display holdings
st.header("Holdings")
holdings = holding_collection.find()
for holding in holdings:
    st.write(f"Stock: {holding['stock_name']}, Strike Price: {holding['strike_price']}, "
             f"Option Type: {holding['option_type']}, Buy/Sell: {holding['buy_or_sell']}, "
             f"Timestamp: {holding['timestamp']}")

# Create an exit button to sell a stock
if st.button("Exit"):
    stock_to_sell = st.selectbox("Select a stock to sell:", [holding['stock_name'] for holding in holdings])
    selling_price = st.number_input("Enter Selling Price:")
    
    # Calculate profit or loss
    holding = holding_collection.find_one({"stock_name": stock_to_sell})
    buying_price = holding['strike_price']
    profit_or_loss = selling_price - buying_price
    
    # Add the order to the order_collection
    order_collection.insert_one({
        "stock_name": stock_to_sell,
        "buying_price": buying_price,
        "selling_price": selling_price,
        "profit_or_loss": profit_or_loss,
        "timestamp": datetime.datetime.now()
    })

# Display orders
st.header("Orders")
orders = order_collection.find()
for order in orders:
    st.write(f"Stock: {order['stock_name']}, Buying Price: {order['buying_price']}, "
             f"Selling Price: {order['selling_price']}, Profit/Loss: {order['profit_or_loss']}, "
             f"Timestamp: {order['timestamp']}")
