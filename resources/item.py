from flask_restful import Resource, reqparse
from flask_jwt_extended import jwt_required, get_jwt_claims,jwt_optional, get_jwt_identity,fresh_jwt_required
from models.item import ItemModel

class Item(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument(
        'price', type = float, required= True, help = "This is necessary field"
    )
    parser.add_argument(
        'store_id', type = int, required= True, help = "This is necessary field"
    )

    @jwt_required
    def get(self, name):
        item = ItemModel.find_by_name(name)
        if item is not None:
            return item.json()
        else:
            return {'message':'Item not found'},404

    @fresh_jwt_required
    def post(self,name):
        item = ItemModel.find_by_name(name)
        if item is not None:
            return {"message": f"The item with {name} already exist"}, 400

        data = Item.parser.parse_args()
        newitem = ItemModel(name, **data)
        try:
            newitem.save_to_db()
        except:
            return {"message": "Error in insertion"},500

        return newitem.json(),201

    @jwt_required
    def delete(self, name):
        claims = get_jwt_claims()
        if not claims['is_admin']:
            return {"message":"Admin previlege required"}
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()
            return {"message":"item deleted"}
    
    def put(self, name):
        data = Item.parser.parse_args()
        item = ItemModel.find_by_name(name)
        if item is None:
            item = ItemModel(name, **data)
        else:
            item.price = data['price']
        item.save_to_db()
        return item.json()
        
class ItemList(Resource):
    @jwt_optional
    def get(self):
        user_id = get_jwt_identity()
        items = [item.json() for item in ItemModel.find_all()]
        print(items)
        if user_id is not None:
            return {'items':items},200
        return {
            'items' : [item['name'] for item in items],
            'userid':user_id,
            'message':"More data available login please"
        },200
