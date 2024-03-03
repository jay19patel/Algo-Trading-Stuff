import schedule
import time
from Fyers import Fyers
from Entry import find_treds
from Exit import Auto_exit
import logging

logging.basicConfig(filename='trading.log', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def start_mylogic(fyers):
    logging.info(f'--------------------------------[ {time.strftime("%H:%M:%S")} ]--------------------------------')
    print(f'--------------------------------[ {time.strftime("%H:%M:%S")} ]--------------------------------')
    # find_treds(fyers)
    Auto_exit(fyers)

def Live(fyers):
    current_time = time.localtime()
    hour = current_time.tm_hour
    minute = current_time.tm_min
    
    second = int(time.strftime("%S"))  
    if second == 1 or second == 33:
        logging.info("[ ONLINE ]")
        start_mylogic(fyers)

def Main():
    logging.info("FYER LOGIN")
    fyers = Fyers()
    fyers.authentication()
    logging.info("----------[FYER LOGIN.....]----------")
    schedule.every().second.do(Live,fyers=fyers)

from datetime import datetime

Main()

while True:
    schedule.run_pending()
    time.sleep(1)
