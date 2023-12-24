
from Fyers_Login import get_access_token
import pandas as pd
from fyers_apiv3 import fyersModel



def Get_fyer_model():
    client_id = "MACO3YJA7I-100"
    access_token_path = "access_token.txt"
    access_token = open(access_token_path, 'r').read() if open(access_token_path, 'r') else None
    try:
        fyers = fyersModel.FyersModel(client_id=client_id, is_async=False, token=access_token, log_path="")
        print("Successfull Login : ",fyers.get_profile()['data']['name'])
        return fyers
    except:
        print("Access Token Genration")
        get_access_token()
        Get_fyer_model()

fyers = Get_fyer_model()








