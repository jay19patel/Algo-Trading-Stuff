from flask import Flask, request, jsonify, session, Blueprint
auth_blueprint = Blueprint('auth', __name__)


Users = {'username': "SuperAdmin", 'password': "SuperAdmin"}

@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = ( Users.get("username") == username and  Users.get("password") == password)
    if user:
        session['logged_in'] = True
        session['username'] = username
        return jsonify({'message': 'Login successful'}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401

@auth_blueprint.route('/logout')
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200
