
from ta import momentum,trend
import math

def sigmoid(x):
    return 1 / (1 + math.exp(-x))
# Sub Function for Prediction
def myml_model(row):
    rsi = row[9]
    trend = row[10]
    macd = row[13]
    adx = row[14]

    probability = 0
    if not math.isnan(rsi):
        probability += 10/int(rsi)
    if trend == "Uptrend":
        probability += 1

    if macd<=0:
        probability += -0.5
    if not math.isnan(adx):
        probability += int(adx)/100


    if sigmoid(probability) >=0.7:
        probability = "Buy"
    else:
        probability = "Sell"
    return probability


def Shell_Buy_prob(df):
    df= df.sort_index(ascending=True)
    # RSI
    # SMA20/40
    # TREND
    def Find_Up(df):
        data = df[0]<df[1]
        if data==True:
            return "Green"
        else:
            return "Red"
    df['Canndel']= df[['Open','Close']].apply(Find_Up,axis=1)
    df['SMA20'] = df['Close'].rolling(window=20*25).mean()
    df['SMA40'] = df['Close'].rolling(window=40*25).mean()
    df['RSI'] = momentum.RSIIndicator(df['Close'], window=5).rsi()
    df['Trend'] = 'Sideways'
    df.loc[df['Close'] > df['SMA20'], 'Trend'] = 'Uptrend'
    df.loc[df['Close'] < df['SMA20'], 'Trend'] = 'Downtrend'
    # MACD
    df['MACD_Blue'] = trend.MACD(df['Close']).macd()
    df['MACD_Red'] = trend.MACD(df['Close']).macd_signal()
    df['MACD_Value'] = df['MACD_Blue'] - df['MACD_Red']
    df = df.drop(columns=["SMA20","SMA40"], axis=1)

    df = df.sort_index(ascending=True)
    # Calculate True Range (TR)
    df['tr1'] = df['High'] - df['Low']
    df['tr2'] = abs(df['High'] - df['Close'].shift())
    df['tr3'] = abs(df['Low'] - df['Close'].shift())
    df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)

    # Calculate the Positive Directional Indicator (+DI) and Negative Directional Indicator (-DI)
    df['dmp'] = df['High'].diff()
    df['dmn'] = -df['Low'].diff()
    df['dmp'] = df['dmp'].apply(lambda x: x if x > 0 else 0)
    df['dmn'] = df['dmn'].apply(lambda x: x if x > 0 else 0)

    # Calculate the Smoothed True Range (ATR)
    atr_window = 14
    df['atr'] = df['tr'].rolling(window=atr_window).mean()

    # Calculate +DI and -DI
    di_window = 14
    df['+di'] = (df['dmp'].rolling(window=di_window).sum() / df['atr']) * 100
    df['-di'] = (df['dmn'].rolling(window=di_window).sum() / df['atr']) * 100

    # Calculate the Directional Movement Index (DX)
    df['dx'] = (abs(df['+di'] - df['-di']) / (df['+di'] + df['-di'])) * 100

    # Calculate the ADX
    adx_window = 14
    df['adx'] = df['dx'].rolling(window=adx_window).mean()
    columns_to_drop = ['tr1', 'tr2', 'tr3', 'dmp', 'dmn', 'tr','atr','+di','-di','dx']
    df = df.drop(columns=columns_to_drop, axis=1)

    # MAIN FUNCTION
    df["Predict"] = df.apply(myml_model, axis=1)
    return df.sort_index(ascending=False)
 