# app.py
from flask import Flask``
from Controller import auth,oterh
from datetime import timedelta


app = Flask(__name__)
app.config['SECRET_KEY'] = '12345678'  
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)



app.register_blueprint(auth.auth_blueprint, url_prefix='/auth')
app.register_blueprint(oterh.public_blueprint, url_prefix='/api')


if __name__ == "__main__":
    app.run(debug=True)
