import pandas as pd
import datetime
import yfinance as yf
import pandas as pd
import time



def get_data(day,inter):
    try:
        symbol = '^NSEI'
        period = f'{day}d'
        interval = f"{inter}m"
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)
        df.reset_index(drop=False, inplace=True)
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        df['Date'] = df['Datetime'].dt.date
        df['Time'] = df['Datetime'].dt.time
        df['Pivot'] = (df['High'] + df['Low'] + df['Close']) / 3
        date_range = pd.DatetimeIndex(df['Date'])
        df.drop(columns=["Volume","Dividends","Stock Splits"],inplace=True)
        return df.sort_index(ascending=False)
    except:
        return None

def Main_DataFrame(day,inter,status=None):

    if status == "LIVE":
        now = datetime.datetime.now()
        if now.hour >= 9 and now.hour <= 23 :
            print("-------------------- Current Time:", now.strftime("%H:%M"),"--------------------")
            print("--------------------[LIVE]--------------------")
            data_df = get_data(day,inter)  
        else:
            print("----------------------- TODAYS MARKET OFF -----------------------")
            data_df = get_data(day,inter)  
            # data_df = None
        return data_df
           
    else:
        print("--------------------[RECAPE]--------------------")
        return get_data(day,inter)





