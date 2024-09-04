import pandas as pd
import requests
from datetime import datetime
import os
import io
import os




def remove_files_in_private_folder():
    private_folder = 'Private'
    if os.path.exists(private_folder):
        files = os.listdir(private_folder)
        for file in files:
            file_path = os.path.join(private_folder, file)
            os.remove(file_path)
        print("All files in the 'Private' folder have been removed.")
    else:
        print("The 'Private' folder does not exist.")

def fetch_option_details():
    print("Fetching new option details...")
    spotnames = ['BANKNIFTY', 'FINNIFTY', 'NIFTY', 'SENSEX', 'BANKEX'] 
    nse_fetch = requests.get('https://public.fyers.in/sym_details/NSE_FO.csv')
    bse_fetch = requests.get('https://public.fyers.in/sym_details/BSE_FO.csv')

    nse_df = pd.read_csv(io.StringIO(nse_fetch.text), header=None)
    bse_df = pd.read_csv(io.StringIO(bse_fetch.text), header=None)

    row_df = pd.concat([nse_df, bse_df])
    row_df = row_df[[0,1,3,8,9,13,15,16]]
    column_names = ["ID", "INDEX INFO", "LOT", "TIMESTAMP", "SYMBOL", "INDEX", "STRIKE PRICE", "SIDE"]
    row_df.columns = column_names
    row_df["EXDATETIME"] = pd.to_datetime(row_df["TIMESTAMP"], unit='s')

    current_date = datetime.now().strftime('%Y-%m-%d')
    filtered_df = row_df[row_df['INDEX'].isin(spotnames) & (pd.to_datetime(row_df["TIMESTAMP"], unit='s').dt.date >= datetime.now().date())]
    
    remove_files_in_private_folder()  # Remove existing files in the Private folder
    
    if not os.path.exists('Private'):
        os.makedirs('Private')

    file_path = f'Private/sym_details_{current_date}.csv'
    filtered_df.to_csv(file_path, index=False)
    print(f"Option details saved to {file_path}")

def get_option_for(trad_index, trad_side, price):
    tred_sp = round(price,-2)
    current_date = datetime.now().strftime('%Y-%m-%d')
    file_path = f'Private/sym_details_{current_date}.csv'

    if not os.path.exists(file_path):
        fetch_option_details()

    option_df = pd.read_csv(file_path)
    option_df["EXDATETIME"]=pd.to_datetime(option_df["TIMESTAMP"],unit='s')
    final_data = option_df[
    (option_df["STRIKE PRICE"] == tred_sp)&
    (option_df["EXDATETIME"] >= pd.to_datetime(f"{datetime.now().strftime('%Y-%m-%d')} 10:00:00")) &
    (option_df["SIDE"] == trad_side) &
    (option_df['INDEX'] == trad_index)
    ]
    if final_data.shape[0] == 0:
        print("Somethi wrong ")
        return None
    else:
        return final_data.iloc[0].to_dict()

# get_option_for("BANKNIFTY", "PE", 48541)
