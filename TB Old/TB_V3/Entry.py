

from pymongo import MongoClient
import concurrent.futures
from TredBuddy_Helper import Get_Option_info,get_index_info,generate_id
from Stretegy_Helper import Main_Stetegy_execution
from datetime import datetime , timedelta

from dotenv import load_dotenv

load_dotenv()
import os
# # ---------------------- DATABASE CONECTION ------------------
client = MongoClient(os.getenv("MONGODB_STRING"))
db = client['TredBuddy']
db_orders = db['Orders']
db_positions = db['Positions']

def find_treds(fyers):
    # MyIndex = ["NSE:NIFTY50-INDEX","NSE:NIFTYBANK-INDEX","NSE:FINNIFTY-INDEX","BSE:SENSEX-INDEX"]
    MyIndex = ["NSE:NIFTY50-INDEX","NSE:NIFTYBANK-INDEX"]
    # MyIndex = ["NSE:NIFTY50-INDEX"]

    live_index= fyers.get_current_ltp(",".join(MyIndex))
    index_data_list = list(zip(MyIndex, live_index.values()))
    try:
        def process_index(index_data):
            index_name, current_price = index_data
            index_status = Main_Stetegy_execution(index_name,current_price,fyers)
            if index_status != "NONE":
                current_datetime = datetime.now().strftime('%m/%d/%Y %I:%M %p')
                index_new_name,index_sl,index_tg = get_index_info(index_name)  
                index_side = index_status
                execution_id = generate_id()

                option_info = Get_Option_info(index_new_name,index_side,current_price)
                if option_info != False:
                    option_lot_size = option_info['LOT']
                    option_symbol = option_info['SYMBOL']
                    option_expiry = option_info['EXDATETIME'].date()
                    option_sp = option_info['STRICK PRICE']

                    option_ltp_obj =fyers.get_current_ltp(option_symbol)
                    option_ltp = option_ltp_obj[option_symbol[4:]]

                    sl_factor, tg_factor = (100 - index_sl, 100 + index_tg) if index_side == "CE" else (100 + index_sl, 100 - index_tg)
                    option_ltp_sl = (option_ltp * sl_factor) / 100
                    option_ltp_target = (option_ltp * tg_factor) / 100
                    print(f"[SUCESS] : ALGO FIND A TRED----------- [ BUY {current_datetime} | {option_symbol} | {current_price} | {index_side}] ------------")

                    new_row = {'EXECUTION ID': execution_id,
                                        'INDEX': index_new_name,
                                        'SIDE':index_side,
                                        'TRIGGER INDEX PRICE':current_price,
                                        'OPTION':option_sp,
                                        'OPTION SYMBOL':option_symbol,
                                        'BUY PRICE':option_ltp,
                                        'QTY':option_lot_size,
                                        'BUY DATETIME':datetime.now().strftime('%m/%d/%Y %I:%M %p'),
                                        "SL PRICE":option_ltp_sl,
                                        "TARGET PRICE":option_ltp_target,
                                        "SELL PRICE":0,
                                        "SELL DATETIME":"",
                                        "TARILING COUNT":0,
                                        "PnL GROW":0,
                                        "PnL GROW %":0,
                                        "POINTS":0,
                                        "TRED TIME":"",
                                        "STATUS" :"Running"
                                        } 
                    db_positions.insert_one(new_row)
                    print("[SUCESS] TRED EXECUETD SUCESS")


        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(process_index, index_data_list )
    except:
        print(" [END] : SOMETHING WRONG TO AUTO TRED :< ")



