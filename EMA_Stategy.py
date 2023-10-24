import yfinance as yf
import datetime
import ta
import datetime
from ta import momentum, trend

symbol = "^NSEI"
ticker = yf.Ticker(symbol)
end_date = datetime.date.today()
df = ticker.history(period="20d", interval="5m")
df['Date'] = df.index.date
df['Time'] = df.index.time

from ta import momentum,trend
df['50EMA'] = trend.EMAIndicator(df['Close'], window=50).ema_indicator()
df['10EMA'] = trend.EMAIndicator(df['Close'], window=10).ema_indicator()



def Find_Up(df):
    data = df[0]<df[1]
    if data==True:
        return "Green"
    else:
        return "Red"
df['Canndel']= df[['Open','Close']].apply(Find_Up,axis=1)


df['SMA20'] = df['Close'].rolling(window=20).mean()
df['SMA40'] = df['Close'].rolling(window=40).mean()
df['Trend'] = 'Sideways'
df.loc[df['Close'] > df['SMA20'], 'Trend'] = 'Uptrend'
df.loc[df['Close'] < df['SMA20'], 'Trend'] = 'Downtrend'
del df['SMA20']
del df['SMA40']
del df['Volume']
del df['Dividends']
del df['Stock Splits']


PE_HOLDING = False
pe_inisal_amount = 30000

def find_10EMA_PE(row):
    global PE_HOLDING
    global pe_inisal_amount
    lot_size = 1
    pe_current_price = row['Close'] * lot_size
    
    if row['10EMA'] > row['Close']:
        if row['Canndel'] == "Green":
            if not PE_HOLDING:
                print(f"PE ENTRY ---------------[{row['Date']} [{row['Time']}]]---------")
                pe_inisal_amount = pe_inisal_amount - pe_current_price
                PE_HOLDING = True
    elif row['10EMA'] < row['Close']:
        if row['Canndel'] == "Green":
            if PE_HOLDING:
                print(f"PE EXIT ---------------[{row['Date']} [{row['Time']}]]---------")
                pe_inisal_amount = pe_inisal_amount + pe_current_price
                PE_HOLDING = False

    # else:
    #     print("SIDEWAY")

df.apply(find_10EMA_PE, axis=1)
if PE_HOLDING == True :
    print("HOLDING")
    pe_last_price_today = round(df.iloc[1]['Close'],2)*1
    print(pe_last_price_today)
    print("MY AMOUNT : 30000 ")
    print("TOTAL RETURNS  : ",pe_last_price_today + pe_inisal_amount)
    print("MY P&L : ",pe_last_price_today + pe_inisal_amount-30000)
    pe_percentage = (100 * (pe_last_price_today + pe_inisal_amount-30000))/30000 
    print(f"MY P& %: {pe_percentage}%")
    
else:
    print("MY AMOUNT : 30000 ")
    print("TOTAL RETURNS  : ",pe_inisal_amount)
    print("MY P&L : ",pe_inisal_amount-30000)
    pe_percentage = (100 * (pe_inisal_amount-30000))/30000 
    print(f"MY P&L %: {pe_percentage}%")




CE_HOLDING = False
ce_inisal_amount = 30000

def find_10EMA_CE(row):
    global CE_HOLDING
    global ce_inisal_amount
    lot_size = 1
    ce_current_price = row['Close'] * lot_size
    
    if row['10EMA'] > row['Close']:
        if row['Canndel'] == "Green":
            if not CE_HOLDING:
                print(f"CE ENTRY ---------------[{row['Date']} [{row['Time']}]]---------")
                ce_inisal_amount = ce_inisal_amount + ce_current_price
                CE_HOLDING = True
    elif row['10EMA'] < row['Close']:
        if row['Canndel'] == "Green":
            if CE_HOLDING:
                print(f"CE EXIT ---------------[{row['Date']} [{row['Time']}]]---------")
                ce_inisal_amount = ce_inisal_amount - ce_current_price
                CE_HOLDING = False

    else:
        print("SIDEWAY")


df.apply(find_10EMA_CE, axis=1)
if CE_HOLDING == True :
    print("HOLDING")
    ce_last_price_today = round(df.iloc[1]['Close'],2)*1
    print(ce_last_price_today)
    print("MY AMOUNT : 30000 ")
    print("TOTAL RETURNS  : ",ce_last_price_today + ce_inisal_amount)
    print("MY P&L : ",ce_last_price_today + ce_inisal_amount-30000)
    percentage = (100 * (ce_last_price_today + ce_inisal_amount-30000))/30000 
    print(f"MY P& %: {percentage}%")
    
else:
    print("MY AMOUNT : 30000 ")
    print("TOTAL RETURNS  : ",ce_inisal_amount)
    print("MY P&L : ",ce_inisal_amount-30000)
    percentage = (100 * (ce_inisal_amount-30000))/30000 
    print(f"MY P&L %: {percentage}%")








