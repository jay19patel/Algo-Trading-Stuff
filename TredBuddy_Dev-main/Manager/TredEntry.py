
from Manager import Strategy_Helper 

import concurrent.futures

SYMBOLS = ["NSE:NIFTY50-INDEX", "NSE:NIFTYBANK-INDEX", "NSE:FINNIFTY-INDEX", "BSE:SENSEX-INDEX", "BSE:BANKEX-INDEX"]
# SYMBOLS = ["NSE:NIFTY50-INDEX"]

def TredEntry(fyers):
    live_index = fyers.get_current_ltp(",".join(SYMBOLS))
    index_data_list = list(zip(SYMBOLS, live_index.values()))
    

    def FindEntrys(index_data):
          stategy_status = Strategy_Helper.Main_Stetegy_execution(Symbol=index_data[0], current_price=index_data[1], fyers=fyers)
            # Add more stategy here 
          
    with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(FindEntrys, index_data_list)



