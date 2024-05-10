import pandas as pd

class Trader:
    def __init__(self,initial_balance=100000):
        self.balance = initial_balance
        self.trad_book = pd.DataFrame(columns=['IndexName', 'Side', 'Status', 'Quantity', 'BuyPrice',
                                               'BuyDatetime', 'SellPrice', 'SellDatetime','PnL', 'SLValue',
                                               'TargetValue', 'PnL Status'])
        

    def backtest(self, df):
        open_order = None
        side = None
        tg_order = None
        sl_order = None

        for index, row in df.iterrows():
            if row["Side"] != "None" and open_order is None:
                open_order = row["Price"]
                side = row["Side"]
                sl_order, tg_order = (open_order - 10, open_order + 10) if side == "CE" else (open_order + 10, open_order - 10)
                symbol = "Nifty50"
                quantity = 10
                new_log = pd.DataFrame({'IndexName': [symbol],'Side':[side],'Status':["Open"] ,'Quantity': [quantity], 'BuyPrice': [open_order],
                                'BuyDatetime': [row["Datetime"]], 'SellDatetime': [None], 'SellPrice': [None],
                                'PnL': [0],'SLValue': [sl_order], 'TargetValue': [tg_order], 'PnL Status': [None] })
                self.trad_book = pd.concat([self.trad_book, new_log], ignore_index=True)
            if open_order is not None:
                if (side == "CE" and (row["Price"] >= tg_order or row["Price"] <= sl_order)) or \
                   (side == "PE" and (row["Price"] <= tg_order or row["Price"] >= sl_order)):
                    pnl = row["Price"] - open_order if side == "CE" else open_order - row["Price"]
                    self.balance += pnl
                    
                    index = self.trad_book.shape[0] -1
                    self.trad_book.at[index, 'SellPrice'] = row["Price"]
                    self.trad_book.at[index, 'SellDatetime'] = row["Datetime"]
                    self.trad_book.at[index, 'Status'] = "Done"
                    self.trad_book.at[index, 'PnL'] = pnl
                    self.trad_book.at[index, 'PnL Status'] = "Profit" if  pnl >0  else "Loss"
                    self.trad_book.at[index, 'SellDatetime'] = row["Datetime"]
                    open_order = None

    
    def stats(self):
            df = self.trad_book
            total_trade = len(df.index)
            pnl = df.PnL.sum()
            winners = len(df[df.PnL > 0])
            losers = len(df[df.PnL <= 0])
            win_ratio = round((winners / total_trade) * 100, 2)
    
            # Calculate CE and PE trades
        
            ce_trades = f"{(len(df[(df['Side'] == 'CE') & (df['PnL'] > 0)]) / len(df[df['Side'] == 'CE']) * 100):.2f}%" if len(df[df['Side'] == 'CE']) != 0 else 0
            pe_trades = f"{(len(df[(df['Side'] == 'PE') & (df['PnL'] > 0)]) / len(df[df['Side'] == 'PE']) * 100):.2f}%" if len(df[df['Side'] == 'PE']) != 0 else 0

    
            # Calculate additional metrics
            capital = self.balance
            max_win = round(df[df.PnL > 0].PnL.max(), 2) if winners > 0 else 0
            max_profit_sum = round(df[df.PnL > 0].PnL.sum(), 2) if winners > 0 else 0
            max_loss = round(df[df.PnL <= 0].PnL.min(), 2) if losers > 0 else 0
            max_loss_sum = round(df[df.PnL <= 0].PnL.sum(), 2) if losers > 0 else 0
            total_profit = round(df.PnL.sum(), 2)
            total_profit_percentage = round((total_profit / self.balance) * 100, 2)
    
            # Prepare the data for tabular representation
            parameters = ['Total Trades', 'Capital', 'Total Wins', 'Total Losses', 'Win Ratio',
                          'Max Win', 'Max Win Score','Max Loss', 'Max Loss Score','Total Profit', ' Grow Profit %',
                          'CE Trades', 'PE Trades', 'Stategy Name']
            data_points = [total_trade, capital, winners, losers, f"{win_ratio}%",
                           max_win, max_profit_sum,max_loss, max_loss_sum,total_profit, f"{total_profit_percentage}%",
                           ce_trades, pe_trades, "Test"]
            data = list(zip(parameters, data_points))
    
            # Print the tabular representation
            print(tabulate(data, headers=['Parameters', 'Values'], tablefmt='psql'))
    
            excel_file = "statistics.xlsx"
            try:
                existing_df = pd.read_excel(excel_file)
                new_data = pd.DataFrame([data_points], columns=parameters)
                updated_df = pd.concat([existing_df, new_data], ignore_index=True)
                updated_df.to_excel(excel_file, index=False)
            except FileNotFoundError:
                new_data = pd.DataFrame([data_points], columns=parameters)
                new_data.to_excel(excel_file, index=False)
    
                        
                    



trader = Trader()
trader.backtest(df)
trader.stats()


