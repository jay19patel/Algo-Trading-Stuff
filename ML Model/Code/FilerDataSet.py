import pandas as pd
import yfinance as yf
import pandas as pd
import datetime
from ta.trend import EMAIndicator
import pandas_ta as pdta
import numpy as np
import ta



temp = None
MaxList = list()
MinList = list()
def FindMinMax(row):
    global temp,MinList,MaxList
    # print(row["Trend"],temp)
    if temp!= None :
        if row["Trend"] == 1 and temp == 1:
            MaxList.append(row["High"])
        elif row["Trend"] == -1 and temp == -1:
            MinList.append(row["Low"])
            
        elif row["Trend"] == -1 and temp == 1:
            MinList.clear()
            MinList.append(row["Low"])
            temp = row["Trend"]
            
        elif row["Trend"] == 1 and temp == -1:
            MaxList.clear()
            MaxList.append(row["High"])
            temp = row["Trend"]

        return min(MinList),max(MaxList)
            
    else:
        temp = row["Trend"]
        MaxList.append(row["High"])
        MinList.append(row["Low"])
    
    return min(MinList),max(MaxList)
    
def GetMainDataSet():
    df = pd.read_csv("Private/Nifty50_5min.csv")
    df_day = pd.read_csv("Private/Nifty50_day.csv")
    df.drop(columns=['Volume'], inplace=True)
    df_day.drop(columns=['Volume'], inplace=True)

    super_trend = pdta.supertrend(high=df_day['High'], low=df_day['Low'], close=df_day['Close'], length=50, multiplier=4)
    df_day['Trend'] = super_trend['SUPERTd_50_4.0']
    df_day['Datetime'] = pd.to_datetime(df_day['Datetime'])
    df_day['Date'] = df_day['Datetime'].dt.date

    df_day[['SwingMin', 'SwingMax']] = df_day.apply(FindMinMax, axis=1, result_type='expand')
    df_day = df_day.add_prefix('Day_')

    df['Pivot'] = df[["High", "Low", "Close"]].mean(axis=1)
    df['Candle'] = df.apply(lambda row: 'Green' if row['Close'] >= row['Open'] else 'Red', axis=1)
    df['5EMA'] = EMAIndicator(close=df['Close'], window=5, fillna=False).ema_indicator()
    df['15EMA'] = EMAIndicator(close=df['Close'], window=15, fillna=False).ema_indicator()
    df['20EMA'] = EMAIndicator(close=df['Close'], window=20, fillna=False).ema_indicator()
    df['50EMA'] = EMAIndicator(close=df['Close'], window=50, fillna=False).ema_indicator()
    df['200EMA'] = EMAIndicator(close=df['Close'], window=200, fillna=False).ema_indicator()
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'],window=6).rsi()
    super_trend = pdta.supertrend(high=df['High'], low=df['Low'], close=df['Close'], length=50, multiplier=4)
    df['Trend'] = super_trend['SUPERTd_50_4.0']
    df['CandleBody'] = abs(df['Close'] - df['Open'])
    df.dropna(inplace=True)

    df[["Small_Swing_Min","Small_Swing_Max"]]=df.apply(FindMinMax, axis=1, result_type='expand')

    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df['Day_Date'] = df['Datetime'].dt.date

    merged_df = df_day.merge(df, on='Day_Date', how='inner')
    merged_df.dropna(inplace=True)
    merged_df.drop(['Day_Datetime'], axis=1, inplace=True)
    merged_df.to_csv("MainDataSet.csv",index=False)
