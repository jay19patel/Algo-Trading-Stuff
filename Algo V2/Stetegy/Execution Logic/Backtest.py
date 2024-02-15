import pandas as pd
import pytz
from datetime import datetime, timedelta

from Fyers import Fyers


# --------------------------- BACKTEST MODEL ------------------------------



# ----------------------GET DATAFRAME-----------------------------
def generate_and_save_historical_data(fyers, num_days,interval):
    start_date = datetime.now() - timedelta(days=num_days)
    end_date = datetime.now()

    date_range_list = []
    current_date = start_date

    while current_date <= end_date:
        last_day_current = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        last_day_next = (last_day_current.replace(day=1) + timedelta(days=62)).replace(day=1) - timedelta(days=1)
        date_range_list.append((current_date, last_day_next))
        current_date = last_day_next + timedelta(days=1)

    print(date_range_list)
    mydf = pd.DataFrame({})
    for start_date, end_date in date_range_list:
        data = {
            "symbol": "NSE:NIFTY50-INDEX",
            "resolution": interval,
            "date_format": "1",
            "range_from": start_date.strftime('%Y-%m-%d'),
            "range_to": end_date.strftime('%Y-%m-%d'),
            "cont_flag": "0"
        }
        row_data = fyers.fyers_instance.history(data=data)
        df = pd.DataFrame.from_dict(row_data['candles'])
        mydf = pd.concat([mydf, df], ignore_index=True)

    columns_name = ['Datetime','Open','High','Low','Close','Volume']
    mydf.columns = columns_name
    mydf['Datetime'] = pd.to_datetime(mydf['Datetime'], unit='s')
    mydf['Datetime'] = mydf['Datetime'].dt.tz_localize(pytz.utc).dt.tz_convert('Asia/Kolkata')
    mydf['Datetime'] = mydf['Datetime'].dt.tz_localize(None)

    return mydf



