

from pymongo import MongoClient
import concurrent.futures
from TredBuddy_Helper import Get_Option_info,get_index_info,generate_id
from datetime import datetime , timedelta

from dotenv import load_dotenv
import logging

logging.basicConfig(filename='trading.log', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


load_dotenv()

import os
# ---------------------- DATABASE CONECTION ------------------
client = MongoClient(os.getenv("MONGODB_STRING"))
db = client['TredBuddy']
db_orders = db['Orders']
db_positions = db['Positions']

import json


# Function to load index_open_trade from a JSON file
def load_index_open_trade():
    try:
        with open('index_open_trade.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_index_open_trade(index_open_trade):
    with open('index_open_trade.json', 'w') as file:
        json.dump(index_open_trade, file)


def Auto_exit(fyers):
    index_open_trade = load_index_open_trade()

    row_data = [document for document in db_positions.find("STATUS" == "Running")]
    live_data_list = {item['OPTION SYMBOL'] for item in row_data}

    live_data_symbols = ",".join(live_data_list)


    if len(live_data_list) >= 1:
        live_data = fyers.get_current_ltp(live_data_symbols)
        logging.info("[SUCCESS] Auto Exit Check For :",live_data)
        live_data_options = tuple(live_data.items())


        def Condition_check(option_data, live_data):
            symbol_name = option_data['OPTION SYMBOL'][4:]
            option_live_price = live_data.get(symbol_name)  # Get the live price for the option symbol
            option_side = option_data.get("SIDE")


            index_sl = 20
            index_tg = 20
            sl_factor, tg_factor = (100 - index_sl, 100 + index_tg) if option_side == "CE" else (100 + index_sl, 100 - index_tg)
            option_ltp_sl = (option_live_price * sl_factor) / 100
            option_ltp_target = (option_live_price * tg_factor) / 100
             # ------------------------------- TARGET CHECK ---------------------------------
            # print(f"LIVE : {option_live_price} | TG : {option_data['TARGET PRICE']} | SL : {option_data['SL PRICE']} ")
            if (option_side == "CE" and option_data['TARGET PRICE'] <= option_live_price) or (option_side == "PE" and option_data['TARGET PRICE'] >= option_live_price):
                    filter_criteria = {'EXECUTION ID': option_data['EXECUTION ID']}
                    update_execution = {
                        '$set': {
                            'TARGET PRICE': option_ltp_target,
                            'SL PRICE': option_ltp_sl,
                            'TARILING COUNT': option_data['TARILING COUNT'] + 1,
                        }
                    }
                    db_positions.update_one(filter_criteria, update_execution)
                    print(f"-----------------[{option_data['OPTION SYMBOL']} : Target Hit] TARGET =[{option_ltp_target})] SL = [{option_ltp_sl}]- TC = [{option_data['TARILING COUNT'] + 1}]----------------")

            elif (option_side == "CE" and option_data['SL PRICE'] >= option_live_price) or (option_side =="PE" and option_data['SL PRICE'] <= option_live_price):
                    filter_criteria = {'EXECUTION ID': option_data['EXECUTION ID']}
                   
                    PNL_GROW = round((option_live_price - option_data.get("BUY PRICE", 10)) * option_data.get('QTY', 0), 2)
                    PNL_GROW_PR = PNL_GROW * 100 / (option_data.get('BUY PRICE', 0) * option_data.get('QTY', 0))
                    update_execution = {
                        '$set': {
                            'STATUS': "SL Hit",
                            'SELL PRICE': option_live_price,
                            'SELL DATETIME': datetime.now().strftime('%m/%d/%Y %I:%M %p'),
                            'PnL GROW': PNL_GROW,
                            'PnL GROW %': PNL_GROW_PR
                        }
                    }
                    index_open_trade[option_data['INDEX']] = False
                    save_index_open_trade(index_open_trade)

                    print(f"-----------------[{option_data['OPTION SYMBOL']} : SL Hit] PNL =[{PNL_GROW}(%{PNL_GROW_PR})]-----------------")
   
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for i in row_data:
                executor.submit(Condition_check, i, dict(live_data_options))





























# from Fyers import Fyers
# fyers = Fyers()
# fyers.authentication()
# Auto_exit(fyers)