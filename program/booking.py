#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from datetime import datetime
from os import environ


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3306/booking_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

CORS(app)

class Booking_Class(db.Model):
    __tablename__ = 'booking_table'

    booking_id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, nullable=False)
    doctor_id = db.Column(db.Integer, nullable=False)
    consultation_date = db.Column(db.DateTime, nullable=False)
    consultation_details = db.Column(db.String(255))
    payment_status = db.Column(db.String(20), nullable=False)
    modified = db.Column(db.DateTime, nullable=False,
                         default=datetime.now, onupdate=datetime.now)
 
    def json(self):
        dto = {
            "booking_id": self.booking_id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "consultation_date":self.consultation_date,
            "consultation_details":self.consultation_details,
            "payment_status":self.payment_status,
            "modified":self.modified
            } 

        dto['drug_details_table'] = []
        for drug in self.drug_details_table:
            dto['drug_details_table'].append(drug.json())

        return dto

class Drug_Details_Class(db.Model):
    __tablename__ = 'drug_details_table'

    details_id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.ForeignKey(
        'booking_table.booking_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)

    item_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    booking_table = db.relationship(
        'Booking_Class', primaryjoin='Drug_Details_Class.booking_id == Booking_Class.booking_id', backref='drug_details_table')

    def json(self):
        return  {'details_id':self.details_id, "item_id":self.item_id, 'quantity':self.quantity, 'booking_id':self.booking_id}

@app.route("/booking/getall")
def get_all():
    allitems = Booking_Class.query.all()
    if len(allitems):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "bookings": [booking.json() for booking in allitems]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no bookings."
        }
    ), 404

@app.route("/booking/<string:booking_id>")
def find_by_booking_id(booking_id):
    booking = Booking_Class.query.filter_by(booking_id=booking_id).first()
    if booking:
        return jsonify(
            {
                "code": 200,
                "data": booking.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "booking_id": booking_id
            },            
            "message": "Booking not found."
        }
    ), 404

@app.route("/booking/doctor/<string:doctor_id>")
def find_by_doctor_id(doctor_id):
    bookings = Booking_Class.query.filter_by(doctor_id=doctor_id).all()
    if bookings:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "bookings": [booking.json() for booking in bookings]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "doctor_id": doctor_id
            },            
            "message": "Doctor not found."
        }
    ), 404

@app.route("/booking/unpaid/<string:patient_id>")
def find_unpaid_by_patient_id(patient_id):
    payment_status = "UNPAID"
    bookings = Booking_Class.query.filter_by(patient_id=patient_id, payment_status=payment_status).all()
    if bookings:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "bookings": [booking.json() for booking in bookings]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "You do not have unpaid bookings"
        }
    ), 404

@app.route("/booking/unpaid/doctor/<string:doctor_id>")
def find_unpaid_by_doctor_id(doctor_id):
    payment_status = "UNPAID"
    bookings = Booking_Class.query.filter_by(doctor_id=doctor_id, payment_status=payment_status).order_by(Booking_Class.consultation_date).all()
    if bookings:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "bookings": [booking.json() for booking in bookings]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "You do not have bookings to cancel"
        }
    ), 404

@app.route("/booking/unpaid_booking/<string:booking_id>")
def find_unpaid_by_booking_id(booking_id):
    payment_status = "UNPAID"
    bookings = Booking_Class.query.filter_by(booking_id=booking_id, payment_status=payment_status).all()

    if bookings:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "bookings": [booking.json() for booking in bookings]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "You do not have unpaid bookings"
        }
    ), 404
 
@app.route("/booking/drug/<string:booking_id>")
def get_drug_details(booking_id):
    drugs = Drug_Details_Class.query.filter_by(booking_id=booking_id).all()
    if drugs:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "DrugDetails": [drug.json() for drug in drugs]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Booking not found."
        }
    ), 404

@app.route("/booking", methods=['POST'])
def create_booking():
    patient_id = request.json.get('patient_id', None)
    doctor_id = request.json.get('doctor_id',None)
    consultation_date = request.json.get('consultation_date',None)
    
    booking = Booking_Class(patient_id=patient_id, doctor_id=doctor_id, consultation_date=consultation_date,consultation_details='Consultation yet to happen',payment_status='UNPAID')

    try:
        db.session.add(booking)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while creating the booking. " + str(e)
            }
        ), 500

    return jsonify(
        {
            "code": 201,
            "data": booking.json()
        }
    ), 201    

@app.route("/booking/drug", methods=['POST'])
def create_drug_details():
    booking_id = request.json.get('booking_id', None)
    item_id = request.json.get('item_id',None)
    quantity = request.json.get('quantity',None)
    
    exist = Drug_Details_Class.query.filter_by(booking_id=booking_id,item_id=item_id).first()

    if not exist:
        drug = Drug_Details_Class(booking_id=booking_id, item_id=item_id, quantity=quantity)

        # drugs_used = request.json.get('drugs_used')
        # for item in drugs_used:
        #     booking.drug_details_table.append(Drug_Details_Class(  
        #         item_id=item['item_id'], quantity=item['quantity']))

        try:
            db.session.add(drug)
            db.session.commit()
            return jsonify(
            {
                "code": 201,
                "data": drug.json()
            }
        ), 201
        except Exception as e:
            return jsonify(
                {
                    "code": 500,
                    "message": "An error occurred while creating the drug details. " + str(e)
                }
            ), 500
        
    else:
        try:
            exist.quantity = quantity
            db.session.commit()
            return jsonify(
            {
                "code": 201,
                "data": exist.json(),
                "message": "Prescription updated successfully"
            }
        )
        except Exception as error:
            db.session.rollback()
            return jsonify(
            {
                "code": 500,
                "data": request.get_json(),
                "message": "An error occurred updating the prescription."
            }
        ), 500
        

@app.route("/booking/updatepay/<string:booking_id>", methods=['PUT'])
def update_payment(booking_id):
    try:
        booking = Booking_Class.query.filter_by(booking_id=booking_id).first()
        if not booking:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "booking_id": booking_id
                    },
                    "message": "Booking not found."
                }
            ), 404

        # update payment_status
        data = request.get_json()
        if data['payment_status']:
            booking.payment_status = data['payment_status']
            db.session.commit()
            return jsonify(
                {
                    "code": 201,
                    "data": booking.json()
                }
            ), 200       

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "booking_id": booking_id
                },
                "message": "An error occurred while updating the booking. " + str(e)
            }
        ), 500

@app.route("/booking/updatecon/<string:booking_id>", methods=['PUT'])
def update_consultation(booking_id):
    try:
        booking = Booking_Class.query.filter_by(booking_id=booking_id).first()
        if not booking:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "booking_id": booking_id
                    },
                    "message": "Booking not found."
                }
            ), 404

        data = request.get_json()
        if data['consultation_details']:
            booking.consultation_details = data['consultation_details']
            db.session.commit()
            return jsonify(
                {
                    "code": 201,
                    "data": booking.json()
                }
            ), 200       

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "booking_id": booking_id
                },
                "message": "An error occurred while updating the booking. " + str(e)
            }
        ), 500



if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage bookings ...")
    app.run(host='0.0.0.0', port=5000, debug=True)