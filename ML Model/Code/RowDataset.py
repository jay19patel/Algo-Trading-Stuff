from fyers_apiv3 import fyersModel
from datetime import datetime , timedelta
import pandas as pd
import pytz
from Fyers import Fyers


fyers_obj  = Fyers()
fyers_obj.authentication()

def Historical_Data(Symbol,TimeFrame,startdate,enddate):
    data = {
            "symbol":Symbol,
            "resolution": TimeFrame,
            "date_format":"1",
            "range_from":startdate,
            "range_to":enddate,
            "cont_flag":"0"
            }
    row_data =  fyers_obj.fyers_instance.history(data=data)
    return row_data



from datetime import datetime, timedelta
def generate_date_range(years):
    current_date = datetime.now()
    past_date = current_date - timedelta(days=years*365)  
    date_ranges = []
    while past_date < current_date:
        next_date = past_date + timedelta(days=3*30)
        if next_date > current_date:
            next_date = current_date
        date_ranges.append((past_date, next_date))
        past_date = next_date + timedelta(days=1)
    return date_ranges


def fyers_Dataset(Symbol,TimeFrame,filename):
    data = []
    # here 1 is our yesr
    for i in  generate_date_range(1):
        startdate = i[0].date()
        enddate = i[1].date()
        df = Historical_Data(Symbol,TimeFrame,startdate,enddate)
        data.extend(df['candles'])

    import pandas as pd
    df = pd.DataFrame(data)

    columns_name = ['Datetime','Open','High','Low','Close','Volume']
    df.columns = columns_name
    df['Datetime'] = pd.to_datetime(df['Datetime'], unit='s')
    df['Datetime'] = df['Datetime'].dt.tz_localize(pytz.utc).dt.tz_convert('Asia/Kolkata')
    df['Datetime'] = df['Datetime'].dt.tz_localize(None)

    df.to_csv(filename, index=False)









