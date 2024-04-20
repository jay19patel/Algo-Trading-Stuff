import pymongo  
import datetime
import time
import functools
import json
client = pymongo.MongoClient("mongodb+srv://justj:justj@cluster0.fsgzjrl.mongodb.net/")
db =client["TradBuddy_V2_Worker_1"]
account_collection =db["Account"]

Signal_Path = "strategies_results.json"
#  ["NSE:NIFTY50-INDEX", "NSE:NIFTYBANK-INDEX", "NSE:FINNIFTY-INDEX", "BSE:SENSEX-INDEX", "BSE:BANKEX-INDEX"]
data = None

def call_on_second_2(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        while True:
            current_time = datetime.datetime.now()
            if current_time.second == 2:
                func(*args, **kwargs)
            time.sleep(1)
    return wrapper

# @call_on_second_2
def Test():
    Active_Accounts = account_collection.find({"is_activate":"Activate"})
    # STATUS FETCH FROM SIGNALS
    with open(Signal_Path, "r") as json_file:
        data = json.load(json_file)

    print("------------",datetime.datetime.now(),"------------")
    for acc in Active_Accounts:
        print("******************")
        print(acc["account_id"])
        for i in acc["trad_indexs"]:
            StrategyStatusIs =  data.get(i).get(acc["strategy"])
            print(StrategyStatusIs)
        print("******************")
    print("done process")

Test()

























