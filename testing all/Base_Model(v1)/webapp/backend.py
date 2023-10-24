import requests
import time
import http.client
import json
import datetime


from testweb import webmain

# APIS
def put_call_ratio(date):
    print("PCR RUN ----------------------------------------")
    # in =27-Jul-2023
    # need = 27-07-2023
    # Conveter
    try:

        output_date_str = datetime.datetime.strptime(date, "%d-%b-%Y").strftime("%d-%m-%Y")
        url = f"https://api.indiainfoline.com/api/cmots/v1/derivatives/put-call-ratio/idx/all/{output_date_str}/Symbol/5/Desc"

        response = requests.request("GET", url)

        pcr_data = response.json()

        PCRatioOI =float(pcr_data['data'][0]['PCRatioOI'])
        # PCRatioOI = 1.3

        return PCRatioOI
    except:
        return None

    
def vix_india():
    print("VIX RUN ----------------------------------------")

    import http.client
    try:

        conn = http.client.HTTPSConnection("appfeeds.moneycontrol.com")
        payload = ''
        headers = {}
        conn.request("GET", "/jsonapi/market/indices&format=json&t_device=iphone&t_app=MC&t_version=48&ind_id=36", payload, headers)
        res = conn.getresponse()
        data = res.read()
        vix_alldata=json.loads(data.decode("utf-8"))

        vix = float(vix_alldata['indices']['lastprice'])
        # vix = 11.22

        return vix
    except:
        return None

