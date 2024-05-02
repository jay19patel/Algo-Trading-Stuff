from dotenv import load_dotenv
import os
from pymongo import MongoClient
from datetime import datetime, date
load_dotenv()

client = MongoClient("mongodb+srv://justj:justj@cluster0.fsgzjrl.mongodb.net/")
db = client['TredBuddy']
db_profile = db["Profile"]

db_profile.insert_one(
    {"Account":"001",
        "Name":"Jay Patel",
        "Balance":100000,
        "Alogo Status":False,
     })

# print(date.today())