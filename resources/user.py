from flask_restful import Resource, reqparse
from models.user import UserModel
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import (
    create_access_token, 
    create_refresh_token,
    jwt_refresh_token_required,
    jwt_required,
    get_jwt_identity,
    get_raw_jwt
)

from blacklist import Blacklist

_user_parser = reqparse.RequestParser()
_user_parser.add_argument('username', type = str, required = True)
_user_parser.add_argument('password', type = str, required = True)

class UserRegister(Resource):
    def post(self):
        data = _user_parser.parse_args()
        if UserModel.find_by_username(data['username']):
            return {"message":"the user already exists"}
        user  = UserModel(**data)
        user.save_to_db()
        return {"message":"new user created successfully", 'data': [user.json()]},201

class User(Resource):

    @classmethod
    def get(self, user_id):
        user = UserModel.find_by_id(user_id)
        if user is None:
            return {"message": "No such username"},404
        else:
            return {"data":[user.json()]}

    @classmethod
    def delete(self, user_id):
        user = UserModel.find_by_id(user_id)
        if user:
            user.delete_from_db()
            return {"message":"successfully deleted user"}
        else:
            return {"message":"No such user found"}
        
    

class Userlogin(Resource):
    @classmethod
    def post(cls):
        data = _user_parser.parse_args()
        user = UserModel.find_by_username(data['username'])
        if user and safe_str_cmp(user.password, data['password']):
            access_token = create_access_token(identity = user.id, fresh = True)
            refresh_token = create_refresh_token(user.id)
            return {
                "STATUS":"LOGIN SUCCESSFUL",
                "access_token": access_token,
                "refresh_token":refresh_token
            },200
        else :
            return {"message": "invalid creddentials"},401

class Logout(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        Blacklist.add(jti)

class TokenRefresh(Resource):

    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        new_token  = create_access_token(identity= current_user, fresh = False)
        return {'access_token':new_token}
        
