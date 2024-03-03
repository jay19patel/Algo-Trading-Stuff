

from datetime import datetime , timedelta
fyers = 1
import pandas as pd
import pytz
from ta.trend import EMAIndicator
import numpy as np

from Fyers import Fyers
import logging

logging.basicConfig(filename='Private/trading.log', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')


#  each 30sec / 1min ma aas script run thase jema only CE KE PE KE NONE return thase

def Stetegy_here(df,current_price):
    df['15EMA'] = EMAIndicator(close=df['Close'], window=15, fillna=False).ema_indicator()
    df['Candle'] = ['Green' if close >= open else 'Red' for close, open in zip(df['Close'], df['Open'])]
    
    ce_condition = ((df['High'].shift(1) < df['15EMA'].shift(1)) & (current_price > df['15EMA'])) | ((df['Candle'].shift(2) == "Green") & (df['Candle'].shift(1) == "Red") & (current_price >= df['High'].shift(1)) & (df['Low'].shift(2) <= df['Low'].shift(1)))
    pe_condition = ((df['Low'].shift(1) > df['15EMA'].shift(1)) & (current_price < df['15EMA']) )| ((df['Candle'].shift(2) == "Red") & (df['Candle'].shift(1) == "Green") & (current_price <= df['Low'].shift(1)) & (df['High'].shift(2) >= df['High'].shift(1)))
    df['Main_Status'] = np.select([ce_condition, pe_condition], ['CE', 'PE'], default='NONE')
    # return df.iloc[-1]['Main_Status']
    return "CE"
    # return CE/PE/NONE

    
def Main_Stetegy_execution(Symbol, current_price, fyers):
    try:
        data = fyers.Historical_Data(Symbol, 15)
        status = Stetegy_here(data, current_price)
        return status
    except Exception as e:
        logging.info("[ERROR] : MAIN STETEGY BUILDER", e)
        return "NONE"






