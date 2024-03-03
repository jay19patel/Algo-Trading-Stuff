
from pymongo import MongoClient
import concurrent.futures
from TredBuddy_Helper import Get_Option_info, get_index_info, generate_id
from Stretegy_Helper import Main_Stetegy_execution
from datetime import datetime

from dotenv import load_dotenv
import logging

logging.basicConfig(filename='Private/trading.log', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


load_dotenv()
import os

# ---------------------- DATABASE CONNECTION ------------------
client = MongoClient(os.getenv("MONGODB_STRING"))
db = client['TredBuddy']
db_orders = db['Orders']
db_positions = db['Positions']

import json

# Function to load index_open_trade from a JSON file
def load_index_open_trade():
    try:
        with open('Private/index_open_trade.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Function to save index_open_trade to a JSON file
def save_index_open_trade(index_open_trade):
    with open('Private/index_open_trade.json', 'w') as file:
        json.dump(index_open_trade, file)


def find_treds(fyers):
    index_open_trade = load_index_open_trade()
    MyIndex = ["NSE:NIFTY50-INDEX", "NSE:NIFTYBANK-INDEX"]
    # MyIndex = ["NSE:NIFTY50-INDEX"]
    live_index = fyers.get_current_ltp(",".join(MyIndex))
    index_data_list = list(zip(MyIndex, live_index.values()))

    try:
        def process_index(index_data):
            index_name, current_price = index_data
            index_status = Main_Stetegy_execution(index_name, current_price, fyers)

            if index_status != "NONE":
                current_datetime = datetime.now().strftime('%m/%d/%Y %I:%M %p')
                index_new_name, index_sl, index_tg = get_index_info(index_name)
                index_side = index_status
                execution_id = generate_id()
                option_info = Get_Option_info(index_new_name, index_side, current_price)
                option_symbol = option_info['SYMBOL']  # Move this line here
                option_lot_size = option_info['LOT']
                option_expiry = option_info['EXDATETIME'].date()
                option_sp = option_info['STRICK PRICE']

                if index_open_trade.get(index_name)  and index_open_trade.get(index_name) == index_side :
                    logging.info(f"Trade is already open for {index_name} : [{option_symbol}] Quantity will be Added.")    
                else:
                    index_open_trade[index_name] = index_side
                    save_index_open_trade(index_open_trade)
                    if option_info != False:
                        
                        option_ltp_obj = fyers.get_current_ltp(option_symbol)
                        option_ltp = option_ltp_obj[option_symbol[4:]]

                        option_lot = fyers.Get_Lotsize(int(option_info['LOT']),option_ltp)

                        sl_factor, tg_factor = 100 - index_sl, 100 + index_tg
                        option_ltp_sl = (option_ltp * sl_factor) / 100
                        option_ltp_target = (option_ltp * tg_factor) / 100
                        logging.info(f"[SUCCESS] : ALGO FIND A TRADE----------- [ BUY {current_datetime} | {option_symbol} | {current_price} | {index_side}] | {option_lot}------------")
                
                        new_row = {'EXECUTION ID': execution_id,
                                        'INDEX': index_name,
                                        'SIDE': index_side,
                                        'TRIGGER INDEX PRICE': current_price,
                                        'OPTION': option_sp,
                                        'OPTION SYMBOL': option_symbol,
                                        'LOT SIZE': option_info['LOT'],
                                        'LOT':option_lot,
                                        "SL PRICE": option_ltp_sl,
                                        "TARGET PRICE": option_ltp_target,
                                        'BUY PRICE': option_ltp,
                                        'BUY DATETIME': current_datetime,
                                        "SELL PRICE": 0,
                                        "SELL DATETIME": "",
                                        "TRAILING": [{'SL': option_ltp_sl, 'TARGET': option_ltp_target, 'DATETIME': current_datetime}],
                                        "Entry Margin": int(option_lot*option_lot_size*option_ltp),
                                        "Exit Margin":0,
                                        "PnL GROW": 0,
                                        "STATUS": "Running"
                                        }
                        db_positions.insert_one(new_row)
                        logging.info("[SUCCESS] TRADE EXECUTED SUCCESSFULLY.")
                        print("[BUY]")


        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(process_index, index_data_list)
    except Exception as e:
        logging.info(f"[END] : SOMETHING WENT WRONG WITH AUTO TRADE: {e}")