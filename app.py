from flask import Flask, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager
from resources.user import UserRegister,User, Userlogin, TokenRefresh, Logout
from resources.item import Item, ItemList
from resources.store import Store, StoreList
from blacklist import Blacklist

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['PROPAGATE_EXCEPTIONS'] = True
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = {'access', 'refresh'}

app.secret_key = 'secret'
api = Api(app)

jwt = JWTManager(app) 

@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    return decrypted_token['jti'] in Blacklist


@jwt.user_claims_loader
def add_claims_to_jwt(identity):
    if identity == 1:
        return {'is_admin':True}
    return {'is_admin':False}

@jwt.expired_token_loader
def expired_token_callback():
    return jsonify({"message":"The token has expired"}),401

@jwt.invalid_token_loader
def invalid_token_callback():
    return jsonify({"message":"The token is not valid"}),401

@jwt.unauthorized_loader
def unauthorized_callback():
    return jsonify({"message":"No token is provided"}),401

    
@jwt.needs_fresh_token_loader
def needs_fresh_token_callback():
    return jsonify({"message":"The token is not fresh"}),401
    
@jwt.revoked_token_loader
def revoked_token_callback():
    return jsonify({"message":"The token has been revoked"}),401

api.add_resource(ItemList, '/items')
api.add_resource(Item, '/item/<string:name>')
api.add_resource(UserRegister, '/register')
api.add_resource(Store, '/store/<string:name>')
api.add_resource(StoreList, '/stores')
api.add_resource(User, '/user/<int:user_id>')
api.add_resource(Userlogin, '/login')
api.add_resource(TokenRefresh, '/refresh')
api.add_resource(Logout, '/logout')

if __name__ == '__main__':
    app.run(port=5000, debug=True)
