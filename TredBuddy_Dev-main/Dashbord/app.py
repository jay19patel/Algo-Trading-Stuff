from flask import Flask, render_template, request, redirect, url_for, session
from datetime import timedelta
from Analysis import analysis

app = Flask(__name__)
app.secret_key = "your_secret_key"
app.permanent_session_lifetime = timedelta(minutes=60)

from pymongo import MongoClient

client = MongoClient("mongodb+srv://justj:justj@cluster0.fsgzjrl.mongodb.net/")
db = client['TredBuddy']
db_positions = db['Positions']
db_profile = db['Profile']
db_daily = db["DayilyStatus"]



@app.route('/')
def HomePage():
    if 'username' in session:
        analysis_data = analysis.DayAnalysis("DAY")
        return render_template('index.html', data=analysis_data)
    else:
        return redirect(url_for('LoginPage'))


@app.route('/login', methods=['GET', 'POST'])
def LoginPage():
    if request.method == 'POST':
        # username = request.form['username']
        password = request.form['password']
        
        if password == '123':
            session.permanent = True
            session['username'] = "Jay Patel"
            return redirect(url_for('HomePage'))
        else:
            return render_template('login.html', error='Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
def Logout():
    session.pop('username', None)
    return redirect(url_for('LoginPage'))

@app.route('/profile',methods=["GET","POST"])
def Profile():
    status = db_profile.find_one({"Account":"001"}).get("Algo Status")
    if request.method == "POST":
        formstatus = request.form["status"]
        db_profile.update_one({"Account": "001"}, {"$set": {"Algo Status": formstatus}})

        return redirect(url_for('HomePage'))

    return render_template('profile.html',status=status)


@app.route('/overview')
def overview():
    analysis_data = analysis.DayAnalysis("WEEK")
    dayilydata = list(db_daily.find({}))
    return render_template('overview.html', data=analysis_data,dayilydata =dayilydata )

@app.route('/tradsbooks')
def TradBook():
    analysis_data = analysis.DayAnalysis("WEEK")
    return render_template('All_Trads.html', data=analysis_data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
