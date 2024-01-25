

from TredBuddy_Helper import Get_Option_info
import pandas as pd
import concurrent.futures
from datetime import datetime
import json
from pymongo import MongoClient
from Fyers import Get_Current_ltp


client = MongoClient('mongodb://localhost:27017/')

db = client['TredBuddy']

# Select collection
db_orders = db['Orders']
db_positions = db['Positions']

def Tred_Execution(get_index,get_cuurent_price,get_tred_side,get_execution_id):
    print("TRED EXECUTION ")
    option_info = Get_Option_info(get_index,get_tred_side,get_cuurent_price)
    print("OPTION DATA :",option_info)
    if option_info != None:
        option_lot_size = option_info['LOT']
        option_symbol = option_info['SYMBOL']
        option_expiry = option_info['EXDATETIME'].date()
        option_sp = option_info['STRICK PRICE']

        option_ltp =Get_Current_ltp(option_symbol)
        option_ltp_sl = (option_ltp*70)/100
        option_ltp_target = (option_ltp*150)/100
        print("LTP :",option_ltp)

        new_row = {'EXECUTION ID': get_execution_id,
                    'INDEX': get_index,
                    'SIDE':get_tred_side,
                    'TRIGGER INDEX PRICE':get_cuurent_price,
                    'OPTION':option_sp,
                    'OPTION SYMBOL':option_symbol,
                    'BUY PRICE':option_ltp,
                    'QTY':option_lot_size,
                    'BUY DATETIME':datetime.now().strftime('%m/%d/%Y %I:%M %p'),
                    "SL PRICE":option_ltp_sl,
                    "TARGET PRICE":option_ltp_target,
                    "SELL PRICE":None,
                    "SELL DATETIME":None,
                    "TARILING COUNT":None,
                    "PnL GROW %":None,
                    "POINTS":None,
                    "TRED TIME":None,
                    "STATUS" :"Open"
                    } 
        db_positions.insert_one(new_row)

import time 
def generate_id():
    timestamp = int(time.time() * 1000)
    additional_info = "EXECUTION" 
    new_id = f"{timestamp}_{additional_info}"
    return new_id

def Trigger_pdt():
    get_index = "BANKNIFTY"
    get_cuurent_price = 44766

    df = db_orders.find()
    current_datetime = datetime.now().strftime('%m/%d/%Y %I:%M %p')
    row_data = [json.dumps(document, default=str) for document in df]

    def check_condition(entry):
        row = json.loads(entry)
        price = row["PRICE"]
        condition = row["CONDITION"]
        execution_id= row['EXECUTION ID']


        if ((condition == "ABOVE" and price >= get_cuurent_price) or(condition == "BELOW" and price <= get_cuurent_price)) and row['EXECUTION STATUS'] != "Executed" and get_index == row['INDEX']:
            filter_criteria = {'EXECUTION ID': execution_id}
            update_execution = {'$set': {'EXECUTION STATUS': "Executed"}}
            update_datetime = {'$set': {'EXECUTION DATETIME': current_datetime}}
            db_orders.update_one(filter_criteria, update_execution)
            db_orders.update_one(filter_criteria, update_datetime)
            Tred_Execution(get_index,get_cuurent_price,row['SIDE'],execution_id)


    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(check_condition, row_data)


    # test_row = {    'EXECUTION ID': generate_id(),
    #                 'INDEX': "BANKNIFTY",
    #                 'SIDE':"CE",
    #                 "CONDITION":"ABOVE",
    #                 "PRICE":1520,
    #                 "TIMEFRAME":15,
    #                 "EXECUTION STATUS" :"Open",
    #                 "EXECUTION DATETIME" : None,
    #                 "NOTES":"TEST"
    #                 } 
    # df = db_orders.insert_one(test_row)

Trigger_pdt()
