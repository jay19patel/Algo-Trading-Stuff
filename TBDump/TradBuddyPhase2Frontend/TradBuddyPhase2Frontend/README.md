# TradBuddy Modules
![Untitled Diagram](https://github.com/jay19patel/TradBuddy/assets/107461719/5a9a27d8-51b6-42b9-81a2-23200fc1c6b7)


# Flow of Modules
![Flow](https://github.com/jay19patel/TradBuddy/assets/107461719/3f474c5e-c226-42da-b6c9-11a455317f78)



# Important Functionalities

    - Multiple User Support (Fyers Registration)
    - Multiple Accounts (Paper Trading, Real Trading, and Adjustable Account Settings)
    - Account Management (Automatic and Manual Adjustment of Settings like Stop Loss, Target, Trailing, etc.)
    - Automated Buy and Sell Orders
    - Risk Management 
    - Day-wise Analysis
    - Comprehensive Analysis Across All Accounts
    - Strategy Building and Selection, Customized for Different Accounts
    - Backtesting Capabilities
    - Each Component is Independent, Allowing for Individual Code Updates and Process Changes



# Function List

## TradBuddyBroker Class

### Methods
1. `profile_create`: Creates a new user profile.
2. `profile_login`: Authenticates a user profile.
3. `profile_get`: Retrieves the profile information of the authenticated user.
4. `account_create`: Creates a new trading account.
5. `account_update`: Updates the details of a trading account.
6. `account_get`: Retrieves the details of a specific trading account.
7. `account_list`: Lists all trading accounts associated with the authenticated user.
8. `account_delete`: Deletes a trading account.
9. `account_transaction_create`: Performs a transaction (deposit/withdrawal) for a trading account.
10. `account_transaction_view`: Retrieves the transaction history of a trading account.
11. `order_place`: Places a new order for trading.
12. `order_close`: Closes a specific order.
13. `order_book`: Retrieves the order book for a trading account.
14. `generate_report`: Generates a trading report for a trading account.
15. `perform_analysis`: Performs analysis on trading data for a specific account.

### Middleware
- `check_authentication`: Middleware function to check user authentication status before accessing certain methods.

### Custom Imports
- `pandas as pd`
- `generate_password_hash, check_password_hash` from `werkzeug.security`
- Custom imports from `DB.Connection` and `Utility.Generator`






# Important Modules for API Generation

    - flask 
    - flask_restful 
    - flask_jwt_extended 
    - cryptography.fernet
    - flask_login 
    - flask_bcrypt 
    - werkzeug.security


```py
# BASE FLASK SETUP 

from flask import Flask, request  # Flask: Web application framework for creating web applications
from flask_restful import Api, Resource, reqparse  # Flask-RESTful: Extension for building REST APIs
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity  # Flask-JWT-Extended: Extension for JSON Web Tokens (JWT) support
from flask_login import LoginManager, UserMixin, login_user, logout_user  # Flask-Login: Extension for managing user authentication
from flask_bcrypt import Bcrypt  # Flask-Bcrypt: Extension for password hashing
from cryptography.fernet import Fernet  # cryptography.fernet: Library for data encryption
from pymongo import MongoClient  # pymongo: Library for MongoDB database interaction

app = Flask(__name__)  # Flask application instance

# JWT Configuration
app.config['JWT_SECRET_KEY'] = 'your_secret_key_here'  # Secret key for JWT token encoding and decoding
jwt = JWTManager(app)  # JWTManager instance for managing JWT tokens

# Flask-Login Configuration
login_manager = LoginManager()  # LoginManager instance for managing user authentication with Flask-Login
login_manager.init_app(app)  # Initialize Flask-Login with the Flask app

# Bcrypt Initialization
bcrypt = Bcrypt(app)  # Bcrypt instance for password hashing with Flask-Bcrypt

# MongoDB Configuration
client = MongoClient('mongodb://localhost:27017/')  # Connect to MongoDB server
db = client['your_database_name_here']  # Select database
collection = db['your_collection_name_here']  # Select collection

# Fernet Encryption Key
key = Fernet.generate_key()  # Generate encryption key
cipher_suite = Fernet(key)  # Fernet instance for data encryption

# User Class for Flask-Login
class User(UserMixin):  # User class for managing user objects with Flask-Login
    def __init__(self, username):
        self.username = username

@login_manager.user_loader
def load_user(user_id):  # User loader function for loading user objects from the database
    return User(user_id)

# Register Resource
class Register(Resource):  # Register resource for handling user registration
    def post(self):  # POST method for registering a new user
        parser = reqparse.RequestParser()  # RequestParser instance for parsing request data
        parser.add_argument('username', type=str, required=True, help='Username is required')  # Parse username from request
        parser.add_argument('password', type=str, required=True, help='Password is required')  # Parse password from request
        data = parser.parse_args()
        username = data['username']
        password = data['password']

        # Encrypt the password
        encrypted_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Store the encrypted data in the database
        encrypted_data = cipher_suite.encrypt(f"{username},{encrypted_password}".encode())
        collection.insert_one({'_id': username, 'data': encrypted_data})

        return {'message': 'User registered successfully'}, 201

# Login Resource
class Login(Resource):  # Login resource for handling user login
    def post(self):  # POST method for user login
        parser = reqparse.RequestParser()  # RequestParser instance for parsing request data
        parser.add_argument('username', type=str, required=True, help='Username is required')  # Parse username from request
        parser.add_argument('password', type=str, required=True, help='Password is required')  # Parse password from request
        data = parser.parse_args()
        username = data['username']
        password = data['password']

        # Get the encrypted data from the database
        encrypted_data = collection.find_one({'_id': username})
        if not encrypted_data:
            return {'message': 'User not found'}, 404

        # Decrypt the data and check the password
        decrypted_data = cipher_suite.decrypt(encrypted_data['data']).decode().split(',')
        stored_password = decrypted_data[1]
        if not bcrypt.check_password_hash(stored_password, password):
            return {'message': 'Invalid password'}, 401

        # Login the user using Flask-Login
        user = User(username)
        login_user(user)

        # Generate JWT token
        access_token = create_access_token(identity=username)
        return {'access_token': access_token}, 200

# Protected Resource
class ProtectedResource(Resource):  # Protected resource accessible only with a valid JWT token
    @jwt_required()  # Decorator to protect the resource with JWT
    def get(self):  # GET method for accessing the protected resource
        current_user = get_jwt_identity()  # Get the identity of the current user from the JWT token
        return {'message': f'You are accessing protected resource as {current_user}'}, 200

# Add resources to the API
api.add_resource(Register, '/register')  # Register endpoint for user registration
api.add_resource(Login, '/login')  # Login endpoint for user login
api.add_resource(ProtectedResource, '/protected')  # Protected endpoint accessible only with a valid JWT token

if __name__ == '__main__':
    app.run(debug=True)  # Run the Flask application in debug mode

```