def Nifty50_list():
    print("NIFTY 50 LIST RUN ----------------------------------------")

    conn = http.client.HTTPSConnection("www.nseindia.com")
    payload = ''
    headers = {
  'Cookie': 'ak_bmsc=166B3F25E7CFF36DE29F14035588E816~000000000000000000000000000000~YAAQBzkgFyzrQaGJAQAAz6rauxS398jO/qncLGWlQ99woC3zcRPTnOk408v8mdONAFIssejXTo1hPaqkAfPcPacdvJWfoEngWOjMb/nHMAmKp5Jwwi+SKKqMwwexJxuz/r+7QhUEeXm70SNwVsXKAbNBwJiQx0TOb9/Q5NRovEQNnnFA4j0p0xI2XYJ0s+ET+kT+nWGYffdLqlWT+Xa6vlOHqd6iloNByryaqc3uhY3nfoOx+YqeHoydY+JT72db8nLuYohWfV736iLC0tZYUllIOHZa+4AyS+95OhQdBVNV+6XqvtvMmbSfAZSaBlLP9yVZzgQt8aQJkKycvFm3Be+2pSjPFDxMAjEw6wCJJPFvfd65Dm9PpuYvTTfzoQ==; bm_sv=A1F4BD1F2E9BE0CC7D54EF240EA7212E~YAAQBzkgF8vrQaGJAQAAHsTauxSTl0dKv7Y4tRGhcf+F0B0jV5u7zmTZRDnin0vfwrqVr1oXiVjJPa9E2vRxfmp+jTmIUxjpOOXpB7yXWEgWti3G7H2V7unzOzh7uckqXFSYSdAXqC3L8QlGy0aoToj6N1RcPPOfaeruRRAlg1KDadqn7tS8Ml6mD0FPvdVpXOnDnuSRCV7zFp7+Rn36njqGxaFsgISz/tzRzXcUs05fmSnFQRTNLCSxz+Aj8q6HTS8=~1'
}
    conn.request("GET", "/api/equity-stockIndices?index=NIFTY%2050", payload, headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    alldata = json.loads(data)

    nifty_compny_list = []

    for i in alldata['data']:
        #  i = darek compny ni dictionry 
        com_name = i['symbol']
        com_today_price = i['lastPrice']
        com_today_change= i['change']

        nifty_compny_list.append({
                "com_name":com_name,
                "com_today_price":com_today_price,
                "com_today_change":com_today_change            
                })

    market_status = alldata['marketStatus']
    market_metadata = alldata['metadata']

    non_positive_prices = [product for product in nifty_compny_list if product.get("com_today_change", 0) <= 0]
    positive_prices = [product for product in nifty_compny_list if product.get("com_today_change", 0) >= 1]

    sorted_data_by_chnage = sorted(non_positive_prices, key=lambda x: x["com_today_change"],reverse=True)
    max_chnage_com_up = [product  for product in sorted_data_by_chnage[:10]] # chnage 5 for more compnay


    sorted_data_by_chnage = sorted(positive_prices, key=lambda x: x["com_today_change"])
    max_chnage_com_down = [product for product in sorted_data_by_chnage[:10]]


    print(f"Negative prices: {len(non_positive_prices)}   ||||    Positive prices: {len(positive_prices)}")
    print(f"To days Down Compny : {max_chnage_com_down}   ||||    To days Up Compny : {max_chnage_com_up}" )

    res_data = {
        "max_chnage_com_down":max_chnage_com_down,
        "max_chnage_com_up":max_chnage_com_up,
        "downfall_no":len(non_positive_prices),
        "upfall_no":len(positive_prices),
        "market_metadata":market_metadata,
        "market_status":market_status,
        "row_data":alldata
    }
    return res_data

def Nifty50_chain():
    print("NIFTY 50 CHAIN RUN ----------------------------------------")

    conn = http.client.HTTPSConnection("www.nseindia.com")
    payload = ''
    headers = {
  'Cookie': 'ak_bmsc=166B3F25E7CFF36DE29F14035588E816~000000000000000000000000000000~YAAQBzkgFyzrQaGJAQAAz6rauxS398jO/qncLGWlQ99woC3zcRPTnOk408v8mdONAFIssejXTo1hPaqkAfPcPacdvJWfoEngWOjMb/nHMAmKp5Jwwi+SKKqMwwexJxuz/r+7QhUEeXm70SNwVsXKAbNBwJiQx0TOb9/Q5NRovEQNnnFA4j0p0xI2XYJ0s+ET+kT+nWGYffdLqlWT+Xa6vlOHqd6iloNByryaqc3uhY3nfoOx+YqeHoydY+JT72db8nLuYohWfV736iLC0tZYUllIOHZa+4AyS+95OhQdBVNV+6XqvtvMmbSfAZSaBlLP9yVZzgQt8aQJkKycvFm3Be+2pSjPFDxMAjEw6wCJJPFvfd65Dm9PpuYvTTfzoQ==; bm_sv=A1F4BD1F2E9BE0CC7D54EF240EA7212E~YAAQBzkgF/PtQaGJAQAAZX/buxSmkzLBbd+f48gPAbP3UOA5kwsRWATG1CJHq8FZUvCSbmIdQGjr8HhsuwTMZnimEr0k5XA4QkT1mBSq0qFjXQemhTbDc8ONFhL5IUzoIcXBCxnPYnpreNaat5qGwkzYyaOEQ5a0rsLsGne+fpX9XxKdmAYmzkkcDkAxSC820KR1FnbYuvbMgFfGpFKbv2TBXKvEMOIXjZ+DpuzwgWELQ78280eBbK3ILLVecrnWFtU=~1'
}
    conn.request("GET", "/api/option-chain-indices?symbol=NIFTY", payload, headers)

    res = conn.getresponse()
    data = res.read().decode("utf-8")
    alldata = json.loads(data)

    expiry_date = alldata['records']['expiryDates']

    filtered_data = alldata['filtered']['data']
    total_ce_data = alldata['filtered']["CE"]
    total_pe_data = alldata['filtered']["PE"]

    current_pcr_oi = float(total_pe_data['totOI'])/float(total_ce_data['totOI'])
    current_pcr_vol = float(total_pe_data['totVol'])/float(total_ce_data['totVol'])

    my_nifty_data =filtered_data

    sorted_data_by_oi_ce = sorted(my_nifty_data, key=lambda x: x['CE']["openInterest"],reverse=True)
    ce_resistance= [(product['CE']['strikePrice'],product['CE']['openInterest']) for product in sorted_data_by_oi_ce[:2]]

    sorted_data_by_oi_ce = sorted(my_nifty_data, key=lambda x: x['PE']["openInterest"],reverse=True)
    pe_suport= [(product['PE']['strikePrice'],product['PE']['openInterest']) for product in sorted_data_by_oi_ce[:2]]


    timestamp = alldata['records']['timestamp']

    print("Time :",timestamp)
    print(f" RESISTANCE : {ce_resistance}   |||    SUPORT : {pe_suport}")
    print(f"Current Total PCR(OI): {current_pcr_oi}     |||     Current Total PCR(Vol): {current_pcr_vol}")

    res_data ={
        "expiry_date":expiry_date,
        "current_pcr_oi":current_pcr_oi,
        "current_pcr_vol":current_pcr_vol,
        "ce_resistance":ce_resistance,
        "pe_suport":pe_suport,
        "timestamp":timestamp,
        "strikePrices":alldata['records']['strikePrices'],
        "row_data":alldata
    }
    return res_data



# Send Data
def process_data(data_dictionary):
    webmain(data_dictionary)


def main():
    data_dictionary = {}
    
    while True:
        now = datetime.datetime.now()

        # Check if the current time is between 9:15 AM and 3:15 PM
        if now.hour >= 9 and now.hour <= 23 :
            print("-------------------- Current time:", now.strftime("%H:%M"),"--------------------")
            # API call
            ex_date = "27-Jul-2023"
            data_dictionary['status']= "Open"
            data_dictionary['last_update_time']= now.strftime("%H:%M")
            data_dictionary['pcr']= put_call_ratio(ex_date)
            data_dictionary['vix']= vix_india()
            data_dictionary['Nifty50_list']= Nifty50_list()
            data_dictionary['Nifty50_chain']= Nifty50_chain()

            process_data(data_dictionary)
            
        else:
            data_dictionary['status']= "Close"
            process_data(data_dictionary)
            break

        time.sleep(120)

if __name__ == "__main__":
    main()
