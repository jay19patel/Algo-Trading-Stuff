import pymongo  
import datetime
import time
import functools
import json
client = pymongo.MongoClient("mongodb+srv://justj:justj@cluster0.fsgzjrl.mongodb.net/")
db =client["TradBuddy_V2_Worker_1"]
account_collection =db["Account"]

Signal_Path = "data.json"
data = None


def Test():
    Active_Accounts = account_collection.find({"is_activate":"Activate"})
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

























