from flask import Flask, render_template, request, redirect, url_for, session,flash
from flask_bcrypt import Bcrypt
from cryptography.fernet import Fernet
from functools import wraps
from datetime import timedelta,datetime
from Broker.TradBuddy_Broker import TradBuddyBroker


app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'it_is_very_strong_password_123'
app.permanent_session_lifetime = timedelta(days=1)

tb_broker = TradBuddyBroker()


ENCODE_key = b'5KRuqp63vx4HevBI3cNxyH_vW7ug1LnMTKH4ahEWvh4='

def encrypt_data(data):
    cipher_suite = Fernet(ENCODE_key)
    encrypted_data = cipher_suite.encrypt(data.encode())
    return encrypted_data

def decrypt_data(encrypted_data):
    cipher_suite = Fernet(ENCODE_key)
    decrypted_data = cipher_suite.decrypt(encrypted_data)
    return decrypted_data.decode()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        profile_id = request.form['profile_id']
        profile_password = request.form['profile_password']

        is_auth = tb_broker.profile_login(profile_id=profile_id, profile_password=profile_password)
        if is_auth.get("status") == "Authenticated":
            session['username'] = is_auth["body"]
            session['profile_id'] = profile_id
            print("Success Login")
            return redirect(url_for('home'))
        else:
            flash(is_auth["message"], 'error')
            return render_template('Pages/login.html')
    
    return render_template('Pages/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        fyers_user_id = request.form['fyers_user_id']
        fyers_mobile_no = request.form['fyers_mobile_no']
        fyers_client_id = encrypt_data(request.form['fyers_client_id'])
        fyers_secret_key = encrypt_data(request.form['fyers_secret_key'])
        fyers_app_pin = encrypt_data(request.form['fyers_app_pin'])
        fyers_totp_key = encrypt_data(request.form['fyers_totp_key'])

        if not (username and password and fyers_user_id and fyers_mobile_no and fyers_client_id and fyers_secret_key and fyers_app_pin and fyers_totp_key):
            flash("All fields must be filled", 'error')
            return redirect(url_for('register'))

        data_status =  tb_broker.profile_create(username=username,
                                        password=password,
                                        fyers_user_id=fyers_user_id,
                                        fyers_mobile_no=fyers_mobile_no,
                                        fyers_client_id=fyers_client_id,
                                        fyers_secret_key=fyers_secret_key,
                                        fyers_app_pin=fyers_app_pin,
                                        fyers_totp_key=fyers_totp_key)
        if data_status["status"] == "Ok":
            return redirect(url_for('login'))
        else:
            return render_template('Pages/register.html', message='Username already exists. Please choose another.')
    return render_template('Pages/register.html')

@app.context_processor
def inject_accounts():
    list_data = tb_broker.account_list()
    if "message" in list_data:
        flash("Please Relogin","error")
        return []
    else:
        return {'accounts_list': tb_broker.account_list()}


@app.route('/')
def home():
    return render_template('Pages/home.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    session.pop('profile_id', None)
    return redirect(url_for('login'))


@app.route('/add_account' ,methods=['GET', 'POST'])
@login_required
def AddAccount():
     
    if request.method == 'POST':
        # Retrieve form data
        data = request.form
        account_balance = data.get('account_balance')
        strategy = data.get('strategy')
        max_trad = data.get('max_trade')
        description = data.get('description')
        trading_index = data.getlist('trading_index[]')
        account_activation_status = data.get('account_activation_status')
        trailing_status = data.get('trailing_status')
        payment_status = data.get('payment_status')
        today_margin = data.get('today_margin')
        today_single_trade_margin = data.get('today_single_trade_margin')
        minimum_profit = data.get('minimum_profit')
        maximum_loss = data.get('maximum_loss')
        base_stoploss = data.get('base_stoploss')
        base_target = data.get('base_target')
        base_trailing_stoploss = data.get('base_trailing_stoploss')
        base_trailing_target = data.get('base_trailing_target')

        # Call function with optimized variables
        account_status = tb_broker.account_create(
            account_balance=account_balance,
            is_activate=account_activation_status,
            trad_indexs=trading_index,
            strategy=strategy,
            max_trad_per_day=max_trad,
            todays_margin=today_margin,
            todays_trad_margin=today_single_trade_margin,
            account_min_profile=minimum_profit,
            account_max_loss=maximum_loss,
            base_stoploss=base_stoploss,
            base_target=base_target,
            trailing_status=trailing_status,
            trailing_stoploss=base_trailing_stoploss,
            trailing_target=base_trailing_target,
            payment_status=payment_status,
            description=description
        )
        flash(account_status.get("message"), 'success')

     
    return render_template('Pages/add_account.html')

@app.route('/account_setting/<account>' ,methods=['GET', 'POST'])
@login_required
def AccountSetting(account):
    if request.method == 'POST':
        data = request.form
        update_data = {
            "account_balance": data.get('strategy'),
            "is_activate":data.get('account_activation_status'),
            "trad_indexs":data.getlist('trading_index[]'),
            "strategy":data.get('strategy'),
            "max_trad_per_day":data.get('max_trade'),
            "todays_margin":data.get('today_margin'),
            "todays_trad_margin":data.get('today_single_trade_margin'),
            "account_min_profile":data.get('minimum_profit'),
            "account_max_loss":data.get('maximum_loss'),
            "base_stoploss":data.get('base_stoploss'),
            "base_target":data.get('base_target'),
            "trailing_status":data.get('trailing_status'),
            "trailing_stoploss":data.get('base_trailing_stoploss'),
            "trailing_target":data.get('base_trailing_target'),
            "payment_status": data.get('payment_status'),
            "description": data.get('description'),
            "last_updated_datetime":datetime.now()
        }
        update_status = tb_broker.account_update(account,update_data)

        flash(update_status["message"],"")
        return redirect(f"/account_setting/{account}")


        
    account_data = tb_broker.account_get(account)
    if account_data["status"] == "Ok":
        accout_details = account_data["body"]
        accout_details['last_updated_datetime'] = accout_details['last_updated_datetime'].strftime('%Y-%m-%d %H:%M:%S')
    else:
        accout_details = None

    
    return render_template('Pages/accountSetting.html',account_data=accout_details)


@app.route('/account_delete/<account>')
@login_required
def AccountDelete(account):
    delete_status = tb_broker.account_delete(account)
    flash(delete_status["message"])
    return redirect(url_for('home'))


@app.route('/account_dashbord/<account>')
@login_required
def AccountDashbord(account):

    OpenTrades = [
    {'ID': 1, 'Symbol': 'AAPL', 'Buy Price': 150.25, 'SL Price': 155.50, 'Target Price': 500, 'Buy Datetime': '2024-04-15 10:00:00', 'Sell Datetime': '2024-04-15 12:00:00', 'Qnty': 100},
    {'ID': 2, 'Symbol': 'GOOGL', 'Buy Price': 2500.75, 'SL Price': 2520.80, 'Target Price': 2000, 'Buy Datetime': '2024-04-15 11:00:00', 'Sell Datetime': '2024-04-15 13:00:00', 'Qnty': 50}
]
    CloseTrades = [
    {'ID': 3, 'Symbol': 'MSFT', 'Buy Price': 300.50, 'Sell Price': 295.25, 'PnL': -700, 'Buy Datetime': '2024-04-15 09:30:00', 'Sell Datetime': '2024-04-15 11:30:00', 'Qnty': 150},
    {'ID': 4, 'Symbol': 'AMZN', 'Buy Price': 3500.25, 'Sell Price': 3550.80, 'PnL': 3000, 'Buy Datetime': '2024-04-15 10:30:00', 'Sell Datetime': '2024-04-15 12:30:00', 'Qnty': 40}
]

    SummryData = [
            {
                "INDEX": 1,
                "CE_Profit": 100,
                "CE_Amount_Profit": 200,
                "PE_Profit": 150,
                "PE_Amount_Profit": 250,
                "CE_Loss": 50,
                "CE_Amount_Loss": 100,
                "PE_Loss": 75,
                "PE_Amount_Loss": 125,
                "Total_Tred": 200,
                "Total_Tred_Amount": 400
            },
            {
                "INDEX": 2,
                "CE_Profit": 120,
                "CE_Amount_Profit": 220,
                "PE_Profit": 160,
                "PE_Amount_Profit": 270,
                "CE_Loss": 60,
                "CE_Amount_Loss": 110,
                "PE_Loss": 80,
                "PE_Amount_Loss": 130,
                "Total_Tred": 220,
                "Total_Tred_Amount": 420
            }
        ]
    
    return render_template('Pages/accountDashbord.html',OpenTrades=OpenTrades,CloseTrades=CloseTrades,SummryData=SummryData)


@app.route('/update_trad')
@login_required
def UpdateTrad():
    updatetrad = {"name":1,"age":2}
    return render_template('Pages/UpdateTrad.html',updatetrad=updatetrad)

@app.route('/account_overview/<account>')
@login_required
def accountOverview(account):
    overviewData = []
    return render_template('Pages/accountOverview.html',overviewData=overviewData)


@app.route('/notification')
@login_required
def Notification():
    notifications = []
    return render_template('Pages/Notification.html',notifications=notifications)

@app.route('/account_tradbook/<account>')
@login_required
def AccountTradbook(account):
    tradbook = [
    {
        'Date': '2024-04-15',
        'ID': '1',
        'Symbol': 'AAPL',
        'Buy Price': '$150',
        'Sell Price': '$160',
        'PnL': -250,
        'Buy Datetime': '2024-04-01 09:00:00',
        'Sell Datetime': '2024-04-15 15:00:00',
        'Quantity': '10'
    },
    {
        'Date': '2024-04-14',
        'ID': '2',
        'Symbol': 'GOOGL',
        'Buy Price': '$2500',
        'Sell Price': '$2600',
        'PnL': 500,
        'Buy Datetime': '2024-04-01 10:00:00',
        'Sell Datetime': '2024-04-14 14:00:00',
        'Quantity': '5'
    },
    {
        'Date': '2024-04-13',
        'ID': '3',
        'Symbol': 'MSFT',
        'Buy Price': '$200',
        'Sell Price': '$220',
        'PnL': 200,
        'Buy Datetime': '2024-04-01 11:00:00',
        'Sell Datetime': '2024-04-13 13:00:00',
        'Quantity': '8'
    }
]

    return render_template('Pages/accountTradbook.html',tradbook=tradbook)



if __name__ == '__main__':
    app.run(debug=True)
    # app.run(host='0.0.0.0', port=8080,debug=True)
