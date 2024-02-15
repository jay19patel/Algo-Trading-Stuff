from Backtestclass import StockTrader
import pandas as pd
from ta.trend import EMAIndicator
import numpy as np
from datetime import datetime , timedelta
from fyers_apiv3 import fyersModel
# NOTES :

import pytz

def Get_dataset(fyers_acess_token,Symbol,TimeFrame,days):
    print(Symbol)
    data = {
                "symbol":Symbol,
                "resolution": TimeFrame,
                "date_format":"1",
                "range_from":(datetime.now() - timedelta(days=int(days))).strftime('%Y-%m-%d'),
                "range_to":datetime.now().strftime('%Y-%m-%d'),
                "cont_flag":"0"
            }
    fyers = fyersModel.FyersModel(client_id="MACO3YJA7I-100", is_async=False, token=fyers_acess_token, log_path="")
    row_data =  fyers.history(data=data)
    print(row_data)
    df = pd.DataFrame.from_dict(row_data['candles'])
    columns_name = ['Datetime','Open','High','Low','Close','Volume']
    df.columns = columns_name
    df['Datetime'] = pd.to_datetime(df['Datetime'], unit='s')
    df['Datetime'] = df['Datetime'].dt.tz_localize(pytz.utc).dt.tz_convert('Asia/Kolkata')
    df['Datetime'] = df['Datetime'].dt.tz_localize(None)

    # path = "30day.csv"
    # df = pd.read_csv(path)
    # df.drop(['Unnamed: 0','Volume'], axis=1, inplace=True)

    # ----------------------- [INDICATORS] --------------------------------
    df['5EMA'] = EMAIndicator(close=df['Close'], window=5, fillna=False).ema_indicator()
    df['15EMA'] = EMAIndicator(close=df['Close'], window=15, fillna=False).ema_indicator()
    df['Candle'] = ['Green' if close >= open else 'Red' for close, open in zip(df['Close'], df['Open'])]
    df['3C_Gap'] = df['Low'] - df['Low'].rolling(window=3).min()


    return df




def Stetegy3_here(df):
    ce_condition = ((df['High'].shift(1) < df['15EMA'].shift(1)) & (df['High'] >= df['15EMA'])) | ((df['Candle'].shift(2) == "Green") & (df['Candle'].shift(1) == "Red") & (df['Close'] >= df['High'].shift(1)) & (df['Low'].shift(2) <= df['Low'].shift(1)))
    pe_condition = ((df['Low'].shift(1) > df['15EMA'].shift(1)) & (df['Low'] <= df['15EMA']) )| ((df['Candle'].shift(2) == "Red") & (df['Candle'].shift(1) == "Green") & (df['Close'] <= df['Low'].shift(1)) & (df['High'].shift(2) >= df['High'].shift(1)))
    df['Main_Status'] = np.select([ce_condition, pe_condition], ['CE', 'PE'], default='None')
    return df, "Mark3"


def Backtesting(fyers_acess_token,select_index,select_timeframe,days):
    trader = StockTrader()

    def main_app(row, strategy_name):
        if row['Main_Status'] in ["CE", "PE"]:
            trader.buy_stock(quantity=1, price=row['Close'], datetime=row['Datetime'], symbol="NIFTY50", side=row['Main_Status'],strategy_name=strategy_name)
        trader.auto_exit(row['Close'],row['Datetime'])

    df = Get_dataset(fyers_acess_token,select_index,select_timeframe,days).tail(5000)
    strategy_df, strategy_name = Stetegy3_here(df)
    strategy_df.apply(main_app, axis=1, strategy_name=strategy_name)
    states,logs = trader.stats()
    return states,logs


