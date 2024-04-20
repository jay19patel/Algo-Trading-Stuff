# import pandas as pd 


# # --------------------[Custom Imports]------------------------
# from DB.Connection import DBConnection_for_Broker
# from Utility.Generator import create_uuid,tbCurrentTimestamp


# class TradBuddyBroker:
#     def __init__(self):
#         self.profile_collection, self.transactions_collection, self.account_collection, self.notifications_collection, self.orders_collection, self.mongo_connection = DBConnection_for_Broker()
#         self.isAuthenticated = False
        

#     # Middelware
#     def check_authentication(func):
#         def wrapper(self, *args, **kwargs):
#             if not self.isAuthenticated:
#                 print(f"Authentication required for {func.__name__} ")
#                 print("Use: profile_create() or profile_login() for Authentication.")
#             else:
#                 return func(self, *args, **kwargs)
#         return wrapper
    

#     def profile_create(self,**data):
#         try:
#             profile_id = f"PROF-{str(self.profile_collection.count_documents({}) +1).zfill(3)}"
#             profileSchema = {
#                 "username": data.get("username"),
#                 "profile_id": profile_id,
#                 "profile_password": data.get("password"),
#                 "fyers_user_id":data.get("fyers_user_id"),
#                 "fyers_mobile_no":data.get("fyers_mobile_no"),
#                 "fyers_client_id":data.get("fyers_client_id"),
#                 "fyers_secret_key":data.get("fyers_secret_key"),
#                 "fyers_app_pin":data.get("fyers_app_pin"),
#                 "fyers_totp_key":data.get("fyers_totp_key"),
#                 "account_list": [],
#                 "algo_status": False
#             }
#             self.profile_collection.insert_one(profileSchema)
#             print(f"profile_create [{profile_id}]: success - Profile created successfully.")
#         except Exception as e:
#             print(f"profile_create: fail - Failed to create profile: {e}")

#     def profile_login(self, profile_id, profile_password):
#         try:
#             data = self.profile_collection.find_one({"profile_id": profile_id, "profile_password": profile_password})
#             if data:
#                 self.isAuthenticated = True
#                 self.username = data.get("name")
#                 self.profile_id = profile_id
#                 print(f"profile_login: success - Authentication successful for user: {self.username}")
#             else:
#                 print("profile_login: fail - Authentication failed: Incorrect profile ID or password")
#         except Exception as e:
#             print(f"profile_login: fail - Failed to login: {e}")

#     @check_authentication
#     def profile_get(self):
#         try:
#             data = self.profile_collection.find_one({"profile_id": self.profile_id})
#             del data["_id"]
#             print(data)
#         except Exception as e:
#             print(f"profile_get: fail - Failed to get profile: {e}")

#     @check_authentication
#     def account_create(self):
#         try:
#             account_id = f"ACC-{str(self.account_collection.count_documents({}) + 1).zfill(3)}"
#             accountSchema = {
#                 "profile_id": self.profile_id,
#                 "account_id": account_id,
#                 "account_balance": float(0),
#                 "is_activate": True,
#                 "trad_indexs": [],
#                 "strategy": None,
#                 "max_trad_per_day": 10,
#                 "todays_margin": float(0),
#                 "todays_trad_margin": float(0),
#                 "account_min_profile": float(0),
#                 "account_max_loss": float(0),
#                 "base_stoploss": float(0),
#                 "base_target": float(0),
#                 "trailing_status": True,
#                 "trailing_stoploss": float(0),
#                 "trailing_target": float(0),
#                 "payment_status": "Paper Trad",
#                 "last_updated_datetime": tbCurrentTimestamp()
#             }
#             self.account_collection.insert_one(accountSchema)
#             print(f"account_create [{account_id}]: success - Account created successfully.")
#         except Exception as e:
#             print(f"account_create: fail - Failed to create account: {e}")

#     @check_authentication
#     def account_update(self, account_id, update_data):
#         try:
#             result = self.account_collection.update_one({"account_id": account_id}, {"$set": update_data})
#             if result.modified_count:
#                 print(f"account_update [{account_id}]: success - Account updated successfully.")
#             else:
#                 print("account_update: fail - No matching account found for update.")
#         except Exception as e:
#             print(f"account_update: fail - Failed to update account: {e}")

#     @check_authentication
#     def account_get(self, account_id):
#         try:
#             result = self.account_collection.find_one({"account_id": account_id})
#             del result["_id"]
#             print(result)
#         except Exception as e:
#             print(f"account_get [{account_id}]: fail - Failed to get account: {e}")

#     @check_authentication
#     def account_delete(self, account_id):
#         try:
#             result = self.account_collection.delete_one({"account_id": account_id})
#             if result.deleted_count:
#                 print(f"account_delete [{account_id}]: success - Account deleted successfully.")
#             else:
#                 print("account_delete: fail - No matching account found for deletion.")
#         except Exception as e:
#             print(f"account_delete: fail - Failed to delete account: {e}")

