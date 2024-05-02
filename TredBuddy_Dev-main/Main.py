import schedule
import time
from utility import Fyers

from Manager import TredEntry,TredExit
from datetime import datetime, timedelta
from utility import TredBuddy_Helper
import logging

from pymongo import MongoClient
from datetime import datetime, date

from Dashbord.Analysis import analysis


client = MongoClient("mongodb+srv://justj:justj@cluster0.fsgzjrl.mongodb.net/")
db = client['TredBuddy']
db_profile = db["Profile"]
db_daily = db["DayilyStatus"]

logging.basicConfig(filename='trading.log', level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

def Messages(message):
    print(message)
    logging.info(message)

def Live(fyers):
    current_time = time.localtime()
    hour = current_time.tm_hour
    minute = current_time.tm_min
    
    # Run job only between 9:15 AM and 3:30 PM
    if (hour == 9 and minute >= 15) or (hour > 9 and hour < 16) or (hour == 15 and minute <= 15):
        second = int(time.strftime("%S"))  
        if second == 2:
            Messages(f'--------------------------------[ {time.strftime("%H:%M:%S")} ]--------------------------------')
            TredEntry.TredEntry(fyers)
            TredExit.TredExit(fyers)
    else:
        Messages(f'--------------------------------[ ALGO OFF  : {time.strftime("%H:%M:%S")} ]--------------------------------')
        schedule.clear()
        schedule.every().day.at("09:15").do(Main)


def DailyStatusManager():
    today_str = str(date.today())
    data = analysis.DayAnalysis("DAY")
    capital = db_profile.find_one({"Account": "001"}).get("Balance")
    db_daily.update_one({"Date": today_str},{"$set": {"Info": data["AllTred"],"Capital":capital}}, upsert=True)
    Messages(f"Todays Status Update :{today_str} {capital}")


def Main():
    market_status = TredBuddy_Helper.Update_FO()
    # market_status = True
    if market_status:
        Messages("FYER LOGIN")
        fyers = Fyers.Fyers()
        fyers.authentication()
        schedule.every().second.do(Live,fyers=fyers)
        schedule.every().day.at("16:00").do(DailyStatusManager)
    else:
        tomorrow = datetime.now().replace(hour=9, minute=15) + timedelta(days=1)
        Messages(f'--------------------------------[ MARKET OPEN AT : {tomorrow} ]--------------------------------')
        schedule.every().day.at("09:15").do(Main)

from datetime import datetime

now = datetime.now()
current_time = time.localtime()
hour = current_time.tm_hour
minute = current_time.tm_min
# 16 15
if (hour == 9 and minute >= 15) or (hour > 9 and hour < 24) or (hour == 24 and minute <= 15):
    Main()
else:
    Messages(f'--------------------------------[ ALGO CLOSE : {time.strftime("%H:%M:%S")} ]--------------------------------')
    schedule.every().day.at("09:15").do(Main)

while True:
    schedule.run_pending()
    time.sleep(1)
