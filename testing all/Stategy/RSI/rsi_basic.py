import yfinance as yf
import pandas as pd
import ta
import datetime

class RSIAnalysis:
    def __init__(self, symbol, start_date, end_date):
        self.symbol = symbol
        self.start_date = start_date
        self.end_date = end_date
        self.interval_data = None
        self.daily_data = None

    def download_data(self):
        # Download interval data (15 minutes)
        self.interval_data = yf.download(self.symbol, start=self.start_date, end=self.end_date, interval='5m')
        self.interval_data.drop(columns=['Adj Close', 'Volume'], inplace=True)
        self.interval_data = self.interval_data.astype(int)

        # Download daily data
        self.daily_data = yf.download(self.symbol, start=self.start_date, end=datetime.date.today(), interval='1d')
        self.daily_data = self.daily_data.astype(int)

    def add_previous_day_data(self, row):
        date = row.name.date()
        previous_date = date - pd.DateOffset(days=1)

        if previous_date in self.daily_data.index:
            previous_day_data = self.daily_data.loc[previous_date]
            row['Previous_Day_Open'] = previous_day_data['Open']
            row['Previous_Day_High'] = previous_day_data['High']
            row['Previous_Day_Low'] = previous_day_data['Low']
            row['Previous_Day_Close'] = previous_day_data['Close']

        return row

    def calculate_daily_high_low(self):
        self.daily_data['Daily_High'] = self.daily_data['High'].shift()
        self.daily_data['Daily_Low'] = self.daily_data['Low'].shift()

        for date, daily_row in self.daily_data.iterrows():
            mask = self.interval_data.index.date == date.date()
            self.interval_data.loc[mask, 'Daily_High'] = daily_row['Daily_High']
            self.interval_data.loc[mask, 'Daily_Low'] = daily_row['Daily_Low']

    def calculate_rsi_strategy(self, rsi_window=4):
        self.interval_data['RSI'] = ta.momentum.RSIIndicator(self.interval_data['Close'], window=rsi_window).rsi()

        def rsi_strategy(row):
            row_dict = row[['Previous_Day_High', 'Previous_Day_Low', 'Previous_Day_Close', 'Daily_High', 'Daily_Low']].to_dict()
            close = row['Close']
            min_key = min(row_dict, key=lambda key: abs(row_dict[key] - close))
            min_value = row_dict[min_key]
            min_difference = abs(min_value - close)

            if (row['RSI'] <= 30) and min_difference <= 50:
                return "Bullish"
            elif (row['RSI'] >= 70) and min_difference <= 50:
                return "Bearish"
            else:
                return None

        self.interval_data['Status'] = self.interval_data.apply(rsi_strategy, axis=1)
        self.interval_data = self.interval_data.sort_values(by='Datetime', ascending=False)

    def run_analysis(self):
        self.download_data()
        self.interval_data = self.interval_data.apply(self.add_previous_day_data, axis=1)
        self.calculate_daily_high_low()
        self.calculate_rsi_strategy()

if __name__ == "__main__":
    symbol = '^NSEI'
    start_date = pd.Timestamp.now() - pd.DateOffset(days=10)
    end_date = pd.Timestamp.now()
    analysis = RSIAnalysis(symbol, start_date, end_date)
    analysis.run_analysis()
    print(analysis.interval_data.iloc[0])
