from datetime import datetime , timedelta

from Manager import Strategy_Helper
fyers = 1
import pandas as pd
import pytz
from ta.trend import EMAIndicator
import numpy as np
from utility import TredBuddy_Helper

import logging


from dotenv import load_dotenv
import os
from pymongo import MongoClient
load_dotenv()

client = MongoClient(os.getenv("MONGODB_STRING"))
db = client['TredBuddy']
db_positions = db['Positions']


logging.basicConfig(filename='trading.log', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def Messages(message):
    print(message)
    logging.info(message)


def strategy(df,current_price):
    df['15EMA'] = EMAIndicator(close=df['Close'], window=15, fillna=False).ema_indicator()
    df['Candle'] = ['Green' if close >= open else 'Red' for close, open in zip(df['Close'], df['Open'])]
    
    ce_condition = ((df['High'].shift(1) < df['15EMA'].shift(1)) & (current_price > df['15EMA'])) | ((df['Candle'].shift(2) == "Green") & (df['Candle'].shift(1) == "Red") & (current_price >= df['High'].shift(1)) & (df['Low'].shift(2) <= df['Low'].shift(1)))
    pe_condition = ((df['Low'].shift(1) > df['15EMA'].shift(1)) & (current_price < df['15EMA']) )| ((df['Candle'].shift(2) == "Red") & (df['Candle'].shift(1) == "Green") & (current_price <= df['Low'].shift(1)) & (df['High'].shift(2) >= df['High'].shift(1)))
    df['Main_Status'] = np.select([ce_condition, pe_condition], ['CE', 'PE'], default='NONE')
    return df.iloc[-1]['Main_Status']
    # return "CE"

def Main_Stetegy_execution(Symbol, current_price, fyers):
    try:
        data = fyers.Historical_Data(Symbol, 15)
        status = strategy(data, current_price)
        if status != "NONE":
            option_info = TredBuddy_Helper.Get_Option_info(tred_index = Symbol, tred_side = status, tred_current_price  =current_price )
            option_symbol = option_info['SYMBOL'] 
            option_lot_size = option_info['LOT']
            option_expiry = option_info['EXDATETIME'].date()
            option_sp = option_info['STRICK PRICE']
            option_ltp_obj = fyers.get_current_ltp(option_symbol)
            option_ltp = option_ltp_obj[option_symbol[4:]]
            is_already = list(db_positions.find({"INDEX": Symbol, "SIDE": status, "STATUS": "OPEN"}))
            if len(is_already) == 0:
                fyers.Buy_order(index_name=Symbol, tred_side=status, index_price=current_price, tred_symbol=option_symbol, quantity_per_lot=option_lot_size, buy_price=option_ltp, notes=" Custom EMA Strategy")
            else:
                Messages("Alredy Exist Tred So I can not Buy Again")
    except Exception as e:
        Messages("[ERROR] : STATEGY NOT EXECUTED", e)

