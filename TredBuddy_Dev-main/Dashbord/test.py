from pymongo import MongoClient
from datetime import datetime, date, timedelta
import pandas as pd
client = MongoClient("mongodb+srv://justj:justj@cluster0.fsgzjrl.mongodb.net/")
db = client['TredBuddy2']
db_positions = db['Positions']




data = list(db_positions.find({}))

data = [{**record, 'BUY DATETIME': datetime.strptime(record['BUY DATETIME'], '%m/%d/%Y %I:%M %p')} for record in data]
selected_time = pd.Timestamp.now().normalize() - pd.Timedelta(days=1)
df = pd.DataFrame(data)
filter_data = df[df['BUY DATETIME'].dt.date == selected_time.date()]

open_positions = df[(df['BUY DATETIME'].dt.date == selected_time.date()) & (df['STATUS'] == "OPEN")]

print(open_positions)
