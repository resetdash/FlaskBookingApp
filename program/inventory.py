#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from os import environ

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3306/inventory'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

CORS(app)

class inventory(db.Model):
    __tablename__ = 'inventory'
    ItemID = db.Column(db.Integer, primary_key=True)
    ItemName = db.Column(db.String(50), nullable=False)
    ItemDescription = db.Column(db.String(300), nullable=False)
    CostPrice = db.Column(db.Float(precision=2), nullable=False)
    RetailPrice = db.Column(db.Float(precision=2), nullable=False)
    Quantity = db.Column(db.Integer)

    def __init__(self, ItemID, ItemName, ItemDescription, CostPrice, RetailPrice, Quantity):
        self.ItemID = ItemID
        self.ItemName = ItemName
        self.ItemDescription = ItemDescription
        self.CostPrice = CostPrice
        self.RetailPrice = RetailPrice
        self.Quantity = Quantity

    def json(self):
        return {"ItemID": self.ItemID, "ItemName": self.ItemName, "ItemDescription": self.ItemDescription, 
        "CostPrice": self.CostPrice, "RetailPrice": self.RetailPrice, "Quantity": self.Quantity}


@app.route("/inventory")
def get_all():
    inven_list = inventory.query.all()
    if len(inven_list):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "items": [items.json() for items in inven_list]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no items."
        }
    ), 404


@app.route("/inventory/<string:ItemID>")
def find_by_ItemID(ItemID):
    item = inventory.query.filter_by(ItemID=ItemID).first()
    if item:
        return jsonify(
            {
                "code": 200,
                "data": item.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Item not found."
        }
    ), 404

@app.route("/inventory/price", methods=['POST'])
def get_prices():
    inven_list = inventory.query.all()

    if len(inven_list):
        data = request.get_json()
        output = []
        total = 0.0

        for i in range(0, len(data["Prescription"])):
            for items in data["Prescription"][i]:
                if items == "ItemID":
                    ItemID = data["Prescription"][i][items]
                    try:
                        output.append(
                            jsonify(
                                {
                                    "ItemID": data["Prescription"][i][items], 
                                    "RetailPrice": inven_list[ItemID - 1].RetailPrice,
                                    "Quantity": data["Prescription"][i]["Quantity"] 
                                }
                                )
                            )
                        total += inven_list[ItemID - 1].RetailPrice * data["Prescription"][i]["Quantity"] 

                    except:
                        output.append(
                            jsonify(
                                {
                                    "ItemID": fields[items], 
                                    "RetailPrice": None}
                                )
                            )

        return jsonify(
            {
                "code": 200,
                "data": {
                    "items": [items.json for items in output],
                    "total" : total
                }
            }
        )

    return jsonify(
        {
            "code": 404,
            "message": "Item not found."
        }
    ), 404


@app.route("/inventory/<string:ItemID>", methods=['POST'])
def create_item(ItemID):
    if (inventory.query.filter_by(ItemID=ItemID).first()):
        return jsonify(
            {
                "code": 400,
                "data": {
                    "ItemID": ItemID
                },
                "message": "Item already exists."
            }
        ), 400

    data = request.get_json()
    item = inventory(**data)

    try:
        db.session.add(item)
        db.session.commit()
    except:
        db.session.rollback()
        return jsonify(
            {
                "code": 500,
                "data": {
                    "ItemID": ItemID
                },
                "message": "An error occurred creating the item."
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": item.json()
        }
    ), 201


@app.route("/inventory/", methods=['PUT'])
def update_stock():
    inven_list = inventory.query.all()

    if len(inven_list):
        data = request.get_json()
        try:
            for fields in data["Prescription"]:
                for items in fields:
                    if items == "ItemID":
                        id = fields[items] - 1
                        inven_list[id].Quantity = inven_list[id].Quantity - fields["Quantity"]
            db.session.commit()
            return jsonify(
                {
                    "code": 200,
                    "message": "Inventory updated successfully"
                }
            )
        except Exception as error:
            db.session.rollback()
            return jsonify(
            {
                "code": 500,
                "data": data,
                "message": "An error occurred updating the inventory."
            }
        ), 500
            
    return jsonify(
        {
            "code": 404,
            "message": "Item not found."
        }
    ), 404

@app.route("/inventory/item/<string:ItemID>", methods=['PUT'])
def update_item(ItemID):
    item = inventory.query.filter_by(ItemID=ItemID).first()
    if item:
        data = request.get_json()
 
        #for fields in data:

        if 'ItemName' in data:
            item.ItemName = data['ItemName']
        if 'ItemDescription' in data:
            item.ItemDescription = data['ItemDescription']
        if 'CostPrice' in data:
            item.CostPrice = data['CostPrice']
        if 'RetailPrice' in data:
            item.RetailPrice = data['RetailPrice']
        if 'Quantity' in data:
            item.Quantity = data['Quantity']  

        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": item.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "ItemID": ItemID
            },
            "message": "Item not found."
        }
    ), 404

@app.route("/inventory/<string:ItemID>", methods=['DELETE'])
def delete_item(ItemID):
    item = inventory.query.filter_by(ItemID=ItemID).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": {
                    "ItemID": ItemID
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "ItemID": ItemID
            },
            "message": "Item not found."
        }
    ), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5010, debug=True)
