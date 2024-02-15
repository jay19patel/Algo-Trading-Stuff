
from flask import Flask, render_template , redirect,url_for,request
import pandas as pd
from pymongo import MongoClient
from Main import Backtesting

client = MongoClient('mongodb+srv://justj:justj@cluster0.fsgzjrl.mongodb.net/')

db = client['TredBuddy']
db_orders = db['Orders']
db_positions = db['Positions']


app = Flask(__name__)

def homepagedata():
    Execute_order = db_orders.count_documents({'EXECUTION STATUS': 'Executed'})
    Open_Positions = db_positions.count_documents({'STATUS': 'Running'})
    Closed_Positions = db_positions.count_documents({'EXECUTION STATUS': "SL Hit"})
    algo_capital = sum([int(document['PnL GROW']) for document in db_positions.find({})])
    Points = sum([int(document['POINTS']) for document in db_positions.find({})])
    positions_list = [document for document in db_positions.find({'STATUS': 'Running'})]
    return {"Execute_order":Execute_order,"Open_Positions":Open_Positions,"Closed_Positions":Closed_Positions,"algo_capital":algo_capital,"Points":Points,"positions_list":positions_list}



#  ----------------- PAGE TRIGGER -----------------------
@app.route('/')
def Home():
    context = homepagedata()
    return render_template('Home.html',context=context)

@app.route('/Tred_Setup')
def Tred_Setup():
    return render_template('Tred_Setup.html')


@app.route('/Positions')
def Positions():
    positions_list = db_positions.find({})
    return render_template('Positions.html',data=positions_list )

@app.route('/Backtest' , methods=['GET','POST'])
def Backtest():
    states = None
    dflogs = None
    if request.method == "POST":
        select_index = request.form['select_index']
        select_timeframe = request.form['select_timeframe']
        days = request.form['days']
        fyers_acess_token = request.form['accesstoken']
        states,dflogs = Backtesting(fyers_acess_token, select_index, select_timeframe, days)

    return render_template('Backtest.html', states=states,logs=dflogs)

#  -----------------  LOGICAL FUNCTION -----------------------
import time

def generate_id():
    timestamp = int(time.time() * 1000)
    additional_info = "EXECUTION" 
    new_id = f"{timestamp}_{additional_info}"
    return new_id


@app.route('/Store_Tred_Setup' , methods=['POST'])
def Store_Tred_Setup():
    select_index = request.form['select_index']
    select_type = request.form['select_type']
    select_method = request.form['select_method']
    strick_price = request.form['strick_price']
    select_timeframe = request.form['select_timeframe']
    notes = request.form['notes']

    new_row = {     'EXECUTION ID': generate_id(),
                    'INDEX': select_index,
                    'SIDE':select_type,
                    "CONDITION":select_method,
                    "PRICE":strick_price,
                    "TIMEFRAME":select_timeframe,
                    "EXECUTION STATUS" :"Pending",
                    "NOTES":notes
                    } 
    db_orders.insert_one(new_row)
    return redirect(url_for('Tred_Setup'))




if __name__ == '__main__':
    app.run(debug=True)
