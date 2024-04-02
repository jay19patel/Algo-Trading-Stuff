
from flask import session,jsonify

def auth_required(f):
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return jsonify({'message': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function