import requests
from datetime import datetime
from pymongo import MongoClient



client = MongoClient('mongodb+srv://justj:justj@cluster0.fsgzjrl.mongodb.net/')
db = client['TredBuddy2']
db_fidi = db['FiDi Data']



def nse_online_fiidi():
    url = "https://www.nseindia.com/api/fiidiiTradeReact"
    headers = {
        'Referer': 'https://www.nseindia.com/reports/fii-dii',
        'Sec-Ch-Ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Microsoft Edge";v="122"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0not use cookie'
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    buying = round(sum([float(i['buyValue']) for i in data]),2)
    selling = round(sum([float(i['sellValue']) for i in data]),2)
    netvalue = round(sum([float(i['netValue']) for i in data]),2)
    date = data[0]['date']
    output = {"Date":date,"Buying":buying,"Selling":selling,"Overall":netvalue}
    print(output)
    return output


def nse_fidi():
    data = db_fidi.find_one({"Date":datetime.now().strftime("%d-%b-%Y")})
    if data :
        data.pop('_id', None)
        return  data
    else:
        data = nse_online_fiidi()
        data.pop('_id', None)
        return data 


print(nse_fidi())