import pymongo 
from db import DbEstabilation 
from middelware import check_authentication,create_uuid,tbCurrentTimestamp
import datetime



local_storage = {}

class TradBuddyBroker:
    disc = "Trad Buddy Broker For Real/ Paper Money"
    
    def __init__(self):
        self.TradBuddyDb= DbEstabilation()
        self.isAuthenticated = False


    def create_profile(self):

        profile_id =  f"PROF-{str(self.TradBuddyDb.profileCollection.countDocument() +1).zfill(3)}" 

        profileSchema = {
            "name":"Jay Patel",
            "profile_id" : profile_id,
            "profile_password":"SuperAdmin",
            "account_list":[],
            "algo_status":False # Algo Start chhe ke ni te check karva 
        }

        self.TradBuddyDb.profileCollection.insert_one(profileSchema)
        print("Profile created successfully.")
        
    def authentication(self):
        data = self.TradBuddyDb.profileCollection.find_one({"profile_id":"P-001","profile_password":"SuperAdmin"})
        if data :
            self.isAuthenticated = True
            del data["_id"]
            local_storage["name"] = data.get("name")
            local_storage["profile_id"] = data.get("name")
            print(data)


    # ---------------ACCOUNT----------------
    @check_authentication
    def create_account(self):
        account_id =  f"ACC-{str(self.TradBuddyDb.testCollection.countDocument() +1).zfill(3)}" 
        accountSchema = {
            "profile_id":local_storage.get("profile_id")
            "account_id" = account_id
            "account_balance":float(0),
            "is_activate": True , 
            "trad_indexs": [], 
            "strategy":"",
            "max_trad_per_day":10, 
            "todays_margin":float(0), 
            "todays_trad_margin":float(0),
            "account_min_profile":float(0),
            "account_max_loss":float(0),  
            "base_stoploss": float(0),
            "base_target": float(0),
            "trailing_status":True , 
            "trailing_stoploss":float(0),
            "trailing_target":float(0),
            "payment_status":"Paper Trad" ,
            "last_updated_datetime":tbCurrentTimestamp() 
        }
        account_data = self.TradBuddyDb.testCollection.insert_one(accountSchema)


    # ---------------ACCOUNT TRANSECTION----------------
    def account_transection(transaction_type, amount, profile_id, account_id):
        trans_data = self.TradBuddyDb.testCollection.find_one(
            {"profile_id": profile_id, "account_id": account_id})

        if trans_data:
            if transaction_type == "deposit":
                self.TradBuddyDb.testCollection.update_one(
                    {"_id": trans_data["_id"]},
                    {"$inc": {"amount": amount}})
                print(f"{amount} is deposited in account: {account_id} for profile: {profile_id}")

            elif transaction_type == "withdraw":
                if trans_data["amount"] >= amount:
                    self.TradBuddyDb.testCollection.update_one(
                        {"_id": trans_data["_id"]},
                        {"$inc": {"amount": -amount}})
                    print(f"{amount} is withdrawn from account: {account_id} for profile: {profile_id}")
                else:
                    print(f"Insufficient balance in account: {account_id} for profile: {profile_id}")

            else:
                print("Select Proper Transection type.")

            transectionSchema = {
                "transection_id": create_uuid("ACC-TRAN"),
                "profile_id": profile_id,
                "account_id": account_id,
                "type": transaction_type.capitalize(),
                "amount": amount,
                "datetime": tbCurrentTimestamp(),
                "notes": ""
            }
            self.TradBuddyDb.testCollection.insert_one(transectionSchema)
        else:
            print(f"Account not found for profile: {profile_id} and account: {account_id}")


        # -------------------ORDER
        def place_order(self,reciver):

            ischarges = 50.00

            isAccount = ""
            isStrategy = ""
            isType = "Buy"
            isIndex = ""
            isSide = ""
            isTriggerIndex = ""
            isOptionSymbol = ""
            isQnty = ""
            isBuyPrice = ""
            isSellPrice = ""
            isSlPrice = ""
            isTargetPrice = ""
            isBuytimestamp = ""
            isSelltimestamp = ""
            isBuyMargin = ""
            isSellMargin = ""
            isPnlStatus = ""
            isPnl = ""

        
            
            orderSchema = {
                "order_id": create_uuid("ORD"),
                "profile_id": local_storage.get("profile_id"),
                "account_id": isAccount,
                "strategy": isStrategy,
                "date": tbCurrentTimestamp().strftime("%d-%m-%Y"),
                "trad_status": "Open",
                "trad_type": isType,
                "trad_index": isIndex,
                "trad_side": isSide,
                "trigger_index": isTriggerIndex,
                "option_symbol": isOptionSymbol,
                "qnty": isQnty,
                "buy_price": isBuyPrice,
                "sell_price": isSellPrice,
                "stoploss_price": isSlPrice,
                "target_price": isTargetPrice,
                "buy_datetime": isBuytimestamp,
                "sell_datetime": isSelltimestamp,
                "buy_margin":isBuyMargin,
                "sell_margin":isSellMargin,
                "pnl_status": isPnlStatus,
                "pnl": isPnl
            }

            self.TradBuddyDb.testCollection(orderSchema)
            




obj = TradBuddyBroker()
# obj.authentication()
# obj.create_account()




