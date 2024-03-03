

from pymongo import MongoClient
import concurrent.futures
from TredBuddy_Helper import Get_Option_info,get_index_info,generate_id
from datetime import datetime , timedelta

from dotenv import load_dotenv

load_dotenv()
import os
# ---------------------- DATABASE CONECTION ------------------
client = MongoClient(os.getenv("MONGODB_STRING"))
db = client['TredBuddy']
db_orders = db['Orders']
db_positions = db['Positions']

def Auto_exit(fyers):
    row_data = [document for document in db_positions.find("STATUS" == "Running")]
    live_data_list = {item['OPTION SYMBOL'] for item in row_data}

    live_data_symbols = ",".join(live_data_list)

    if len(live_data_list) >= 1:
        live_data = fyers.get_current_ltp(live_data_symbols)
        print("[SUCCESS] Auto Exit Check For :",live_data)
        live_data_options = tuple(live_data.items())


        def Condition_check(option_data, live_data):
            symbol_name = option_data['OPTION SYMBOL'][4:]
            option_live_price = live_data.get(symbol_name)  # Get the live price for the option symbol
            option_side = option_data.get("SIDE")

        # ------------------------------- TARGET CHECK ---------------------------------

            if 'TARGET PRICE' in i and i['TARGET PRICE'] <= option_live_price:
                index_sl = 20
                index_tg = 20
                sl_factor, tg_factor = (100 - index_sl, 100 + index_tg) if option_side == "CE" else (100 + index_sl, 100 - index_tg)
                option_ltp_sl = (option_live_price * sl_factor) / 100
                option_ltp_target = (option_live_price * tg_factor) / 100

                filter_criteria = {'EXECUTION ID': i['EXECUTION ID']}
                update_execution = {
                    '$set': {
                        'TARGET PRICE': option_ltp_target,
                        'SL PRICE': option_ltp_sl,
                        'TARILING COUNT': i['TARILING COUNT']+ 1,
                    }
                }
                db_positions.update_one(filter_criteria, update_execution)
                print(f"[{i['OPTION SYMBOL']} : Target Hit]")
                print(" [3] : Updated TARGET PRICE:", option_ltp_target)
                print(" [3] : Updated SL PRICE:", option_ltp_sl,i['TARILING COUNT']+ 1)
                print(" [3] : TARGET TRAILING (UPDATED)")

            # ------------------------------- SL CHECK ---------------------------------
                
            if 'SL PRICE' in i and i['SL PRICE'] >= option_live_price:
                
                filter_criteria = {'EXECUTION ID': i['EXECUTION ID']}
                PNL_GROW = (option_live_price - i['BUY PRICE']) * i['QTY']
                PNL_GROW_PR = PNL_GROW * 100 / (i['BUY PRICE'] * i['QTY'])
                update_execution = {
                    '$set': {
                        'STATUS': "SL Hit",
                        'SELL PRICE': option_live_price,
                        'SELL DATETIME': datetime.now().strftime('%m/%d/%Y %I:%M %p'),
                        'PnL GROW': PNL_GROW,
                        'PnL GROW %': PNL_GROW_PR
                    }
                }
                db_positions.update_one(filter_criteria, update_execution)
                print(f"-----------------[{i['OPTION SYMBOL']} : SL Hit] PNL =[{PNL_GROW}(%{PNL_GROW_PR})]-----------------")

   
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for i in row_data:
                executor.submit(Condition_check, i, dict(live_data_options))





























# from Fyers import Fyers
# fyers = Fyers()
# fyers.authentication()
# Auto_exit(fyers)