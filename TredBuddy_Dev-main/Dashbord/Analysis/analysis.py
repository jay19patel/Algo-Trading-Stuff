



from pymongo import MongoClient
from datetime import datetime, date, timedelta
import pandas as pd
client = MongoClient("mongodb+srv://justj:justj@cluster0.fsgzjrl.mongodb.net/")
db = client['TredBuddy']
db_positions = db['Positions']
db_profile = db["Profile"]


def DayAnalysis(state):
    if state == "DAY":
        data = list(db_positions.find({"DATE":str(date.today())}))
    else:
        data = list(db_positions.find({}))
    alldf = pd.DataFrame(data)
    alldf = round(alldf,2)
    account_balance = db_profile.find_one({"Account":"001"}).get("Balance")
    output = []
    profitable_trades = 0
    loss_trades = 0
    win_ratio = 0
    today_grow = 0
    # df = round(df,2)
    # df = alldf[alldf["STATUS"] == "CLOSE"]
    # df = 

    if len(alldf)!=0:
        df = alldf[alldf["STATUS"] == "CLOSE"]
        total_treds =  alldf.shape[0]
        total_open_list = alldf[alldf["STATUS"] == "OPEN"]
        total_close_list = alldf[alldf["STATUS"] == "CLOSE"]
        total_open = total_open_list.shape[0]
        total_close = total_close_list.shape[0]
        # 1111111111111111111
        gdf = df.groupby(['INDEX', 'SIDE', 'PnL Status']).size().reset_index(name='Total Trades')
        pivot_df = gdf.pivot_table(index='INDEX', columns=['SIDE', 'PnL Status'], values='Total Trades', aggfunc='sum', fill_value=0)
        pivot_df.columns = ['_'.join(col) for col in pivot_df.columns.values]
        pivot_df['Total_Tred'] = pivot_df.sum(axis=1)
        pivot_df.reset_index(inplace=True)

        # 222222222222222222222
        gdff = df.groupby(['INDEX', 'SIDE', 'PnL Status'])['PnL GROW'].sum().reset_index(name='Total PnL Grow')
        pivot_dff = gdff.pivot_table(index='INDEX', columns=['SIDE', 'PnL Status'], values='Total PnL Grow', aggfunc='sum', fill_value=0)
        pivot_dff.columns = ['_Amount_'.join(col) for col in pivot_dff.columns.values]
        pivot_dff['Total_Tred_Amount'] = pivot_dff.sum(axis=1)
        
        # merge 

        merged_df = pd.merge(pivot_df, pivot_dff, on='INDEX', how='outer').fillna(0)
        columns_to_add = ['CE_Loss', 'PE_Loss', 'PE_Profit', 'CE_Profit', 'CE_Amount_Loss', 'PE_Amount_Loss', 'PE_Amount_Profit', 'CE_Amount_Profit']
        merged_df = merged_df.reindex(columns=merged_df.columns.union(columns_to_add), fill_value=0)
        merged_df['Total_Tred'] = merged_df[['CE_Loss', 'PE_Loss', 'PE_Profit', 'CE_Profit']].sum(axis=1)
        merged_df['Total_Tred_Amount'] = merged_df[['CE_Amount_Loss', 'PE_Amount_Loss', 'PE_Amount_Profit', 'CE_Amount_Profit']].sum(axis=1)

        # Calculate total row and append it to DataFrame
        total_row = merged_df.sum(numeric_only=True)
        total_row['INDEX'] = 'Over All'
        total_df = pd.DataFrame([total_row])
        output = pd.concat([merged_df, total_df], ignore_index=True).to_dict('records')

        # Calculate additional metrics
        profitable_trades = len(df[df['PnL Status'] == 'Profit'])
        loss_trades = len(df[df['PnL Status'] == 'Loss'])
        total_treds = total_row['Total_Tred']
        win_ratio = (profitable_trades / total_treds) * 100
        today_grow = total_close_list["PnL GROW"].sum()
        
    # return output
    
        return {"AllTred":output,
                    "OpenTreds":total_open_list.to_dict("records"),
                    "CloseTred":total_close_list.to_dict("records"),
                    "total_treds":total_treds,"total_open":total_open,
                    "total_close":total_close,"win_ratio":round(win_ratio,2),
                    "today_grow":today_grow,
                    "account_balance":account_balance,
                    "profitable_trades":profitable_trades,
                    "loss_trades":loss_trades}
    return {"AllTred":[],
        "OpenTreds":[],
        "CloseTred":[],
        "total_treds":0,"total_open":0,
        "total_close":0,"win_ratio":0,
        "today_grow":0,
        "account_balance":account_balance,
        "profitable_trades":0,
        "loss_trades":0}
    