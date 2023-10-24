

from Modules.Support_Resistance import n_day_support_resistance,high_fz_leveles
from Modules.Time_frame_data import Main_DataFrame
from Modules.Indicator import Candle_patten_trend_rsi,candle_adx
from Modules.Patten_finder import Main_Patten_finder
from Modules.Final_Buy_Sall import Shell_Buy_prob

import pandas as pd

def Main():
# --------------------------------------------------------------------------------------------------
   
    # NEED DATAFRAME FOR N DAY DATA FOR 5 MINUTES INTERVEL
    print(f"-------------------------------[DATAFRAME TIMEFRAME]------------------------------------")
    day_need_data = 10 # Day for Analysis
    minutes = 5 # Time frame for candles (5,10,15,30)
    df = Main_DataFrame(day_need_data,minutes,"LIVE")
# --------------------------------------------------------------------------------------------------

    # No need DF
    # NEED RESISTNACE AND SUPPORT FOR LAST N DAY DAYA RETURN N DAY DATA
    # print(f"-------------------------------[N DAY S & P]------------------------------------")
    # day = 5  #Total n Day for analysis
    # num = 3  # return n data set 
    # print(n_day_support_resistance(day,num))

# --------------------------------------------------------------------------------------------------

    # FIND THE HIGH OCILATE CANDLES RANGE AND RETURN 
    # print(f"-------------------------------[LEVELS]------------------------------------")
    # range_candle = 1 #incress n points into ranges 
    # num_return = 4 # n data set return
    # n_days = 2 # n day for analysis 
    # print(high_fz_leveles(df,n_days,range_candle,num_return))

# --------------------------------------------------------------------------------------------------
    # FIND A CANDLE PATTENS 
    # print(f"-------------------------------[CANDLE RSI & PATEN]------------------------------------")
    # patten_data = Candle_patten_trend_rsi(df,2)
    # # single_last_data = patten_data.head(1).to_dict()
    # rsi_trend_data= patten_data.head(2)
    # print(rsi_trend_data[["Date","Time","Pivot","Canndel","RSI","Trend","MACD_Value"]].to_string(index=False))

# --------------------------------------------------------------------------------------------------
    # print(f"-------------------------------[CANDLE ADX]------------------------------------")
    # adx_data = candle_adx(df).head(2)
    # print(adx_data)

# --------------------------------------------------------------------------------------------------
    # print(f"-------------------------------[CANDLE PATTERN FINDER]------------------------------------")
    # all_data_of_candle = Main_Patten_finder.All_Data_Candle(df)
    # all_data_of_pattern = Main_Patten_finder.Find_Pattern_all(all_data_of_candle)
    # last_row = df.iloc[1]
    # print(last_row)

# --------------------------------------------------------------------------------------------------
    # print(f"-------------------------------[BUY & SALL]------------------------------------")

    Final_data_prob = Shell_Buy_prob(df)
    print(Final_data_prob.iloc[0])



if __name__ =='__main__':
    Main()