#     @check_authentication
#     def account_transaction(self, transaction_type, amount, account_id,notes=""):
#         try:
#             account_data = self.account_collection.find_one({"profile_id": self.profile_id, "account_id": account_id})
#             if not account_data:
#                 print(f"account_transaction: fail - Account not found for profile: {self.profile_id} and account: {account_id}")
#                 return False

#             if transaction_type == "deposit":
#                 self.account_collection.update_one({"_id": account_data["_id"]}, {"$inc": {"account_balance": amount}})
#                 print(f"account_transaction: success - {amount} is deposited in account: {account_id} for profile: {self.profile_id}")

#             elif transaction_type == "withdraw":
#                 if account_data["account_balance"] >= amount:
#                     self.account_collection.update_one({"_id": account_data["_id"]}, {"$inc": {"account_balance": -amount}})
#                     print(f"account_transaction: success - {amount} is withdrawn from account: {account_id} for profile: {self.profile_id}")
#                 else:
#                     print(f"account_transaction: fail - Insufficient balance in account: {account_id} for profile: {self.profile_id}")
#             else:
#                 print("account_transaction: fail - Select proper transaction type.")
#                 return False

#             # Create transaction ID
#             transaction_id = create_uuid("ACC-TRAN")
#             transaction_schema = {
#                 "transaction_id": transaction_id,
#                 "profile_id": self.profile_id,
#                 "account_id": account_id,
#                 "type": transaction_type.capitalize(),
#                 "amount": amount,
#                 "datetime": tbCurrentTimestamp(),
#                 "notes": notes
#             }
#             # Insert transaction data into the collection
#             self.transactions_collection.insert_one(transaction_schema)
#             print(f"account_transaction: success - Account transaction successful, Transaction ID: {transaction_id}")
#             return True

#         except Exception as e:
#             print(f"account_transaction: fail - Failed to perform account transaction: {e}")
#             return False

#     @check_authentication
#     def order_place(self, **data):
#         try:
#             order_id = create_uuid("ORD")
#             isBuyMargin = data.get("buyprice") * data.get("qnty")
#             order_schema = {
#                 "order_id": order_id,
#                 "profile_id": self.profile_id,
#                 "account_id": data.get("account_id"),
#                 "strategy": data.get("strategy"),
#                 "date": tbCurrentTimestamp().strftime("%d-%m-%Y"),
#                 "trad_status": "Open",
#                 "trad_type": data.get("type", "Buy"),
#                 "trad_index": data.get("trad_index"),
#                 "trad_side": data.get("side"),
#                 "trigger_index": data.get("trigger_index"),
#                 "option_symbol": data.get("symbol"),
#                 "qnty": data.get("qnty"),
#                 "buy_price": data.get("buyprice"),
#                 "sell_price": None,
#                 "stoploss_price": data.get("sl_price"),
#                 "target_price": data.get("target_price"),
#                 "buy_datetime": tbCurrentTimestamp(),
#                 "sell_datetime": None,
#                 "buy_margin": isBuyMargin,
#                 "sell_margin": None,
#                 "pnl_status": None,
#                 "pnl": None,
#                 "notes":data.get("notes")
#             }
#             account = self.account_collection.find_one({"account_id": data["account_id"]})
#             if not account:
#                 print(f"order_place: fail - Failed to place order: Account not found.")
#                 return

#             if account.get("account_balance", 0) < isBuyMargin:
#                 print(f"order_place: fail - Failed to place order: Insufficient balance in the Account ID: {data['account_id']} Require Balance is More then {isBuyMargin}")
#                 return

#             self.orders_collection.insert_one(order_schema)
#             self.account_collection.update_one({"account_id": data["account_id"]}, {"$inc": {"account_balance": -isBuyMargin}})
#             print(f"order_place [{order_id}]: success - Order placed successfully.")
#             return order_id

#         except Exception as e:
#             print(f"order_place: fail - Failed to place order: {e}")

#     @check_authentication
#     def order_close(self, account_id, order_id, sell_price):
#         try:
#             order = self.orders_collection.find_one({"order_id": order_id, "account_id": account_id})
#             if order and sell_price:
#                 isSellMargin = float(order.get("qnty") * sell_price)
#                 isPnl = isSellMargin - order.get("buy_margin")
#                 update_data = {
#                     "trad_status": "Close",
#                     "sell_price": sell_price,
#                     "sell_datetime": tbCurrentTimestamp(),
#                     "sell_margin": isSellMargin,
#                     "pnl_status": "Profit" if isPnl >= 1 else "Loss",
#                     "pnl": isPnl
#                 }
#                 result_order = self.orders_collection.update_one({"order_id": order_id, "account_id": account_id}, {"$set": update_data})
#                 result_account = self.account_collection.update_one({"account_id": account_id}, {"$inc": {"account_balance": isSellMargin}})

