

from datetime import datetime , timedelta
fyers = 1
import pandas as pd
import pytz
from ta.trend import EMAIndicator
import numpy as np

from Fyers import Fyers




def EMA_Strategy(df):
    df['15EMA'] = EMAIndicator(close=df['Close'], window=15, fillna=False).ema_indicator()
    ce_5ema = (df['High'].shift(1) < df['15EMA'].shift(1)) & (df['Close'] >= df['15EMA'])
    pe_5ema = (df['Low'].shift(1) > df['15EMA'].shift(1)) & (df['Close'] <= df['15EMA'])
    df['Signal_5EMA'] = np.select([ce_5ema, pe_5ema], ['CE', 'PE'], default='None')
    return df.iloc[-4]['Signal_5EMA'],df.iloc[-4]['Close']

    
def Main_Stetegy_execution(Symbol,TimeFrame,fyers):
    try:
        data = fyers.Historical_Data(Symbol,TimeFrame)
        status,Price = EMA_Strategy(data)
        # return {Symbol:status,"Price":Price}
        return {Symbol:"None","Price":Price}
    except:
        return False


