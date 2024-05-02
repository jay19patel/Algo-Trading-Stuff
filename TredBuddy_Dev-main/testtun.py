import schedule
import time
from utility import Fyers

from Manager import TredEntry,TredExit
from datetime import datetime, timedelta,date
from utility import TredBuddy_Helper
import logging


from pymongo import MongoClient
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
    second = int(time.strftime("%S"))  
    if (second == 2 or second == 32):
        Messages(f'--------------------------------[ {time.strftime("%H:%M:%S")} ]--------------------------------')
        TredEntry.TredEntry(fyers)
        TredExit.TredExit(fyers)


from Dashbord.Analysis import analysis
def DailyStatusManager():
    today_str = str(date.today())
    data = analysis.DayAnalysis("DAY")
    capital = db_profile.find_one({"Account": "001"}).get("Balance")
    db_daily.update_one({"Date": today_str},{"$set": {"Info": data["AllTred"],"Capital":capital}}, upsert=True)
    Messages(f"Todays Status Update :{today_str} {capital}")
# def Main():
#     Messages("FYER LOGIN")
#     fyers = Fyers.Fyers()
#     fyers.authentication()
#     schedule.every().second.do(Live,fyers=fyers)
# Main()
# while True:
#     schedule.run_pending()
#     time.sleep(1)


DailyStatusManager()