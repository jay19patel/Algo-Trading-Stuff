import schedule
import time
from Fyers import Fyers
from Entry import find_treds
from Exit import Auto_exit

def start_mylogic(fyers):
    print(f'--------------------------------[ {time.strftime("%H:%M:%S")} ]--------------------------------')
    find_treds(fyers)
    Auto_exit(fyers)

def Live(fyers):
    current_time = time.localtime()
    hour = current_time.tm_hour
    minute = current_time.tm_min
    
    # Run job only between 9:15 AM and 3:30 PM
    # if (hour == 9 and minute >= 15) or (hour > 9 and hour < 16) or (hour == 15 and minute <= 15):
    if (hour == 0 and minute >= 15) or (hour > 0 and hour < 24) or (hour == 24 and minute <= 15):
        second = int(time.strftime("%S"))  
        if second == 1 or second == 33:
            print("[ ONLINE ]")
            start_mylogic(fyers)
    else:
        print(f'--------------------------------[ ALGO CLOSE : {time.strftime("%H:%M:%S")} ]--------------------------------')
        # Cancel the job once the market is closed
        schedule.clear()
        schedule.every().day.at("09:15").do(Main)

def Main():
    print("FYER LOGIN")
    fyers = Fyers()
    fyers.authentication()
    print("----------[FYER LOGIN.....]----------")
    schedule.every().second.do(Live,fyers=fyers)

from datetime import datetime

now = datetime.now()
# if 9 <= now.hour < 24:
if 0 <= now.hour < 24:
    Main()
else:
    print(f'--------------------------------[ ALGO CLOSE : {time.strftime("%H:%M:%S")} ]--------------------------------')
    schedule.every().day.at("09:15").do(Main)

while True:
    schedule.run_pending()
    time.sleep(1)