#                 if result_order.modified_count > 0 and result_account.modified_count > 0:
#                     print(f"order_close [{order_id}]: success - Order closed successfully with PNL: {isPnl}")
#                 else:
#                     print("order_close: fail - Failed to close the order.")
#             else:
#                 print("order_close: fail - Something wrong in Order Close")
#         except Exception as e:
#             print(f"order_close: fail - Failed to close the order: {e}")

#     @check_authentication
#     def order_book(self, account_id):
#         try:
#             order_book = self.orders_collection.find_one({"account_id": account_id})
#             del order_book["_id"]
#             print(order_book)
#         except Exception as e:
#             print(f"order_book: fail - Failed to get order book: {e}")

#     @check_authentication
#     def generate_report(self,account_id):
#         try:
#             order_book = self.orders_collection.find({"account_id": account_id,"trad_status":"Close"})
#             if order_book:
#                 df = pd.DataFrame(order_book)
#                 count_df_group = df.groupby(['trad_index', 'trad_side', 'pnl_status']).size().reset_index(name='Total Trades')
#                 count_df = count_df_group.pivot_table(index='trad_index', columns=['trad_side', 'pnl_status'], values='Total Trades', aggfunc='sum', fill_value=0)
#                 count_df.columns = ['_'.join(col) for col in count_df.columns.values]
#                 count_df['Total_Tred'] = count_df.sum(axis=1)
#                 count_df.reset_index(inplace=True)

#                 amount_df_group = df.groupby(['trad_index', 'trad_side', 'pnl_status'])['pnl'].sum().reset_index(name='Total PnL Grow')
#                 amount_df = amount_df_group.pivot_table(index='trad_index', columns=['trad_side', 'pnl_status'], values='Total PnL Grow', aggfunc='sum', fill_value=0)
#                 amount_df.columns = ['_Amount_'.join(col) for col in amount_df.columns.values]
#                 amount_df['Total_Tred_Amount'] = amount_df.sum(axis=1)

#                 merged_df = pd.merge(count_df, amount_df, on='trad_index', how='outer').fillna(0)
#                 columns_to_add = ['CE_Loss', 'PE_Loss', 'PE_Profit', 'CE_Profit', 'CE_Amount_Loss', 'PE_Amount_Loss', 'PE_Amount_Profit', 'CE_Amount_Profit']
#                 merged_df = merged_df.reindex(columns=merged_df.columns.union(columns_to_add), fill_value=0)
#                 merged_df['Total_Tred'] = merged_df[['CE_Loss', 'PE_Loss', 'PE_Profit', 'CE_Profit']].sum(axis=1)
#                 merged_df['Total_Tred_Amount'] = merged_df[['CE_Amount_Loss', 'PE_Amount_Loss', 'PE_Amount_Profit', 'CE_Amount_Profit']].sum(axis=1)

#                 total_row = merged_df.sum(numeric_only=True)
#                 total_row['trad_index'] = 'Over All'
#                 total_df = pd.DataFrame([total_row])
#                 output = pd.concat([merged_df, total_df], ignore_index=True).to_dict('records')
#                 print(output)
#                 return output
#             else:
#                 print(f"generate_report: fail - Order book have no values.")
#         except Exception as e:
#             print(f"generate_report: fail - Failed to generate report: {e}")
    
#     @check_authentication
#     def perform_analysis(self,account_id): # Daily data analysis
#         try:
#             order_book = self.orders_collection.find({"account_id": account_id})
#             alldf = pd.DataFrame(order_book)
#             total_trades = alldf.shape[0]
#             total_open_list = alldf[alldf["trad_status"] == "Open"]
#             total_close_list = alldf[alldf["trad_status"] == "Close"]
#             profitable_trades = len(total_close_list[total_close_list['pnl_status'] == 'Profit'])
#             loss_trades = len(total_close_list[total_close_list['pnl_status'] == 'Loss'])
#             win_ratio = (profitable_trades / total_trades) * 100
#             today_grow = total_close_list["pnl"].sum()
#             total_open, total_close = total_open_list.shape[0], total_close_list.shape[0]

#             responsedata =  {
#                 "total_trades": total_trades,
#                 "total_open_trades": total_open,
#                 "total_close_trades": total_close,
#                 "profitable_trades": profitable_trades,
#                 "loss_trades": loss_trades,
#                 "win_ratio": win_ratio,
#                 "pnl_growth": today_grow
#             }
#             print(responsedata)
        
#         except Exception as e:
#             print(f"perform_analysis: fail - Error in performing analysis:{e}")
#             return None

#     def notification(self, **message):
#         try:
#             self.notifications_collection.insert_one({"Header": message.get("Header"), "Message": message.get("Message"), "Time": tbCurrentTimestamp()})
#             print("notification: success - Notification sent successfully.")
#         except Exception as e:
#             print(f"notification: fail - Failed to send notification: {e}")