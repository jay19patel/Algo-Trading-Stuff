import schedule
import time
from Fyers import Fyers
from PDT import Trigger_pdt,target_trailing

def start_mylogic(fyers):
    print(f'--------------------------------[ {time.strftime("%H:%M:%S")} ]--------------------------------')
    Trigger_pdt(fyers)
    target_trailing(fyers)


def Todays_status():
    print("-----------TREDING END--------------")


def Live(fyers):
    current_time = time.localtime()
    hour = current_time.tm_hour
    minute = current_time.tm_min
    
    # Run job only between 9:15 AM and 3:30 PM
    if (hour == 9 and minute >= 15) or (hour > 9 and hour < 24) or (hour == 24 and minute <= 15):
        second = int(time.strftime("%S"))  
        if second == 1 or second == 33:
            print("[ ONLINE ]")
            start_mylogic(fyers)
    else:
        print([' MARKET CLOSE '])
        schedule.clear()
        
        
def Main():
    fyers = Fyers()
    fyers.authentication()
    print("FYER LOGIN")
    schedule.every().second.do(Live,fyers=fyers)
    


from datetime import datetime

now = datetime.now()
if 9 <= now.hour < 24:
    Main()
else:
    print("[ OFFLINE ]")
    schedule.every().day.at("10:10").do(Main)

schedule.every().day.at("15:40").do(Todays_status)

while True:
    schedule.run_pending()
    time.sleep(1)





