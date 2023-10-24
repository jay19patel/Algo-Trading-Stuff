


class Main_Patten_finder():
    
    def All_Data_Candle(df):
        df["upper_shadow"] = df.apply(lambda row: row['High'] - max(row['Open'], row['Close']),axis=1)
        df["lower_shadow"] = df.apply(lambda row: min(row['Open'], row['Close']) - row['Low'],axis=1)
        # Calculate body length
        df["body"] = abs(df["Close"] - df["Open"])
        df["full"] = df['High'] - df['Low']

        # Create a new column for the candle type
        df["Candle"] = df.apply(lambda row: "Green" if row["Close"] >= row["Open"] else "Red", axis=1)
        return df

    def Find_Pattern_all(df):
        df['Prev_Open'] = df['Open'].shift(1)
        df['Prev_Close'] = df['Close'].shift(1)
        df['Prev_High'] = df['High'].shift(1)
        df['Prev_Low'] = df['Low'].shift(1)
        df['Prev_Candle'] = df['Candle'].shift(1)

        df['Next_Open'] = df['Open'].shift(-1)
        df['Next_Close'] = df['Close'].shift(-1)
        df['Next_High'] = df['High'].shift(-1)
        df['Next_Low'] = df['Low'].shift(-1)
        df['Next_Candle'] = df['Candle'].shift(-1)

        def engulfing_bearish(row):
            data = row["Prev_Candle"] == "Green" and row["Open"]>=row["Prev_Close"] and row["Close"]<= row["Prev_Open"] and row['Next_Candle']=="Red"
            return data

        def engulfing_bullish(row):
            data= row["Prev_Candle"] == "Red" and row["Open"]<=row["Prev_Close"] and row["Close"]>= row["Prev_Open"] and row['Next_Candle']=="Green"
            return data   
        
        def is_doji(row):
            n = 5 
            data = row["body"] < row['full']/n and row['upper_shadow'] >= n * row["body"] and row['lower_shadow'] >= n * row["body"]
            return data

        def is_dragonfly_doji(row):
            n=5
            data =  row["body"] < row['full']/n and row['upper_shadow'] *2 < row['lower_shadow']
            return data

            
        def is_gravestone_doji(row):
            n=5
            data =  row["body"] < row['full']/n and row['upper_shadow'] > row['lower_shadow']*2
            return data
        
        def evning_bearish(row):
            prev_body = abs(row["Prev_Close"] - row["Prev_Open"])
            data = row["Prev_Candle"] == "Green" and row["Next_Candle"] =="Red" and  prev_body > row["body"]
            return data

        def morning_bullish(row):
            prev_body = abs(row["Prev_Close"] - row["Prev_Open"])
            data = row["Prev_Candle"] == "Red" and row["Next_Candle"] =="Green" and  prev_body > row["body"]
            return data
        
        def is_hammer(row):
            data = row['upper_shadow'] *2 < row['lower_shadow'] 
            return data

        def is_shooting_star(row):
            data =  row['upper_shadow'] > row['lower_shadow']*2 
            return data
        
        def harami_bearish(row):
            prev_body = abs(row["Prev_Close"] - row["Prev_Open"])
            data = row["Prev_Candle"] == "Green" and  prev_body > row["body"]*2 and row["High"]<row["Prev_High"] and row["Close"] < row["Prev_Close"]
            return data

        def harami_bullish(row):
            prev_body = abs(row["Prev_Close"] - row["Prev_Open"])
            data = row["Prev_Candle"] == "Red" and  prev_body > row["body"]*2 and row["High"]<row["Prev_High"] and row["Close"] < row["Prev_Close"]
            return data

        df['Engulfing_Bullish'] = df.apply(engulfing_bullish, axis=1)
        df['Engulfing_Bearish'] = df.apply(engulfing_bearish, axis=1)
        df['Is_Doji'] = df.apply(is_doji, axis=1)
        df['Is_Dragonfly_Doji'] = df.apply(is_dragonfly_doji, axis=1)
        df['Is_Gravestone_Doji'] = df.apply(is_gravestone_doji, axis=1)
        df['Evning_Bullish'] = df.apply(evning_bearish, axis=1)
        df['Morning_Bearish'] = df.apply(morning_bullish, axis=1)
        df['Is_Hammer'] = df.apply(is_hammer, axis=1)
        df['Is_Shooting_Star'] = df.apply(is_shooting_star, axis=1)
        df['Harami_Bullish'] = df.apply(harami_bearish, axis=1)
        df['Harami_Bearish'] = df.apply(harami_bullish, axis=1)

        removelist = ['Open',
        'High',
        'Low',
        'Close',
        'upper_shadow',
        'lower_shadow',
        'body',
        'full',
        'Candle',
        'Prev_Open',
        'Prev_Close',
        'Prev_High',
        'Prev_Low',
        'Prev_Candle',
        'Next_Open',
        'Next_Close',
        'Next_High',
        'Next_Low',
        'Next_Candle']

        df = df.drop(columns=removelist,inplace=True)
        return df
