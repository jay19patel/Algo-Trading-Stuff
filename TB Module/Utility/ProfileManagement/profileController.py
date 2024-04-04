
from datetime import datetime

ProfileSchema = {
    "name" : "Jay Patel",
    "account_number" : "AC-001",
    "password" : "SuperAdmin",
    "account_balance" : 10000.00,
    "today_margin_amount": 1000,
    "today_trad_margin":1000,
    "algo_status" :  False ,# "Online" | "Offline" ,
    "market_status" : False , #"Online" | "Offline" ,
    "payment_status" : False, # "Real Money" | "Paper Money",
    "created" : datetime.now()
}

from DB.Collections import profile_collection

def get_profile():
    account_number = "AC-001"
    profile = profile_collection.find_one({"account_number":account_number})
    # profile = profile_collection.insert_one(ProfileSchema)
    if profile:
        del profile['_id']
        return profile
    
    return {"body" : "Account Not found !"}
