
from pymongo import MongoClient
import concurrent.futures

from dotenv import load_dotenv
import os
load_dotenv()

client = MongoClient(os.getenv("MONGODB_STRING"))
db = client['TredBuddy']
db_positions = db['Positions']

def Exit_sl_tg(option_data, live_data,fyers):
            symbol_name = option_data['OPTION SYMBOL'][4:]
            option_live_price = live_data.get(symbol_name) 
            option_side = option_data.get("SIDE")

            if option_data['TARGET PRICE'] <= option_live_price:
                fyers.Modify_order(execution_id = option_data.get("EXECUTION ID"),current_price=option_live_price)
                
            elif option_data['SL PRICE'] >= option_live_price:
                fyers.Sell_order(execution_id = option_data.get("EXECUTION ID"),sell_price=option_live_price)
            
def TredExit(fyers):
    row_data = [document for document in db_positions.find({"STATUS" : "OPEN"})]
    live_data_symbols =  ",".join({item['OPTION SYMBOL'] for item in row_data})
    if live_data_symbols != "":
        live_data = fyers.get_current_ltp(live_data_symbols)
        live_data_options = tuple(live_data.items())
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for i in row_data:
                executor.submit(Exit_sl_tg, i, dict(live_data_options),fyers)




    



