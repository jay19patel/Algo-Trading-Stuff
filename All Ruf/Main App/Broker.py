from concurrent.futures import ThreadPoolExecutor
import pandas as pd
from datetime import datetime
import time
from tabulate import tabulate
import concurrent.futures

class StockTrader:
    def __init__(self, initial_balance=100000):
        self.balance = initial_balance
        self.in_tred = {'CE': None, 'PE': None}
        self.last_generated_id = int(time.time())
        columns = ['Symbol', 'Status', 'Side', 'BuyID', 'Quantity', 'BuyPrice', 'BuyDatetime', 'SellTransactions',
                   'PendingQuantity', 'SLValue', 'SL[%]', 'TargetValue', 'Target[%]', 'AverageSellPrice', 'PnL', 'PnL%', 'ExitReason', 'TrailingCount']
        self.logs = pd.DataFrame(columns=columns)

    def generate_id(self):
        unique_id = self.last_generated_id
        self.last_generated_id += 1
        return unique_id

    def calculate_average_sell_price(self, buy_index):
        sell_transactions = self.logs.at[buy_index, 'SellTransactions']
        if not sell_transactions:
            return 0

        total_sell_price = sum(transaction['Quantity'] * transaction['SellPrice'] for transaction in sell_transactions)
        total_quantity = sum(transaction['Quantity'] for transaction in sell_transactions)

        return total_sell_price / total_quantity

    def Buy(self, quantity, price, datetime, symbol, side):
        if side not in ['CE', 'PE']:
            print("Invalid side. Please provide 'CE' or 'PE'.")
            return None

        # Check if already in trade for the given symbol and side
        if self.in_tred[side] is not None and self.in_tred[side]['symbol'] == symbol:
            # print(f"Already in {side} trade for {symbol}, cannot enter again.")
            return None

        buy_id = self.generate_id()
        buy_datetime = datetime
        if side == "CE":
            stoploss = round(price - 30, 2)
            target = round(price + 80, 2)
        else:
            stoploss = round(price + 30, 2)
            target = round(price - 80, 2)

        stoploss_percentage = round((stoploss / price - 1) * 100, 2)
        target_percentage = round((target / price - 1) * 100, 2)
        self.in_tred[side] = {'symbol': symbol, 'buy_id': buy_id}
        exit_reason = 'Open'
        new_log = pd.DataFrame({'Symbol': [symbol], 'Status': ['Open'], 'Side': [side], 'BuyID': [buy_id], 'Quantity': [quantity],
                                'BuyPrice': [round(price, 2)], 'BuyDatetime': [buy_datetime], 'SellTransactions': [[]],
                                'PendingQuantity': [quantity], 'SLValue': [stoploss], 'SL[%]': [stoploss_percentage],
                                'TargetValue': [target], 'Target[%]': [target_percentage], 'AverageSellPrice': [0],
                                'PnL': [0], 'PnL%': [0], 'ExitReason': [exit_reason], 'TrailingCount': [0]})
        self.logs = pd.concat([self.logs, new_log], ignore_index=True)
        print("BUY", buy_id)
        return buy_id

    def Sell(self, buy_id, quantity, sell_price, datetime, exit_reason):
        buy_row = self.logs[self.logs['BuyID'] == buy_id]
        if buy_row.empty:
            return "Buy ID not found."
        tred_side = buy_row['Side'].values[0]
        self.in_tred[tred_side] = None
        if tred_side == "CE":
            pnl = round(quantity * (sell_price - buy_row['BuyPrice'].values[0]), 2)
        else:
            pnl = round(quantity * (buy_row['BuyPrice'].values[0] - sell_price), 2)

        self.balance += pnl
        buy_index = buy_row.index[0]
        sell_transaction = {'Quantity': quantity, 'SellPrice': round(sell_price, 2), 'SellDatetime': datetime, 'PnL': pnl}
        self.logs.at[buy_index, 'SellTransactions'] = self.logs.at[buy_index, 'SellTransactions'] + [sell_transaction]
        percentage_pnl = round(((sell_price - buy_row['BuyPrice']) / buy_row['BuyPrice']) * 100, 2)
        self.logs.at[buy_index, 'PnL%'] = percentage_pnl.values[0]
        self.logs.at[buy_index, 'PendingQuantity'] -= quantity
        self.logs.at[buy_index, 'AverageSellPrice'] = round(self.calculate_average_sell_price(buy_index), 2)
        self.logs.at[buy_index, 'PnL'] += pnl
        if self.logs.at[buy_index, 'PendingQuantity'] == 0:
            self.logs.at[buy_index, 'Status'] = 'Done'

        self.logs.at[buy_index, 'ExitReason'] = exit_reason

        return f"Stock sold successfully. PnL: {pnl}"

    def Auto_Exit(self, symbol_prices):
        with ThreadPoolExecutor() as executor:
            futures = []
            for symbol_price in symbol_prices:
                futures.append(executor.submit(self._process_auto_exit, symbol_price))
            concurrent.futures.wait(futures)

    def _process_auto_exit(self, symbol_price):
        symbol, current_price = symbol_price['symbol'], round(symbol_price['ltp'], 2)

        # EXIT
        ce_entries_sl = self.logs[(self.logs['Side'] == 'CE') & (self.logs['SLValue'] >= current_price) & (self.logs['Status'] == "Open")]
        pe_entries_sl = self.logs[(self.logs['Side'] == 'PE') & (self.logs['SLValue'] <= current_price) & (self.logs['Status'] == "Open")]
        relevant_entries_ls = pd.concat([ce_entries_sl, pe_entries_sl])
        for sell_index, sell_row in relevant_entries_ls.iterrows():
            print(f"SL HIT at index {sell_index}, Sell Price: {sell_row['Quantity']}")
            self.Sell(buy_id=sell_row['BuyID'], quantity=sell_row['Quantity'], sell_price=current_price, datetime=datetime.now(), exit_reason="SL HIT")


        # Trailing
        ce_entries_tg = self.logs[(self.logs['Side'] == 'CE') & (self.logs['TargetValue'] <= current_price) & (self.logs['Status'] == "Open")]
        pe_entries_tg = self.logs[(self.logs['Side'] == 'PE') & (self.logs['TargetValue'] >= current_price) & (self.logs['Status'] == "Open")]
        relevant_entries_tg = pd.concat([ce_entries_tg, pe_entries_tg])
        for buy_index, buy_row in relevant_entries_tg.iterrows():
            if buy_row['Side'] == "CE" and current_price > buy_row['TargetValue']:
                new_sl = round(current_price - 15,2)
                new_target = round(current_price + 20,2)
                self.logs.at[buy_index, 'SLValue'] = new_sl
                self.logs.at[buy_index, 'SL[%]'] = round((new_sl / current_price - 1) * 100, 2)
                self.logs.at[buy_index, 'TargetValue'] = new_target
                self.logs.at[buy_index, 'Target[%]'] = round((new_target / current_price - 1) * 100, 2)
                percentage_gain = round(((current_price - buy_row['BuyPrice']) / buy_row['BuyPrice']) * 100, 2)
                self.logs.at[buy_index, 'PnL%'] = percentage_gain
                self.logs.at[buy_index, 'TrailingCount'] += 1
                print(f"TRED ID [{buy_row['BuyID']}] STATUS [TRAIL TARGET] NEW TARGET [{new_target}] NEW SL [{new_sl}] GAIN [{percentage_gain}]")

            if buy_row['Side'] == "CE" and current_price >= buy_row['BuyPrice'] * 3:
                self.Sell(buy_id=buy_row['BuyID'], quantity=buy_row['Quantity'], sell_price=round(current_price, 2), datetime=datetime.now(), exit_reason="TRAILING HIT")
                print("EXIT TRAIL TARGET DONE")

    def stats(self):
        df = self.logs
        total_trade = len(df.index)
        pnl = round(df.PnL.sum(), 2)
        winners = len(df[df.PnL > 0])
        losers = len(df[df.PnL <= 0])
        win_ratio = round((winners / total_trade) * 100, 2)

        # Calculate additional metrics
        capital = round(self.balance, 2)
        max_win = round(df[df.PnL > 0].PnL.max(), 2)
        max_loss = round(df[df.PnL <= 0].PnL.min(), 2)
        total_profit = round(df.PnL.sum(), 2)
        total_profit_percentage = round((total_profit / self.balance) * 100, 2)

        # Prepare the data for tabular representation
        parameters = ['Total Trades', 'Capital', 'Total Wins', 'Total Losses', 'Win Ratio',
                      'Max Win', 'Max Loss', 'Total P&L', ' Grow P&L %']
        data_points = [total_trade, capital, winners, losers, f"{win_ratio}%",
                       max_win, max_loss, total_profit, f"{total_profit_percentage}%"]
        data = list(zip(parameters, data_points))

        # Print the tabular representation
        print(tabulate(data, headers=['Parameters', 'Values'], tablefmt='psql'))

