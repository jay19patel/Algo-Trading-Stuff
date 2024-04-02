from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()


client = MongoClient(os.getenv("MONGODB_STRING"))

db = client['TradBuddy_V2_Worker_1']

dbProfile = db['Profile']


dbProfile.insert_one({
    "AccountID": "000001",
    "Name" : "Jay Patel",
    "Balance" : 10000,
    "AlgoStatus":False,
    "IndexList" :[],


    
    })

