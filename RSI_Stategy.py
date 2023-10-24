import yfinance as yf
import datetime
import ta
import datetime
from ta import momentum, trend

symbol = "^NSEI"
ticker = yf.Ticker(symbol)
end_date = datetime.date.today()
df = ticker.history(period="2d", interval="5m")
df['Date'] = df.index.date
df['Time'] = df.index.time

df['RSI'] = round(momentum.RSIIndicator(df['Close'], window=4).rsi(),2)
df = df.dropna()
df = df[df['RSI'] != 0]
df['RSI_DATA'] = [df['RSI'][max(0, i-1):i+1].to_list() if i >= 4 else [] for i in range(len(df))]
def check_order(arr):
    increasing = all(arr[i] <= arr[i + 1] for i in range(len(arr) - 1))
    decreasing = all(arr[i] >= arr[i + 1] for i in range(len(arr) - 1))
    return "Increasing" if increasing else "Decreasing" if decreasing else "None"
df['RSI_Status'] = df['RSI_DATA'].apply(check_order)

pe_inisal_amount = 30000
PE_HOLDING = False

def RSI_STATEGY_PE(row):
    global pe_inisal_amount
    global PE_HOLDING
    lot_size = 50
    pe_current_price = row['Close'] * lot_size
    
    if row['RSI'] <= 30:
    # if row['RSI'] <= 30 and row['RSI_Status'] in ["Increasing", "None"]:
        if PE_HOLDING == False:
            print(f"------[{row['Date']}]----------------PE EXTRY --[{row['Time']}]---------------RSI [{row['RSI']}]--------------{row['Close']}-----------")
            pe_inisal_amount = pe_inisal_amount - pe_current_price
            PE_HOLDING = True
            
    elif row['RSI'] >= 60:
    # elif row['RSI'] >= 70 and row['RSI_Status'] == "Decreasing":
        if PE_HOLDING == True:
            print(f"-------[{row['Date']}]----------------PE EXIT --[{row['Time']}]-------------RSI [{row['RSI']}]-------------{row['Close']}------------")
            pe_inisal_amount = pe_inisal_amount + pe_current_price
            PE_HOLDING = False
df.apply(RSI_STATEGY_PE,axis = 1) 

if PE_HOLDING == True :
    print("HOLDING")
    pe_last_price_today = round(df.iloc[1]['Close'],2)*50
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


ce_inisal_amount = 30000
CE_HOLDING = False

def RSI_STATEGY_CE(row):
    global ce_inisal_amount
    global CE_HOLDING
    lot_size = 50
    ce_current_price = row['Close'] * lot_size
    
    if row['RSI'] <= 30:
    # if row['RSI'] <= 30 and row['RSI_Status'] in ["Increasing", "None"]:
        if CE_HOLDING == True:
            print(f"------[{row['Date']}]----------------CE EXIT--[{row['Time']}]---------------RSI [{row['RSI']}]--------------{row['Close']}-----------")
            ce_inisal_amount = ce_inisal_amount - ce_current_price
            CE_HOLDING = False
            
    elif row['RSI'] >= 70:
    # elif row['RSI'] >= 70 and row['RSI_Status'] == "Decreasing":
        if CE_HOLDING == False:
            print(f"-------[{row['Date']}]----------------CE ENTRY --[{row['Time']}]-------------RSI [{row['RSI']}]-------------{row['Close']}------------")
            ce_inisal_amount = ce_inisal_amount + ce_current_price
            CE_HOLDING = True
df.apply(RSI_STATEGY_CE,axis = 1) 

if CE_HOLDING == True :
    print("HOLDING")
    ce_last_price_today = round(df.iloc[1]['Close'],2)*50
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