from flask import Flask, request, jsonify, session, Blueprint

from MidelWare.middelware import auth_required

public_blueprint = Blueprint('api', __name__)

@auth_required
@public_blueprint.route('/public_api', methods=['GET'])
def public_api():
    return jsonify({'message': 'This is a public API'}), 200
