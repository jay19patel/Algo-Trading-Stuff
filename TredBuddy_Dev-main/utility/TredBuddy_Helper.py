


import pandas as pd
import requests
from datetime import datetime
import io
import os
import pandas as pd

import logging
logging.basicConfig(filename='trading.log', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def Messages(message):
    print(message)
    logging.info(message)


def get_index_info(option_symbol):
    index_mapping = {
        "NSE:NIFTY50-INDEX": "NIFTY",
        "NSE:NIFTYBANK-INDEX":"BANKNIFTY",
        "NSE:FINNIFTY-INDEX": "FINNIFTY",
        "BSE:BANKEX-INDEX": "BANKEX",
        "BSE:SENSEX-INDEX": "SENSEX"
    }
    return index_mapping.get(option_symbol)

def Update_FO():
        current_date = datetime.now().strftime('%Y-%m-%d')
        Messages(" [2.1 SUCESS] : UPDATE FO ONLINE  ")
        spotnames=['BANKNIFTY','FINNIFTY','NIFTY','SENSEX','BANKEX']
        response1=requests.get('https://public.fyers.in/sym_details/NSE_FO.csv')
        response2=requests.get('https://public.fyers.in/sym_details/BSE_FO.csv')
        row_df1=pd.read_csv(io.StringIO(response1.text),header=None)
        row_df2=pd.read_csv(io.StringIO(response2.text),header=None)
        row_df = pd.concat([row_df1, row_df2])
        row_df = row_df[[0,1,3,8,9,13,15,16]]
        column_name = ["ID","INDEX INFO","LOT","TIMESTAMP","SYMBOL","INDEX","STRICK PRICE","SIDE"]
        row_df.columns= column_name
        row_df["EXDATETIME"]=pd.to_datetime(row_df["TIMESTAMP"],unit='s')
        df = pd.concat([row_df[row_df["INDEX"] == spotname] for spotname in spotnames])
        today_date = pd.to_datetime(current_date)
        filtered_df = df[pd.to_datetime(df["TIMESTAMP"],unit='s') >= today_date]
        filtered_df.to_csv(f"Private/sym_details_{current_date}.csv",index=False)
        available_date = df[df['EXDATETIME'].dt.date == datetime.now().date()]
        return not available_date.empty

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
            (df['INDEX'] == get_index_info(tred_index))
            ]
            if final_data.shape[0] == 0:
                Messages(" [2.1 WRONG DATA] : SYMBOL FETCH NONE DF ")
                return False
            else:
                return final_data.iloc[0].to_dict()       
        else:
            filtered_df = Update_FO()
            Get_Option_info(tred_index,tred_side,tred_current_price)
    except Exception as e:
        Messages(" [2.1 ERRO] : SYMBOL FETCH ERROR",e)
        return False
    
