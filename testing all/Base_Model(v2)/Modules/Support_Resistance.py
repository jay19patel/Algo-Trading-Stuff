import pandas as pd
import datetime
import yfinance as yf
import pandas as pd



def n_day_support_resistance(day_n,num):
        start_date = "2023-01-01"
        today = datetime.date.today()
        symbol = "^NSEI"
        data = yf.download(symbol, start=start_date, end=today)
        df = pd.DataFrame(data)
        df = df.astype(int)
        df.reset_index(drop=False, inplace=True)
        df['Date'] = pd.to_datetime(df['Date'])
        df_group_n_day =df.tail(day_n)
        n_day_high = df_group_n_day.sort_values(by='High', ascending=False).head(num)[['High']]
        n_day_low = df_group_n_day.sort_values(by='Low', ascending=True).head(num)[["Low"]]
        previous_day_df = df.tail(num).sort_index(ascending=False)
        return {"n_Day_High":n_day_high.values.ravel().tolist(),
                "n_Day_Low":n_day_low.values.ravel().tolist(),
                "3_previous_day":list(zip(previous_day_df['High'], previous_day_df['Low']))}
    
def high_fz_leveles(df,n_days,n,ln):
        df = df.head(n_days*25)
        # df = Dataframe , n = range points , ln = return values (ketli values joyyes)
        def count_m_values(row):
                m_counts = {}
                for m in range(int(row['Low']) - n, int(row['High']) + n + 1):
                        m_counts[m] = m_counts.get(m, 0) + 1
                return pd.Series(m_counts)
        m_counts_df = df.apply(count_m_values, axis=1).fillna(0).astype(int)
        total_counts = m_counts_df.sum()
        max_candle_re = total_counts.reset_index().rename(columns={'index': 'm', 0: 'Count'}).sort_values(by='Count', ascending=False)
        max_candle_re['m_diff'] = max_candle_re['m'].diff().abs()
        filtered_max_candle_re = max_candle_re[(max_candle_re['m_diff'] >= 20)]
        filtered_max_candle_re = filtered_max_candle_re.drop('m_diff', axis=1).head(ln)
        return list(zip(filtered_max_candle_re['m'], filtered_max_candle_re['Count']))



