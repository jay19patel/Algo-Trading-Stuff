from ta.trend import EMAIndicator
import pandas_ta as pdta
from fyers_apiv3 import fyersModel
from datetime import datetime , timedelta
import pandas as pd
import pytz
import numpy as np


from ta.trend import EMAIndicator
import pandas_ta as pdta


def Analyser_data(Symbol,timeframe,fyers):
    try:
        data = {
                    "symbol":Symbol,
                    "resolution":timeframe,
                    "date_format":"1",
                    "range_from":(datetime.now() - timedelta(days=100)).strftime('%Y-%m-%d'),
                    "range_to":datetime.now().strftime('%Y-%m-%d'),
                    "cont_flag":"0"
                }
        row_data =  fyers.history(data=data)
        df = pd.DataFrame.from_dict(row_data['candles'])
        columns_name = ['Datetime','Open','High','Low','Close','Volume']
        df.columns = columns_name
        df['Datetime'] = pd.to_datetime(df['Datetime'], unit='s')
        df['Datetime'] = df['Datetime'].dt.tz_localize(pytz.utc).dt.tz_convert('Asia/Kolkata')
        df['Datetime'] = df['Datetime'].dt.tz_localize(None)


        df['Pivot'] = (df['High'] + df['Low'] + df['Close']) / 3
        df['Candle'] = df.apply(lambda row: 'Green' if row['Close'] >= row['Open'] else 'Red', axis=1)
        df['5EMA'] = EMAIndicator(close=df['Close'], window=5, fillna=False).ema_indicator()
        df['20EMA'] = EMAIndicator(close=df['Close'], window=20, fillna=False).ema_indicator()
        df['50EMA'] = EMAIndicator(close=df['Close'], window=50, fillna=False).ema_indicator()
        df['200EMA'] = EMAIndicator(close=df['Close'], window=200, fillna=False).ema_indicator()
    
        super_trend = pdta.supertrend(high=df['High'], low=df['Low'], close=df['Close'], length=50, multiplier=4)
        df['Super_Trend'] = super_trend['SUPERTd_50_4.0']
        
        df["Max"] = df['High'].rolling(window=40, min_periods=1).max()
        df["Min"] = df['Low'].shift(1).rolling(window=40, min_periods=1).min()
    
    
        # ----------------------------------FEBONACY RETECHMENT----------------------------------
        def find_closest_fib_level(close_price, fib_levels, max_val, min_val):
            levels = [min_val + level * (max_val - min_val) for level in fib_levels]
            distances = [abs(level - close_price) for level in levels]
            closest_index = distances.index(min(distances))
            closest_level = fib_levels[closest_index]
            distance = round(distances[closest_index], 2)
            return closest_level, distance
    
        fib_levels = [1.33, 1.0, 0.67, 0.61, 0.33, -0.33]
        
        df['Close_Feb_Ret'] = df.apply(lambda row: find_closest_fib_level(row['Close'], fib_levels, row['Max'], row['Min']), axis=1)
        
        #  ----------------------------------CHECK EMA TOUCH----------------------------------
        def Check_EMA_Test(row, n=1):
            if  pd.notna(row['50EMA']) and pd.notna(row['200EMA']):
                ema_50test = row['Low'] - n <= row['50EMA'] <= row['High'] + n
                ema_200test = row['Low'] - n <= row['200EMA'] <= row['High'] + n
                return ema_50test, ema_200test
            else:
                return False, False
        df[['50EMA_Test', '200EMA_Test']] = df.apply(Check_EMA_Test, axis=1, result_type='expand')
        df['50EMA_Test'] = df['50EMA_Test'].rolling(window=2).apply(lambda x: any(x), raw=True).astype(bool)
        df['200EMA_Test'] = df['200EMA_Test'].rolling(window=2).apply(lambda x: any(x), raw=True).astype(bool)
    
        # ----------------------------CHEKING ENTRYES-------------------------
        

        
        # ----------------------------------5 EMA CE PE---------------------------------- 
        ce_5ema = (df['High'].shift(1) < df['5EMA'].shift(1)) & (df['Close'] >= df['5EMA'])
        pe_5ema = (df['Low'].shift(1) > df['5EMA'].shift(1)) & (df['Close'] <= df['5EMA'])
        
        df['Signal_5EMA'] = np.select([ce_5ema, pe_5ema],['CE', 'PE'], default='0')
        # ----------------------------------15 EMA CE PE---------------------------------- 
        ce_ema_crossover = (df['5EMA'] > df['20EMA']) & (df['5EMA'].shift(1) <= df['20EMA'].shift(1))
        pe_ema_crossover = (df['5EMA'] < df['20EMA']) & (df['5EMA'].shift(1) >= df['20EMA'].shift(1))
        
        df['Signal_EMA_CROSSOVER'] = np.select([ce_ema_crossover, pe_ema_crossover],['CE', 'PE'], default='0')
    
        # ----------------------------------FINAL ENTRY STATUS---------------------------------- 
    
        df['Feb&Trend'] = df.apply(lambda row: 'CE' if row['Super_Trend'] == 1 and row['Close_Feb_Ret'][0] <= 0.7 and row['Close_Feb_Ret'][1] <= 40 else 'PE', axis=1)
    
        ce_5ema = ((df['Feb&Trend'] == "CE") & (df['Signal_5EMA'] == "CE")) | ((df['Feb&Trend'] == "CE") & (df['Signal_EMA_CROSSOVER'] == "CE")) | ((df['50EMA_Test'] | df['200EMA_Test']) & (df['Feb&Trend'] == "CE"))
        pe_5ema = ((df['Feb&Trend'] == "PE") & (df['Signal_5EMA'] == "PE")) | ((df['Feb&Trend'] == "PE") & (df['Signal_EMA_CROSSOVER'] == "PE")) | ((df['50EMA_Test'] | df['200EMA_Test']) & (df['Feb&Trend'] == "PE"))
    
        df['5EMA_Feb&Trend_SIGNAL'] = np.select([ce_5ema, pe_5ema], ['CE', 'PE'], default='NONE')
    
        
        delete_column_name = ['50EMA_Test','200EMA_Test','Max','Min','Feb&Trend','Signal_EMA_CROSSOVER','Signal_5EMA','200EMA','50EMA']
        df = df.drop(columns= delete_column_name)
        df = df.dropna()
    except :
        df = pd.DataFrame([])
    return df
    
# Symbol = "NSE:NIFTY50-INDEX"
# df = Data_Get(Symbol,15)