#Test One time Request 

from Fyers import Fyers
import concurrent.futures
from datetime import datetime , timedelta
from pymongo import MongoClient
import json
from TredBuddy_Helper import Get_Option_info,get_index_name,generate_id
from Stretegy_Helper import Main_Stetegy_execution

# ---------------------- DATABASE CONECTION ------------------
client = MongoClient('mongodb+srv://justj:justj@cluster0.fsgzjrl.mongodb.net/')
db = client['TredBuddy']
db_orders = db['Orders']
db_positions = db['Positions']
# -------------------------------------------------------------


#  ------------------------------------------------------------ TRED EXECUTE ------------------

def Tred_Execution(get_index,get_cuurent_price,get_tred_side,get_execution_id,fyers):
    option_info = Get_Option_info(get_index,get_tred_side,get_cuurent_price)
    if option_info != False:
        option_lot_size = option_info['LOT']
        option_symbol = option_info['SYMBOL']
        option_expiry = option_info['EXDATETIME'].date()
        option_sp = option_info['STRICK PRICE']

        option_ltp_obj =fyers.get_current_ltp(option_symbol)
        option_ltp = option_ltp_obj[option_symbol[4:]]
        option_ltp_sl = (option_ltp*70)/100
        option_ltp_target = (option_ltp*150)/100

        print(f'''
            - [2 SUCESS] ----------- [ BUY ] ------------
            BUY     : {option_sp}
            PRICE   : {option_ltp}
            SL      : {option_ltp_sl}
            TARGET  : {option_ltp_target} 
              ''')

        new_row = {'EXECUTION ID': get_execution_id,
                    'INDEX': get_index,
                    'SIDE':get_tred_side,
                    'TRIGGER INDEX PRICE':get_cuurent_price,
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
        print(" [2 SUCESS] TRED EXECUETD SUCESS ")
    else:
        print(" [2 ERROR ] : OPTION DATA NOT GETING ")


# ---------------------------------------------------- INDEX LIVE DATA FETCH ------------------
def Trigger_pdt(fyers):
    # MyIndex = ["NSE:NIFTY50-INDEX","NSE:NIFTYBANK-INDEX","NSE:FINNIFTY-INDEX"]
    MyIndex = ["NSE:NIFTYBANK-INDEX"]
    print(" [1 SUCESS] : FIND TRED USING AUTO TRED SYSTEM ")
    try:
        def process_index(index_name):
            index_status = Main_Stetegy_execution(index_name,15,fyers)
            if index_status.get(index_name) !="None":
                current_datetime = datetime.now().strftime('%m/%d/%Y %I:%M %p')
                index_new_name = get_index_name(index_name)
                index_price = index_status.get("Price")
                index_side = index_status.get(index_name)
                execution_id = generate_id()
                print(f" [1] : ALGO FIND A TRED  : {index_new_name} || {index_price} || {index_side} ")
                Tred_Execution(index_new_name,index_price,index_side,execution_id,fyers)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(process_index, MyIndex)
    except:
        print(" [1 END ] : SOMETHING WRONG TO AUTO TRED :< ")




#  ---------------------------------------------- EXIT WALA CODE  SL / TARGET ------------------------------
def update_position(i, live_data):
    try:
        print(f"[{i['OPTION SYMBOL']} : Running]")
        indexsymbol = i['OPTION SYMBOL'][4:]
        # ------------------------------- TARGET CHECK ---------------------------------
        if 'TARGET PRICE' in i and i['TARGET PRICE'] <= live_data[indexsymbol]:
            live_data_float = float(live_data[indexsymbol])  # Convert live_data to float if it's not already
            new_target = (live_data_float * 120) / 100  # +20%
            new_sl = (live_data_float * 90) / 100  # -10%
            filter_criteria = {'EXECUTION ID': i['EXECUTION ID']}
            update_execution = {
                '$set': {
                    'TARGET PRICE': new_target,
                    'SL PRICE': new_sl,
                    'TARILING COUNT': i.get('TARILING COUNT', 0) + 1,
                }
            }
            db_positions.update_one(filter_criteria, update_execution)
            print(f"[{i['OPTION SYMBOL']} : Target Hit]")
            print(" [3] : Updated TARGET PRICE:", new_target)
            print(" [3] : Updated SL PRICE:", new_sl)
            print(" [3] : TARGET TRAILING (UPDATED)")

        # ------------------------------- SL CHECK ---------------------------------
        if 'SL PRICE' in i and i['SL PRICE'] >= live_data[indexsymbol]:

            live_data_float = float(live_data[indexsymbol])  
            filter_criteria = {'EXECUTION ID': i['EXECUTION ID']}
            PNL_GROW = int((i['SL PRICE'] - i['BUY PRICE']) * i['QTY'])
            PNL_GROW_PR = PNL_GROW * 100 / (i['BUY PRICE'] * i['QTY'])
            update_execution = {
                '$set': {
                    'STATUS': "SL Hit",
                    'SELL PRICE': live_data_float,
                    'SELL DATETIME': datetime.now().strftime('%m/%d/%Y %I:%M %p'),
                    'PnL GROW': PNL_GROW,
                    'PnL GROW %': PNL_GROW_PR
                }
            }
            db_positions.update_one(filter_criteria, update_execution)
            print(f"[{i['OPTION SYMBOL']} : SL Hit]")
            print("PNL_GROW:", PNL_GROW)
            print("PNL_GROW_PR:", PNL_GROW_PR)
            print(" [3] SL HIT ")

    except Exception as e:
        print(f" [3] ERROR IN TRED EXECUTION SL TARGET (ERROR : {e} )")




#  ------------------------------------------TRAILING TARGET --------------------------------------
def target_trailing(fyers):
    row_data = [document for document in db_positions.find("STATUS" == "Running")]

    live_data_list = [item['OPTION SYMBOL'] for item in row_data if item.get('STATUS') == 'Running']
    live_data_symbols = ",".join(live_data_list)

    if len(live_data_list) >= 1:
        print(live_data_symbols)
        live_data = fyers.get_current_ltp(live_data_symbols)
        print(f" [101] : LIVE DATA OPTION:{live_data}")

        with concurrent.futures.ThreadPoolExecutor() as executor:
            for i in row_data:
                # print(f"------------------[{i , live_data}]----------------")
                executor.submit(update_position, i, live_data)
    else:
        print(f" [101] : NO OPEN POSITION")



