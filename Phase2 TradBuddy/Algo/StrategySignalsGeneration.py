import threading
import time
import json
from datetime import datetime
import schedule
import logging
from Fyers import Fyers
import concurrent.futures

# Configure logging
logging.basicConfig(filename='Algo.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

USER_ID = "YJ00129"
MOBILE_NO = "7069668308"
CLIENT_ID = "MACO3YJA7I-100"
SECRET_KEY = "N7SXUFQG91"
APP_PIN = "2525"
TOTP_KEY = "XKS2IVVGAINIHYVLM32WOXLFMQUK4DRA"

fyers_obj = Fyers(USER_ID, MOBILE_NO, CLIENT_ID, SECRET_KEY, APP_PIN, TOTP_KEY)
fyers_obj.authentication()

def is_market_open():
    return fyers_obj.MarketStatus() != "CLOSED"

def strategy_1(df, current_price):
    # Placeholder logic for strategy 1
    time.sleep(3)
    return "CE"

def strategy_2(df, current_price):
    # Placeholder logic for strategy 2
    time.sleep(5)
    return "PE"

def store_strategy_statuses():
    logging.info("Updating strategy statuses...")
    Symbol = ["NSE:NIFTY50-INDEX", "NSE:NIFTYBANK-INDEX"]
    TimeFrame = "15"
    results = {}

    def find_entries(index_data):
        try:
            data = fyers_obj.Historical_Data(index_data[0], TimeFrame)
            strategy_1_status = strategy_1(data, index_data[1])
            logging.info("Strategy 1 status for %s: %s", index_data[0], strategy_1_status)
            strategy_2_status = strategy_2(data, index_data[1])
            logging.info("Strategy 2 status for %s: %s", index_data[0], strategy_2_status)
            return index_data[0], {
                "strategy_1_status": strategy_1_status,
                "strategy_2_status": strategy_2_status,
                "updated_datetime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except Exception as e:
            logging.error("Error occurred while processing: %s", e)
            return None

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for result in executor.map(find_entries, zip(Symbol, fyers_obj.get_current_ltp(",".join(Symbol)).values())):
            if result:
                results[result[0]] = result[1]

    with open("strategies_results.json", "w") as f:
        json.dump(results, f)

def start_algorithm(stop_event):
    logging.info("Starting algorithm...")
    while not stop_event.is_set():
        if is_market_open():
            store_strategy_statuses()
        else:
            logging.info("Market is closed. Waiting for it to open.")
        time.sleep(60)

def start_algo():
    current_time = datetime.now().time()
    market_status = fyers_obj.MarketStatus()
    if datetime.strptime("09:15", "%H:%M").time() <= current_time <= datetime.strptime("15:15", "%H:%M").time() and market_status != "CLOSED":
        logging.info("Algorithm is online")
        global stop_event
        stop_event = threading.Event()
        threading.Thread(target=start_algorithm, args=(stop_event,)).start()
    else:
        schedule.clear()
        schedule.every().day.at("09:15").do(start_algo)
        logging.info("Market is %s", market_status)

def stop_algorithm():
    global stop_event
    stop_event.set()
    logging.info("Shutting down algorithm")

if __name__ == '__main__':
    start_algo()
    while True:
        schedule.run_pending()
        time.sleep(1)
