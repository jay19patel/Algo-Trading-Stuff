import yfinance as yf
import datetime
import ta
import datetime
from ta import momentum, trend


symbol = "^NSEI"
ticker = yf.Ticker(symbol)
end_date = datetime.date.today()
df = ticker.history(period="5d", interval="5m")



# start_date = datetime.date(2023, 10, 10)  
# end_date = datetime.date(2023, 10, 11)  

# df = df[(df.index.date >= start_date) & (df.index.date <= end_date)]







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


df['Prev_Open'] = df['Open'].shift(1)
df['Prev_Close'] = df['Close'].shift(1)
df['Prev_High'] = df['High'].shift(1)
df['Prev_Low'] = df['Low'].shift(1)
df['Prev_Candle'] = df['Canndel'].shift(1)


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

# ---------------------------- PE -------------------------------

# Decalaration
pe_current_position = None
PE_HOLDING = False
pe_inisal_amount = 0



def find_10EMA_PE(row):
    global PE_HOLDING
    global pe_inisal_amount
    global pe_current_position
    lot_size = 1
    pe_current_price = row['Close'] * lot_size
    # ------------------------------- ENTRY -------------------------------------------
    
    if row['10EMA'] > row['Close']:
        if row['Canndel'] == "Green":
            if not PE_HOLDING:
                pe_current_position = row['Close']
                PE_HOLDING = True
                print("STATUS : -----[PE ENTRY]-----")
                print("Position :",row['Close'])
                print("Date Time :",row['Date'],row['Time'])
                print("\n")

                return

    # ------------------------------- EXIT -------------------------------------------

    if row['10EMA'] < row['Close']:
        if row['Canndel'] == "Green":
            if PE_HOLDING:
                current_pnl  = pe_current_position - row['Close']
                pe_inisal_amount = pe_inisal_amount + current_pnl
                PE_HOLDING = False
                print("STATUS : -----[PE EXIT]-----")
                print("Date Time :",row['Date'],row['Time'])
                print("Position :",pe_current_position)
                print("Current Position :",row['Close'])
                print("Current P&L:",current_pnl)
                print("pe_inisal_amount:",pe_inisal_amount)
                print("\n")
                return



df.apply(find_10EMA_PE, axis=1)


# ---------------------------- CE -------------------------------

# Decalaration
ce_current_position = None
CE_HOLDING = False
ce_inisal_amount = 0



def find_10EMA_CE(row):
    global CE_HOLDING
    global ce_inisal_amount
    global ce_current_position

    lot_size = 1
    ce_current_price = row['Close'] * lot_size
    # ------------------------------- ENTRY -------------------------------------------
    
    if row['10EMA'] < row['Close']:
        if row['Canndel'] == "Red":
            if not CE_HOLDING:
                ce_current_position = row['Close']
                CE_HOLDING = True
                print("STATUS : -----[CE ENTRY]-----")
                print("Position :",row['Close'])
                print("Date Time :",row['Date'],row['Time'])
                print("\n")
                return

    # ------------------------------- EXIT -------------------------------------------

    if row['10EMA'] > row['Close']:
        if row['Canndel'] == "Red":
            if CE_HOLDING:
                current_pnl  = row['Close'] - ce_current_position
                ce_inisal_amount = ce_inisal_amount + current_pnl
                CE_HOLDING = False
                print("STATUS : -----[CE EXIT]-----")
                print("Date Time :",row['Date'],row['Time'])
                print("Position :",ce_current_position)
                print("Current Position :",row['Close'])
                print("Current P&L:",current_pnl)
                print("pe_inisal_amount:",ce_inisal_amount)
                print("\n")
                return
            

    # ------------------------------- EXIT -------------------------------------------
df.apply(find_10EMA_CE, axis=1)
if CE_HOLDING:
    last_price_today = round(df.iloc[-1]['Close'],2)
    print(last_price_today)
    print("PE Holding---------------------------")
    current_pnl  = last_price_today - ce_current_position
    print(current_pnl)
    ce_inisal_amount = ce_inisal_amount + current_pnl


if PE_HOLDING:
    last_price_today = round(df.iloc[-1]['Close'],2)
    print(last_price_today)
    print("PE Holding---------------------------")
    current_pnl  = last_price_today - pe_current_position
    print(current_pnl)
    pe_inisal_amount = pe_inisal_amount + current_pnl


print("TOTAL CE : ",ce_inisal_amount)
print("TOTAL PE: ",pe_inisal_amount)



    # if row['Prev_Candle']=="Green"  and row['Prev_10EMA'] < row['Prev_Low'] and row['Low'] < row['Prev_Low']  :
