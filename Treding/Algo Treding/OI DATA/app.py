import time
import pandas as pd
import requests
from datetime import datetime

def fetch_nifty_bank_option():
    base_headers = {
        'Host': 'www.nseindia.com',
        'Referer': 'https://www.nseindia.com/get-quotes/equity?symbol=SBIN',
        'X-Requested-With': 'XMLHttpRequest',
        'pragma': 'no-cache',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
    }

    # url = "https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY"
    url = "https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY"
    try:
        response = requests.get(url, headers=base_headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to fetch data from {url}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching data from {url}: {str(e)}")
    
    return None

def oi_data(data):
    data_df = []
    current_strike_price = data['records']['underlyingValue']
    expiryDates = data['records']['expiryDates']
    top_10_data = data['records']['data']
    filtered_data = []
    
    for i in top_10_data:
        if (current_strike_price - 500) <= i['strikePrice'] <= (current_strike_price + 500) and i['expiryDate'] == expiryDates[0]:
            filtered_data.append(i)
            
    main_data = []
    for item in filtered_data:
        strike_price = item['strikePrice']   
        if strike_price < current_strike_price:
            category = 'Below'
        else:
            category = 'Above'
        ce_oi  = item['CE']['openInterest']
        ce_oi_change  = item['CE']['changeinOpenInterest']
        ce_oi_change_pr  = item['CE']['pchangeinOpenInterest']
        ce_oi_volume  = item['CE']['totalTradedVolume']
        ce_iv  = item['CE']['impliedVolatility']
    
        pe_oi  = item['PE']['openInterest']
        pe_oi_change  = item['PE']['changeinOpenInterest']
        pe_oi_change_pr  = item['PE']['pchangeinOpenInterest']
        pe_oi_volume  = item['PE']['totalTradedVolume']
        pe_iv  = item['PE']['impliedVolatility']


    
        my_dict = {"strike_price":strike_price,"category":category,"ce_oi":ce_oi,"ce_oi_change":ce_oi_change,"ce_oi_change_pr":ce_oi_change_pr,"ce_oi_volume":ce_oi_volume, 
                   "ce_iv":ce_iv,"pe_oi":pe_oi,"pe_oi_change":pe_oi_change,"pe_oi_change_pr":pe_oi_change_pr,"pe_oi_volume":pe_oi_volume,"pe_iv":pe_iv,}
        main_data.append(my_dict)

    df = pd.DataFrame(main_data)
    total_ot_CE = sum(list(df['ce_oi']))
    total_ot_CE_chnage = sum(list(df['ce_oi_change']))
    total_ot_PE = sum(list(df['pe_oi']))
    total_ot_PE_chnage = sum(list(df['pe_oi_change']))
    total_ot_PE_iv = sum(list(df['pe_iv']))
    total_ot_CE_iv = sum(list(df['ce_iv']))
    
    result_dict = {
        "CE OI": total_ot_CE,
        "PE OI": total_ot_PE,
        "CE OI Change": total_ot_CE_chnage,
        "PE OI Change": total_ot_PE_chnage,
        "CE IV":total_ot_CE_iv,
        "PE IV":total_ot_PE_iv,
    }

    max_age_row = df[df['pe_oi'] == df['pe_oi'].max()]
    result_dict["Strike Price"] = current_strike_price
    result_dict["RESISTANCE"] = max_age_row.iloc[0]['strike_price']

    min_age_row = df[df['ce_oi'] == df['ce_oi'].max()]
    result_dict["SUPPORT"] = min_age_row.iloc[0]['strike_price']

    oi_change = total_ot_PE_chnage / total_ot_CE_chnage
    result_dict["P/C Chnage"] = oi_change
    result_dict["P/C "] = total_ot_PE/total_ot_CE

    if oi_change < 0.8:
        result_dict["Movement"] = "DOWN SIDE MOVE"
    elif oi_change > 1: 
        result_dict["Movement"] = "UP SIDE MOVE"
    else:
        result_dict["Movement"] = "NO SIGNIFICANT MOVE"

    result_dict["PE Total Change%"] = sum(list(df['pe_oi_change_pr']))
    result_dict["CE Total Change%"] = sum(list(df['ce_oi_change_pr']))
    current_datetime = datetime.now()
    result_dict["DateTime"] = current_datetime.strftime('%d-%m-%Y | %H:%M') 

    data_df.append(result_dict)
    return data_df


start_time = 9 * 3600 + 15 * 60  # Convert 9:15 AM to seconds
end_time = 15 * 3600 + 30 * 60  # Convert 3:30 PM to seconds

while True:
    try:
        current_time = time.localtime()
        current_seconds = current_time.tm_hour * 3600 + current_time.tm_min * 60 + current_time.tm_sec

        if start_time <= current_seconds <= end_time:
            data = fetch_nifty_bank_option()
            oi_data_df = oi_data(data)
            
            # Load existing data from the Excel file, if it exists
            try:
                existing_df = pd.read_excel("nifty50_oi_data.xlsx")
            except FileNotFoundError:
                existing_df = pd.DataFrame()

            # Append new data to the existing data
            # Append new data to the existing data
            try:
                combined_df = pd.concat([existing_df, pd.DataFrame(oi_data_df)], ignore_index=True)
                combined_df = combined_df.round(2)
                combined_df.to_excel("nifty50_oi_data.xlsx", index=False)
                print("Data saved to Excel.")
            except:
                print("Skip this data")

        else:
            print("Not in Time")
            break
    except :
        print("Error Acure")

    time.sleep(120)  # Wait for 60 seconds before the next iteration