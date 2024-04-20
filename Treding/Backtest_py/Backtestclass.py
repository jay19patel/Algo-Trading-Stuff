
import pandas as pd
from datetime import datetime
import time
from tabulate import tabulate
import concurrent.futures

class StockTrader:
    def __init__(self, initial_balance=100000 ,sl_points = 20 , target_points = 40):
        self.balance = initial_balance
        self.stock_quantity = 0
        self.stock_price = 0
        self.last_generated_id = int(time.time())
        self.sl_points = sl_points
        self.target_points = target_points
        self.exit_reason = 'Manual'
        columns = ['Symbol', 'Side','Status', 'BuyID', 'Quantity', 'BuyPrice', 'BuyDatetime', 'SellDatetime',
                   'PendingQuantity', 'AverageSellPrice', 'PnL', 'SLValue', 'TargetValue', 'ExitReason']
        self.logs = pd.DataFrame(columns=columns)
    def generate_id(self):
        unique_id = self.last_generated_id
        self.last_generated_id += 1
        return unique_id

    def buy_stock(self, quantity, price, datetime, symbol,side,strategy_name):
        buy_id = self.generate_id()
        self.strategy_name= strategy_name
        buy_datetime = datetime
        self.stock_quantity += quantity
        self.stock_price = price

        if side == "CE":
            self.stoploss = price - self.sl_points
            self.target = price + self.target_points
        elif side == "PE":
            self.stoploss = price + self.sl_points
            self.target = price - self.target_points
        else:
            print("SOMETHING WRONG IS SIDE SELECTION")

        new_log = pd.DataFrame({'Symbol': [symbol],'Side':[side] ,'BuyID': [buy_id], 'Quantity': [quantity], 'BuyPrice': [price],
                                'BuyDatetime': [buy_datetime], 'SellDatetime': [[]], 'PendingQuantity': [quantity],
                                'AverageSellPrice': [0], 'PnL': [0], 'Status': ['Open'],
                                'SLValue': [self.stoploss], 'TargetValue': [self.target], 'ExitReason': [self.exit_reason] ,'StategyName':[strategy_name]})
        self.logs = pd.concat([self.logs, new_log], ignore_index=True)
        return buy_id

    def sell_stock(self, buy_id, quantity, sell_price, datetime, exit_reason='Manual'):
        buy_row = self.logs[self.logs['BuyID'] == buy_id]
        if buy_row.empty:
            return "Buy ID not found."
            
        # sell_datetime = datetime.strptime(date, '%Y-%m-%d')
        sell_datetime = datetime
        tred_side = buy_row['Side'].iloc[0]
        if tred_side == "CE":
            pnl = quantity * (sell_price - buy_row['BuyPrice'].values[0])
            # print("pnl",pnl)

        else:
            pnl = quantity * (buy_row['BuyPrice'].values[0] - sell_price)
            # print("pnl",pnl)
 
            
        # Update the log entry with the sell transaction
        self.balance += pnl
        buy_index = buy_row.index[0]
        self.logs.at[buy_index, 'SellDatetime'] = sell_datetime

        # Update pending quantity, average sell price, and cumulative PnL
        self.logs.at[buy_index, 'PendingQuantity'] -= quantity
        self.logs.at[buy_index, 'SellPrice'] = sell_price
        self.logs.at[buy_index, 'PnL'] += pnl

        # If all quantity sold, update the status to 'Done'
        if self.logs.at[buy_index, 'PendingQuantity'] == 0:
            self.logs.at[buy_index, 'Status'] = 'Done'

        # Set exit reason and update SLValue and TargetValue
        self.exit_reason = exit_reason
        self.logs.at[buy_index, 'SLValue'] = self.stoploss
        self.logs.at[buy_index, 'TargetValue'] = self.target
        self.logs.at[buy_index, 'ExitReason'] = exit_reason

        return f"Stock sold successfully. PnL: {pnl}"

        
   
    def auto_exit(self, current_price,datetime):
        for buy_index, row in self.logs.iterrows():
            if row['Status'] == 'Open':
                qnty = row['PendingQuantity']
                if qnty != 0:
                    if row['Side'] == "CE":
                        if current_price >= row['TargetValue']:
                            exit_reason = 'Target Hit'
                            buy_id = row['BuyID']
                            # Trailing ----------------------
                            # self.logs.at[buy_index, 'SLValue'] = current_price - 20
                            # self.logs.at[buy_index, 'TargetValue'] = current_price + 20
                            # return
                            # Trailing ----------------------

                            return self.sell_stock(buy_id=buy_id, quantity=qnty, sell_price=current_price, datetime=datetime, exit_reason=exit_reason)
                        elif current_price <= row['SLValue']:
                            exit_reason = 'SL Hit'
                            buy_id = row['BuyID']
                            return self.sell_stock(buy_id=buy_id, quantity=qnty, sell_price=current_price, datetime=datetime, exit_reason=exit_reason)
                    elif row['Side'] == "PE":
                        if current_price <= row['TargetValue']:
                            exit_reason = 'Target Hit'
                            buy_id = row['BuyID']
                            # Trailing ----------------------
                            # self.logs.at[buy_index, 'SLValue'] = current_price + 20
                            # self.logs.at[buy_index, 'TargetValue'] = current_price - 20
                            # continue
                            # Trailing ----------------------

                            return self.sell_stock(buy_id=buy_id, quantity=qnty, sell_price=current_price, datetime=datetime, exit_reason=exit_reason)
                        elif current_price >= row['SLValue']:
                            exit_reason = 'SL Hit'
                            buy_id = row['BuyID']
                            return self.sell_stock(buy_id=buy_id, quantity=qnty, sell_price=current_price, datetime=datetime, exit_reason=exit_reason)
        return None
    
    
    def stats(self):
        df = self.logs
        total_trade = len(df.index)
        pnl = df.PnL.sum()
        winners = len(df[df.PnL > 0])
        losers = len(df[df.PnL <= 0])
        win_ratio = round((winners / total_trade) * 100, 2)

        # Calculate CE and PE trades
        ce_trades = f"{(len(df[(df['Side'] == 'CE') & (df['PnL'] > 0)]) / len(df[df['Side'] == 'CE']) * 100):.2f}%"
        pe_trades = f"{(len(df[(df['Side'] == 'PE') & (df['PnL'] > 0)]) / len(df[df['Side'] == 'PE']) * 100):.2f}%"


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
                       ce_trades, pe_trades, self.strategy_name]
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
