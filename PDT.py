#Test One time Request 

from Fyers import Fyers
import concurrent.futures
from datetime import datetime , timedelta
from pymongo import MongoClient
import json
from TredBuddy_Helper import Get_Option_info


# ---------------------- DATABASE CONECTION ------------------
client = MongoClient('mongodb://localhost:27017/')
db = client['TredBuddy']
db_orders = db['Orders']
db_positions = db['Positions']
live_options = db['Live_Options']
# -------------------------------------------------------------


#  ---------------------- TRED EXECUTE ------------------

def Tred_Execution(get_index,get_cuurent_price,get_tred_side,get_execution_id,fyers):
    option_info = Get_Option_info(get_index,get_tred_side,get_cuurent_price)
    # print(option_info)
    if option_info != None:
        option_lot_size = option_info['LOT']
        option_symbol = option_info['SYMBOL']
        option_expiry = option_info['EXDATETIME'].date()
        option_sp = option_info['STRICK PRICE']

        option_ltp =fyers.get_current_ltp(option_symbol)
        option_ltp_sl = (option_ltp*70)/100
        option_ltp_target = (option_ltp*150)/100
        
        print(f'''
            BUY     : {option_sp}
            PRICE   : {option_ltp}
            SL      : {option_ltp_sl}
            TARGET  : {option_ltp_target} 
              ''')
        # add in txt for live server 

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
        # db_positions.insert_one(new_row)
        print(" [2] TRED EXECUETD ")



# ---------------------- INDEX LIVE DATA FETCH ------------------
def Trigger_pdt(fyers):
    MyIndex = "NSE:NIFTY50-INDEX,NSE:NIFTYBANK-INDEX,NSE:FINNIFTY-INDEX"
    indexeslive = fyers.get_current_ltp(MyIndex)
    if indexeslive != False:
        df = db_orders.find({'EXECUTION STATUS':'Panding'})
        current_datetime = datetime.now().strftime('%m/%d/%Y %I:%M %p')
        row_data = [json.dumps(document, default=str) for document in df]
        def check_condition(entry, index_name, index_price):
            row = json.loads(entry)
            price = float(row["PRICE"])
            condition = row["CONDITION"]
            execution_id = row['EXECUTION ID']
            if ((condition == "ABOVE" and price <= index_price) or (condition == "BELOW" and price >= index_price)) and index_name == row['INDEX']:
                # filter_criteria = {'EXECUTION ID': execution_id}
                # update_execution = {'$set': {'EXECUTION STATUS': "Executed"}}
                # update_datetime = {'$set': {'EXECUTION DATETIME': current_datetime}}
                # db_orders.update_one(filter_criteria, update_execution)
                # db_orders.update_one(filter_criteria, update_datetime)
                print(f" [1] TRIGGER PDT : {index_name} {index_price}  ")
                # Tred_Execution(index_name,index_price,row['SIDE'],execution_id,fyers)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(check_condition, entry, index_name, index_price) for entry in row_data for index_name, index_price in indexeslive.items()]
    else:
        print("[SOMETHING WRONG TO GET LIVE DATA ]")




#  ------------------------------ EXIT WALA CODE  SL / TARGET ------------------------------
def update_position(i, live_data):
    try:
        # ------------------------------- TARGET CHECK ---------------------------------
        if 'TARGET PRICE' in i and i['TARGET PRICE'] <= live_data[i['OPTION SYMBOL']]:
            live_data_float = float(live_data[i['OPTION SYMBOL']])  # Convert live_data to float if it's not already
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
            # db_positions.update_one(filter_criteria, update_execution)
            print(f"[{i['OPTION SYMBOL']} : Target Hit]")

            print("Updated TARGET PRICE:", new_target)
            print("Updated SL PRICE:", new_sl)
            print(" [3] TARGET TRAILING (UPDATED)")

        # ------------------------------- SL CHECK ---------------------------------
        if 'SL PRICE' in i and i['SL PRICE'] >= live_data[i['OPTION SYMBOL']]:
            live_data_float = float(live_data[i['OPTION SYMBOL']])  # Convert live_data to float if it's not already
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
            # db_positions.update_one(filter_criteria, update_execution)
            print(f"[{i['OPTION SYMBOL']} : SL Hit]")
            print("PNL_GROW:", PNL_GROW)
            print("PNL_GROW_PR:", PNL_GROW_PR)
            print(" [3] SL HIT ")

        print(f"[{i['OPTION SYMBOL']} : Running]")
    except Exception as e:
        print(f" [3] ERROR IN TRED EXECUTION SL TARGET (ERROR : {e} )")

def target_trailing(fyers):
    
    row_data = [document for document in db_positions.find("STATUS" == "Running")]

    live_data2 = " , ".join([item['OPTION SYMBOL'] for item in row_data if item.get('STATUS') != 'Running'])

    live_data = {'NSE:NIFTY2420121700CE': 350.5,
                 'NSE:NIFTY2420121750CE': 334.5}


    if len(live_data)>=1:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for i in row_data:
                executor.submit(update_position, i, live_data)
    else:
        print("[ NO OPEN POSITION ]")



