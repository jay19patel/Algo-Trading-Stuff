from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
from pyotp import TOTP
from fyers_apiv3 import fyersModel
import os
import requests
import pandas as pd
import pytz
from dotenv import load_dotenv

load_dotenv()




from datetime import datetime , timedelta
def Data_From_url(url, access_token, payload):
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en;q=0.9",
        "Access-Token": access_token,
        "Content-Type": "application/json",
        "Origin": "https://myaccount.fyers.in",
        "Referer": "https://myaccount.fyers.in/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    }
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"API request failed with status code: {response.status_code}")
        return response.text

class Fyers:
    def __init__(self) -> None:

        self.userid = os.getenv("USER_ID")
        self.mobileno = os.getenv("MOBILE_NO")
        self.client_id = os.getenv("CLIENT_ID")
        self.secret_key = os.getenv("SECRET_KEY")
        self.app_pin = os.getenv("APP_PIN")
        self.totp_key = os.getenv("TOTP_KEY")
        self.redirect_uri = "https://trade.fyers.in/api-login/redirect-uri/index.html"
        self.response_type = "code"
        self.grant_type = "authorization_code"
        self.state = "sample_state"
        self.authenticate = False
        self.access_token = None
        self.Capital = 10000
        self.tred_amount = round(self.Capital/4,2)

        print("[ Fyers Initializeation ]")
      
    def get_access_token(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")

        session = fyersModel.SessionModel(
            client_id=self.client_id,
            secret_key=self.secret_key, 
            redirect_uri=self.redirect_uri, 
            response_type=self.response_type, 
            grant_type=self.grant_type
        )
        auth_link = session.generate_authcode()

        driver = webdriver.Chrome(options=chrome_options)
        try:
            driver.get(auth_link)
            time.sleep(2)

            driver.find_element(By.ID, "mobile-code").send_keys(self.mobileno)
            driver.find_element(By.ID, "mobileNumberSubmit").click()
            time.sleep(4)
            myotp = TOTP(self.totp_key).now()
            driver.find_element(By.XPATH, '//*[@id="first"]').send_keys(myotp[0])
            driver.find_element(By.XPATH, '//*[@id="second"]').send_keys(myotp[1])
            driver.find_element(By.XPATH, '//*[@id="third"]').send_keys(myotp[2])
            driver.find_element(By.XPATH, '//*[@id="fourth"]').send_keys(myotp[3])
            driver.find_element(By.XPATH, '//*[@id="fifth"]').send_keys(myotp[4])
            driver.find_element(By.XPATH, '//*[@id="sixth"]').send_keys(myotp[5])
            driver.find_element(By.XPATH, '//*[@id="confirmOtpSubmit"]').click()
            time.sleep(2)
            driver.find_element(By.ID, 'pin-container').find_element(By.ID, 'first').send_keys(self.app_pin[0])
            driver.find_element(By.ID, 'pin-container').find_element(By.ID, 'second').send_keys(self.app_pin[1])
            driver.find_element(By.ID, 'pin-container').find_element(By.ID, 'third').send_keys(self.app_pin[2])
            driver.find_element(By.ID, 'pin-container').find_element(By.ID, 'fourth').send_keys(self.app_pin[3])
            driver.find_element(By.ID, 'verifyPinSubmit').click()
            time.sleep(2)
            current_url = driver.current_url
            auth_code = current_url[current_url.index('auth_code=')+10:current_url.index('&state')]

            session.set_token(auth_code)
            response = session.generate_token()
            access_token = response['access_token']
            
            with open('Private/access_token.txt', 'w') as file:
                file.write(access_token)
            
        finally:
            print("[ Fyers Access Token  ]")
            driver.quit()

    def authentication(self):
        if not self.authenticate:
            access_token_path = "Private/access_token.txt"
            if not os.path.exists(access_token_path):
                open(access_token_path, 'a').close()
            access_token = open(access_token_path, 'r').read().strip()
            if access_token:
                try:
                    fyers = fyersModel.FyersModel(client_id=self.client_id, is_async=False, token=access_token, log_path="Private/")
                    print("Successful Login: ", fyers.get_profile()['data']['name'])
                    self.authenticate = True
                    self.access_token = access_token
                    self.fyers_instance = fyers
                    print("[ Fyers Authenticated  ]")
                
                except Exception as e:
                    print(" Authentication Error:", e)
                    print(" [ Resolve Error Again.... ]")
                    self.get_access_token()
                    self.authentication()
                    
            else:
                self.get_access_token()
                self.authentication()
                print("[ Resolve Error Again.... ]")

        else:
            print("[ Alredy Authenticated ]")


    def profile(self):
            if self.authenticate:
                data = self.fyers_instance.get_profile()['data']
                print(" [ Fyers Profile ]")
                return data
            else:
                print("[ERROR: Not Authenticated]")
                return None


    def get_current_ltp(self, option_symbol):
        if self.authenticate:
            data = {"symbols": option_symbol}
            data = self.fyers_instance.quotes(data=data)
            if data['code'] == 200:
                return {item['v'].get('short_name', 'Unknown'): item['v'].get('lp', 'Unknown') for item in data['d']}
            else:
                print("[DATA NOT GET FROM FYERS]")
                return False
        else:
            print("[ERROR: Authentication Failed]")
            return "[ERROR: Authentication Failed]"
        

    def Fyers_overview(self):
        if self.authenticate:
            url_pnl = "https://api-a1-prod.fyers.in/myaccount/prod/report/global-pnl"
            payload_pnl = {
                "to_date": datetime.now().strftime("%Y/%m/%d"),
                "from_date": "2023/04/01",
                "with_options": "Y",
                "with_expenses": "Y",
                "segments": [3, 8, 7, 5, 4, 6, 9, 10, 11]
            }
            pnl_data = Data_From_url(url_pnl, self.access_token, payload_pnl)
            
            charges = pnl_data['data']['expense']['TOTAL'][0]['value']
            gross_pnl = pnl_data['data']['expense']['SUMMARY'][0]['gross_pnl']
            net_pnl = pnl_data['data']['expense']['SUMMARY'][0]['net_pnl']
            
            pnl_values = [trade['p_n_l'] for trade in pnl_data['data']['global_pnl']['DATA']]
            total_trades = len(pnl_data['data']['global_pnl']['DATA'])
            
            winning_trades = sum(pnl > 0 for pnl in pnl_values)
            win_ratio_percentage = (winning_trades / total_trades) * 100
            
            max_pnl = max(pnl_values)
            min_pnl = min(pnl_values)
            
            url_deposit = "https://api-a1-prod.fyers.in/myaccount/prod/user-deposit-history"
            payload_deposit = {
                "page_no": 1,
                "page_size": 10,
                "filter": {"status": [2]}
            }
            deposit_data = Data_From_url(url_deposit, self.access_token, payload_deposit)
            total_deposit = sum(entry['amount'] for entry in deposit_data['data']['deposit_history'])
            
            url_withdrawal = "https://api-a1-prod.fyers.in/myaccount/prod/user-withdrawal-history"
            payload_withdrawal = {
                "page_no": 1,
                "page_size": 10,
                "filter": {"status": [2]}
            }
            withdrawal_data = Data_From_url(url_withdrawal, self.access_token, payload_withdrawal)
            total_withdrawal = sum(entry['amount'] for entry in withdrawal_data['data']['withdrawable_history'])
            print(" [ Fyers Acount Overview ]")
            
            return {
                    "Charges": charges,
                    "Gross PnL": gross_pnl,
                    "Net PnL": net_pnl,
                    "Max Profit": max_pnl,
                    "Max Loss": min_pnl,
                    "Total Trades": total_trades,
                    "Win": winning_trades,
                    "Loss": total_trades - winning_trades,
                    "Win Ratio": win_ratio_percentage,
                    "Total Deposit": total_deposit, 
                    "Deposit Hist": deposit_data['data'],
                    "Total Withdrawal": total_withdrawal, 
                    "Withdrawal Hist": withdrawal_data['data']
            }
        else:
            print("[ Authentication Fail ]")
            return "[ Authentication Fail ]"
        
    def Historical_Data(self,Symbol,TimeFrame):
        data = {
                    "symbol":Symbol,
                    "resolution": TimeFrame,
                    "date_format":"1",
                    "range_from":(datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d'),
                    "range_to":datetime.now().strftime('%Y-%m-%d'),
                    "cont_flag":"0"
                }
        row_data =  self.fyers_instance.history(data=data)
        if row_data['s']== "ok":
            df = pd.DataFrame.from_dict(row_data['candles'])
            columns_name = ['Datetime','Open','High','Low','Close','Volume']
            df.columns = columns_name
            df['Datetime'] = pd.to_datetime(df['Datetime'], unit='s')
            df['Datetime'] = df['Datetime'].dt.tz_localize(pytz.utc).dt.tz_convert('Asia/Kolkata')
            df['Datetime'] = df['Datetime'].dt.tz_localize(None)
            return df
        else:
            return row_data['s']

    def Get_Lotsize(self,quantity_per_lot,price_per_lot):
        varinace = 100
        lot_size = int((self.tred_amount - 50 - varinace)/(quantity_per_lot*price_per_lot))
        print(f"Tred_Capital :{self.tred_amount}| Lot Size : {lot_size} Price : {price_per_lot}")
        return lot_size



















