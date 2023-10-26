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


#  Trend Finder
df['EMA20'] = df['Close'].ewm(span=20, adjust=False).mean()
df['SMA40'] = df['Close'].rolling(window=40).mean()
range_threshold = 10
df['Trend'] = 'None'
df.loc[df['EMA20'] > df['SMA40'], 'Trend'] = 'Uptrend'

df.loc[df['EMA20'] < df['SMA40'], 'Trend'] = 'Downtrend'

df.loc[abs(df['EMA20'] - df['SMA40']) <= range_threshold, 'Trend'] = 'Sideways'


def Find_Up(row):
    if row['Close'] > row['Open']:
        return "Green"
    else:
        return "Red"

df['Canndel'] = df.apply(Find_Up, axis=1)


df['Prev_Open'] = df['Open'].shift(1)
df['Prev_Close'] = df['Close'].shift(1)
df['Prev_High'] = df['High'].shift(1)
df['Prev_Low'] = df['Low'].shift(1)
df['Prev_Candle'] = df['Canndel'].shift(1)
df['Prev_50EMA'] = df['50EMA'].shift(1)
df['Prev_10EMA'] = df['10EMA'].shift(1)


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
    if row['Prev_Candle']=="Green" and row['Prev_10EMA'] < row['Prev_Open'] and row['Canndel'] == "Red":
            if not PE_HOLDING:
                pe_current_position = row['Close']
                PE_HOLDING = True
                print("STATUS : -----[PE ENTRY]-----")
                print("Position :",row['Close'])
                print("Date Time :",row['Date'],row['Time'])
                print("Trend :",row['Trend'])
                print("\n")

                return

    # ------------------------------- EXIT -------------------------------------------
    above = abs(row['10EMA'] - row['Close'])
    total_range = abs(row['Low'] - row['High'])
    above_percentage = (above / total_range) * 100 if total_range != 0 else 0
    if row['10EMA'] < row['Low']  and above_percentage > 40 and row['Canndel'] == "Green":
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
    if row['Prev_Candle']=="Red" and row['Prev_10EMA'] > row['Prev_High'] and row['Canndel'] == "Green" and row['Trend'] == "Uptrend":
            if not CE_HOLDING:
                ce_current_position = row['Close']
                CE_HOLDING = True
                print("STATUS : -----[CE ENTRY]-----")
                print("Position :",row['Close'])
                print("Date Time :",row['Date'],row['Time'])
                print("Trend :",row['Trend'])
                print("\n")
                return

    # ------------------------------- EXIT -------------------------------------------
    above = abs(row['10EMA'] - row['Close'])
    total_range = abs(row['Low'] - row['High'])
    above_percentage = (above / total_range) * 100 if total_range != 0 else 0
    # if row['10EMA'] > row['Low'] and above_percentage < 40 and row['Canndel'] == "Red":
    if row['10EMA'] > row['Close'] and row['Canndel'] == "Red":
            if CE_HOLDING:
                print("----------------------------",above_percentage)
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


