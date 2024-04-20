import threading
import time
import json
from datetime import datetime,timedelta
import schedule
import logging
import concurrent.futures
import os
from Strategy_Builder.Stretegys import strategy_1, strategy_2
from Fyers import Fyers

fyers_obj = Fyers()
fyers_obj.authentication()

def Time_set_for_next_day(market_status):
    schedule.clear()
    schedule.every().day.at("09:15").do(start_algo)
    print(f"Market Status is : {market_status}")


def store_strategy_statuses():   
    print("Updating strategy statuses...")
    Symbol = ["NSE:NIFTY50-INDEX", "NSE:NIFTYBANK-INDEX"]
    TimeFrame = "15"
    results = {}

    def find_entries(index_data):
        print("index_data:", index_data)
        try:
            data = fyers_obj.Historical_Data(index_data[0], TimeFrame)
            strategy_1_status = strategy_1(data, index_data[1])
            strategy_2_status = strategy_2(data, index_data[1])
            return index_data[0], {
                "strategy_1_status": strategy_1_status,
                "strategy_2_status": strategy_2_status,
                "updated_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            print("Error occurred while processing: %s", e)
            return None

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for result in executor.map(find_entries, zip(Symbol, fyers_obj.get_current_ltp(",".join(Symbol)).values())):
            if result:
                results[result[0]] = result[1]

    with open(f"{os.getcwd()}/Records/strategies_results.json", "w") as f:
        json.dump(results, f)

def start_algo():
    current_time = datetime.now().time()
    market_status = fyers_obj.MarketStatus()
    if datetime.strptime("9:15", "%H:%M").time() <= current_time <= datetime.strptime("15:15", "%H:%M").time() and market_status == "OPEN":
        print("Algorithm is Online")
        schedule.every(1).minutes.do(lambda: Time_set_for_next_day() if current_time > datetime.strptime("15:15", "%H:%M").time() else store_strategy_statuses())
    else:
        Time_set_for_next_day(market_status)


def StrategyExecution():
    start_algo()
    while True:
        schedule.run_pending()
        time.sleep(1)

