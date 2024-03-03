#  UPDATED VERSION OF LIVE TREDING PDT 


import pandas as pd
import requests
from datetime import datetime
import io
import os
import pandas as pd
import concurrent.futures

import logging

logging.basicConfig(filename='trading.log', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


def get_index_info(option_symbol):
    index_mapping = {
        "NSE:NIFTY50-INDEX": ("NIFTY", 20, 40),
        "NSE:NIFTYBANK-INDEX": ("BANKNIFTY", 30, 60),
        "NSE:FINNIFTY-INDEX": ("FINNIFTY", 20, 40)
    }
    return index_mapping.get(option_symbol, (None, None, None))


def Get_Option_info(tred_index,tred_side,tred_current_price):
    try:
        tred_sp = round(tred_current_price,-2)
        current_date = datetime.now().strftime('%Y-%m-%d')
        if os.path.exists(f'Private/sym_details_{current_date}.csv'):
            df = pd.read_csv(f'Private/sym_details_{current_date}.csv')
            df["EXDATETIME"]=pd.to_datetime(df["TIMESTAMP"],unit='s')
            final_data = df[
            (df["STRICK PRICE"] == tred_sp) &
            (df["EXDATETIME"] >= pd.to_datetime(f"{datetime.now().strftime('%Y-%m-%d')} 10:00:00")) &
            (df["SIDE"] == tred_side) & 
            (df['INDEX'] == tred_index)]
            if final_data.shape[0] == 0:
                logging.info(" [2.1 WRONG DATA] : SYMBOL FETCH NONE DF ")
                return False
            else:
                return final_data.iloc[0].to_dict()       
        else:
            logging.info(" [2.1 SUCESS] : SYMBOL FETCH ")
            spotnames=['BANKNIFTY','FINNIFTY','NIFTY']
            response=requests.get('https://public.fyers.in/sym_details/NSE_FO.csv')
            row_df=pd.read_csv(io.StringIO(response.text),header=None)
            row_df = row_df[[0,1,3,8,9,13,15,16]]
            column_name = ["ID","INDEX INFO","LOT","TIMESTAMP","SYMBOL","INDEX","STRICK PRICE","SIDE"]
            row_df.columns= column_name
            row_df["EXDATETIME"]=pd.to_datetime(row_df["TIMESTAMP"],unit='s')
            df = pd.concat([row_df[row_df["INDEX"] == spotname] for spotname in spotnames])
            today_date = pd.to_datetime(current_date)
            filtered_df = df[pd.to_datetime(df["TIMESTAMP"],unit='s') >= today_date]
            filtered_df.to_csv(f"Private/sym_details_{current_date}.csv",index=False)
            Get_Option_info(tred_index,tred_side,tred_current_price)
    except Exception as e:
        logging.info(" [2.1 ERRO] : SYMBOL FETCH ERROR",e)
        return False


import time 
def generate_id():
    timestamp = int(time.time() * 1000)
    additional_info = "EXECUTION" 
    new_id = f"{timestamp}_{additional_info}"
    return new_id


