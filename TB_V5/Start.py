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
    find_treds(fyers)
    Auto_exit(fyers)

def Live(fyers):
    current_time = time.localtime()
    hour = current_time.tm_hour
    minute = current_time.tm_min
    
    # Run job only between 9:15 AM and 3:30 PM
    if (hour == 9 and minute >= 15) or (hour > 9 and hour < 16) or (hour == 15 and minute <= 15):
        second = int(time.strftime("%S"))  
        if second == 2:
            print("[ ONLINE ]")
            start_mylogic(fyers)
    else:
        logging.info(f'--------------------------------[ ALGO CLOSE : {time.strftime("%H:%M:%S")} ]--------------------------------')
        print(f'--------------------------------[ ALGO CLOSE : {time.strftime("%H:%M:%S")} ]--------------------------------')

        schedule.clear()
        schedule.every().day.at("09:15").do(Main)

def Main():
    print("FYER LOGIN")
    fyers = Fyers()
    fyers.authentication()
    logging.info("----------[FYER LOGIN.....]----------")
    schedule.every().second.do(Live,fyers=fyers)

from datetime import datetime

now = datetime.now()
if 9 <= now.hour < 16:
    Main()
else:
    logging.info(f'--------------------------------[ ALGO CLOSE : {time.strftime("%H:%M:%S")} ]--------------------------------')
    print(f'--------------------------------[ ALGO CLOSE : {time.strftime("%H:%M:%S")} ]--------------------------------')
    schedule.every().day.at("09:15").do(Main)

while True:
    schedule.run_pending()
    time.sleep(1)
