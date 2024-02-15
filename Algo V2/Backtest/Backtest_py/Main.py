from Backtestclass import StockTrader
import pandas as pd
from ta.trend import EMAIndicator
import numpy as np


# NOTES :


# - SRETEGY BANAVI NE  IF TE  ROW MA BUY KARVANU HOY TO  COLUMN NU NAME AND AMA CE KA TO PE JE LEVANU HOY E ADD KARVANU
# - AND E DATAFRAME TA CALL THAY ONE BY ONE ROW ATLE TE EXECUTE THEY  JASE AGAR CE HASE TO CE SIDE NI TRED AND PE HASE TO PE SIDE NI TRED

#  EXAMPLE 

# df['5EMA'] = EMAIndicator(close=df['Close'], window=5, fillna=False).ema_indicator()
#     df['15EMA'] = EMAIndicator(close=df['Close'], window=15, fillna=False).ema_indicator()
#     ce_5ema = (df['High'].shift(1) < df['15EMA'].shift(1)) & (df['Close'] >= df['15EMA'])
#     pe_5ema = (df['Low'].shift(1) > df['5EMA'].shift(1)) & (df['Close'] <= df['5EMA'])
#     df['Signal_5EMA'] = np.select([ce_5ema, pe_5ema], ['CE', 'PE'], default='None')

# aa uper wala code ma  5 AND 15 EMA FIND KARI ne je pan row ma apdi Condition true they acroding CE ka to PE
#  e Column Single_5Ema ma add thay bas  baki nu auto metcvi thay jase 





def Get_dataset():
    path = "30day.csv"
    df = pd.read_csv(path)
    df.drop(['Unnamed: 0','Volume'], axis=1, inplace=True)

    # ----------------------- [INDICATORS] --------------------------------
    df['5EMA'] = EMAIndicator(close=df['Close'], window=5, fillna=False).ema_indicator()
    df['15EMA'] = EMAIndicator(close=df['Close'], window=15, fillna=False).ema_indicator()
    df['Candle'] = ['Green' if close >= open else 'Red' for close, open in zip(df['Close'], df['Open'])]
    df['3C_Gap'] = df['Low'] - df['Low'].rolling(window=3).min()


    return df

def Stetegy1_here(df):
     #  --------------------------------------[5-15 EMA]-----------------------------------
    ce_ema1 = (df['High'].shift(1) < df['15EMA'].shift(1)) & (df['High'] >= df['15EMA'])
    pe_ema1 = (df['Low'].shift(1) > df['15EMA'].shift(1)) & (df['Low'] <= df['15EMA'])
    df['Main_Status'] = np.select([ce_ema1, pe_ema1], ['CE', 'PE'], default='None')
    #  --------------------------------------[5-15 EMA]-----------------------------------
    return df , "Mark1"


def Stetegy2_here(df):
     #  --------------------------------------[5-15 EMA]-----------------------------------
    ce = (df['Candle'].shift(2) == "Green") & (df['Candle'].shift(1) == "Red") & (df['Close'] >= df['High'].shift(1)) & (df['Low'].shift(2) <= df['Low'].shift(1))
    pe = (df['Candle'].shift(2) == "Red") & (df['Candle'].shift(1) == "Green") & (df['Close'] <= df['Low'].shift(1)) & (df['High'].shift(2) >= df['High'].shift(1))
    df['Main_Status'] = np.select([ce, pe], ['CE', 'PE'], default='None')
    #  --------------------------------------[5-15 EMA]-----------------------------------
    return df , "Mark2"


def Stetegy3_here(df):
    ce_condition = ((df['High'].shift(1) < df['15EMA'].shift(1)) & (df['High'] >= df['15EMA'])) | ((df['Candle'].shift(2) == "Green") & (df['Candle'].shift(1) == "Red") & (df['Close'] >= df['High'].shift(1)) & (df['Low'].shift(2) <= df['Low'].shift(1)))
    pe_condition = ((df['Low'].shift(1) > df['15EMA'].shift(1)) & (df['Low'] <= df['15EMA']) )| ((df['Candle'].shift(2) == "Red") & (df['Candle'].shift(1) == "Green") & (df['Close'] <= df['Low'].shift(1)) & (df['High'].shift(2) >= df['High'].shift(1)))
    df['Main_Status'] = np.select([ce_condition, pe_condition], ['CE', 'PE'], default='None')
    return df, "Mark3"





def Backtesting(strategy_func):
    trader = StockTrader()

    def main_app(row, strategy_name):
        if row['Main_Status'] in ["CE", "PE"]:
            trader.buy_stock(quantity=1, price=row['Close'], datetime=row['Datetime'], symbol="NIFTY50", side=row['Main_Status'],strategy_name=strategy_name)
        trader.auto_exit(row['Close'],row['Datetime'])

    df = Get_dataset().tail(5000)
    strategy_df, strategy_name = strategy_func(df)
    strategy_df.apply(main_app, axis=1, strategy_name=strategy_name)
    trader.stats()
    trader.logs.to_csv("data.csv")

Backtesting(Stetegy3_here)
