from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

from flask_caching import Cache

import os, sys
from os import environ

import requests
from invokes import invoke_http

import amqp_setup
import pika
import json

config = {
    "DEBUG": True,          # some Flask specific configs
    "CACHE_TYPE": "SimpleCache",  # Flask-Caching related configs
    "CACHE_DEFAULT_TIMEOUT": 3600
}

app = Flask(__name__)
CORS(app)

app.config.from_mapping(config)
cache = Cache(app)

booking_URL = environ.get('booking_URL') or "http://localhost:5000/booking"
inventory_URL = environ.get('inventory_URL') or "http://localhost:5010/inventory"
patient_URL = environ.get('patient_URL') or "http://localhost:3737/patient"
doctor_URL = environ.get('doctor_URL') or "http://localhost:4848/doctor"

#invoke db patient microsvc to get patient id
@app.route("/booking_manager/patient_id/<string:username>", methods=['GET'])
def get_patient_id(username):
    patient_id_URL = patient_URL + "/" + username
    patient_id = invoke_http(patient_id_URL, method='GET')["data"]

    if patient_id:
        print("\nReceived a request to get patient id:", username)
        return str(patient_id)

#scenario 1
@app.route("/booking_manager", methods=['POST'])
def create_booking():
    # Simple check of input format and data of the request are JSON
    if request.is_json:
        try:
            data = request.get_json()
            print("\nReceived a booking request:", data)

            result = processBookingCreation(data)
            return jsonify(result), result["code"]

        except Exception as e:
            pass  # do nothing.

    # if reached here, not a JSON request.
    return jsonify({
        "code": 400,
        "message": "Invalid JSON input: " + str(request.get_data())
    }), 400

def processBookingCreation(data):
    username = data["username"]
    selected_time = data["selected_time"]

    selected_time_dict = {
        "selected_time":selected_time
    }

    doctor_id_URL = doctor_URL + "/availabledoctor"
    print('\n-----Invoking doctor microservice to get doctor_id-----')
    doctor_id = invoke_http(doctor_id_URL, method='POST', json=selected_time_dict)["data"]["Available doctor"]["doctor_id"]
    print('\nobtained doctor id:', doctor_id)


    patient_id_URL = patient_URL + "/" + username
    print('\n-----Invoking patient microservice-----')    
    patient_id = invoke_http(patient_id_URL, method='GET')["data"]
    print('\nobtained patient id:', patient_id)

    doc_update = {        
        "availability" : 0
    }        
    
    #wtf = doctor_URL + "/" + doctor_id 

    #update doctor availability
    print('\n-----Invoking doctor microservice to update-----')
    # print(type(doctor_id))
    doctor_update_URL = doctor_URL + "/" + str(doctor_id) + "/" + selected_time
    # print(doctor_update_URL)
    updated_doctor_availability = invoke_http(doctor_update_URL, method='PUT', json=doc_update)
    print("updated doctor's availability:", updated_doctor_availability)

    new_booking_feed = {
        "patient_id" : patient_id,
        "doctor_id" : doctor_id,
        "consultation_date" : selected_time
    }

    #Create new booking record
    print('\n\n-----Invoking booking microservice-----')
    booking_details = invoke_http(booking_URL, method="POST", json=new_booking_feed)
    print("\nNew booking created:", booking_details)

    return {
        "code": 201,
        "data": {
            "booking_details": booking_details
        }
    }


#scenario 2
#Patient request cancel
@app.route("/booking_manager/request_cancel/<string:booking_id>", methods=['GET'])
def request_cancel_booking(booking_id):
    booking_data_URL = booking_URL + "/unpaid_booking/" + booking_id
    booking_data = invoke_http(booking_data_URL, method='GET')

    if booking_data:
        print("\nReceived a request to cancel booking:", booking_data)
        print("\nNow waiting for confirmation to cancel")
        return jsonify(booking_data)

#scenario 2
#patient confirm cancel
@app.route("/booking_manager/patient_confirm_cancel/<string:booking_id>", methods=['GET'])
def patient_confirm_cancel_booking(booking_id):

    print("\nReceived confirmation to cancel booking:", booking_id)
    print('\n\n-----Invoking booking microservice-----')
    booking_cancel_json ={
        "payment_status" : "CANCELED"
    }

    booking_update_URL = booking_URL + "/updatepay/" + booking_id
    booking_updated_reply = invoke_http(booking_update_URL, method='PUT', json=booking_cancel_json)
    print("Canceled booking:", booking_updated_reply)

    if booking_updated_reply:
        doctor_id = booking_updated_reply["data"]["doctor_id"]
        selected_time = booking_updated_reply["data"]["consultation_date"]
        actual_date_time_str = str(datetime.strptime(selected_time[:len(selected_time)-4],"%a, %d %b %Y %H:%M:%S"))

        doc_update = {        
            "availability" : 1
        }

        print('\n-----Invoking doctor microservice to update-----')
        print(actual_date_time_str)
        print("Type is:", type(actual_date_time_str))
        # print(datetime.strptime(selected_time[:len(selected_time)-4],"%a, %d %b %Y %H:%M:%S"))
        doctor_update_URL = doctor_URL + "/" + str(doctor_id) + "/" + actual_date_time_str
        updated_doctor_availability = invoke_http(doctor_update_URL, method='PUT', json=doc_update)
        print("updated doctor's availability:", updated_doctor_availability)

        if updated_doctor_availability:
            message = "Booking id " + booking_id + " has been successfully canceled."
            print('\n------------------------')
            print('\nCancellation result: ', message)
            return {
                "code": 201,
                "message": message,
                "data": {
                    "booking_result": booking_updated_reply
                }
            }

#scenario 3
#doctor request cancel
@app.route("/booking_manager/doctor_request_cancel/<string:doctor_id>", methods=['GET'])
def doctor_request_cancel_booking(doctor_id):
    booking_data_URL = booking_URL + "/unpaid/doctor/" + doctor_id
    booking_data = invoke_http(booking_data_URL, method='GET')

    if booking_data:
        print("\nReceived a request to cancel booking:", booking_data)
        print("\nNow waiting for confirmation to cancel")
        return jsonify(booking_data)

#scenario 3
#doctor confirm cancel
@app.route("/booking_manager/doctor_cancel/<string:booking_id>", methods=['GET'])
def doctor_confirm_cancel_booking(booking_id):
    try:
        print("\nReceived confirmation to cancel booking id", booking_id)
        
        result = process_doctor_cancel_booking(booking_id)
        print('\n------------------------')
        print('\nresult: ', result)
        return jsonify(result), result["code"]

    except Exception as e:
        # Unexpected error in code
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
        print(ex_str)

        return jsonify({
            "code": 500,
            "message": "booking_manager.py/doctor_cancel internal error: " + ex_str
        }), 500

def process_doctor_cancel_booking(booking_id):
    print('\n\n-----Invoking booking microservice-----')
    booking_cancel_json ={
        "payment_status" : "CANCELED"
    }

    booking_update_URL = booking_URL + "/updatepay/" + booking_id
    booking_updated_reply = invoke_http(booking_update_URL, method='PUT', json=booking_cancel_json)
    print("Canceled booking:", booking_updated_reply)

    if booking_updated_reply:
        doctor_id = booking_updated_reply["data"]["doctor_id"]
        patient_id = booking_updated_reply["data"]["patient_id"]
        selected_time = booking_updated_reply["data"]["consultation_date"]
        actual_date_time_str = str(datetime.strptime(selected_time[:len(selected_time)-4],"%a, %d %b %Y %H:%M:%S"))

        doc_update = {        
            "availability" : 1
        }

        print('\n-----Invoking doctor microservice to update-----')
        print(actual_date_time_str)
        print("Type is:", type(actual_date_time_str))
        # print(datetime.strptime(selected_time[:len(selected_time)-4],"%a, %d %b %Y %H:%M:%S"))
        doctor_update_URL = doctor_URL + "/" + str(doctor_id) + "/" + actual_date_time_str
        updated_doctor_availability = invoke_http(doctor_update_URL, method='PUT', json=doc_update)
        print("updated doctor's availability:", updated_doctor_availability)

        if updated_doctor_availability:
            print('\n-----Invoking patient microservice-----')
            patient_email_URL = patient_URL + "/email/" + str(patient_id)
            patient_email = invoke_http(patient_email_URL, method='GET')["data"]["email"]
            print(patient_email)


            if patient_email:

                code = booking_updated_reply["code"]
                message = json.dumps(booking_updated_reply)
                #jsonify("Booking id: " + booking_result['booking_id'] + " at " + booking_result['consultation_date'])
                print(message)
                if code not in range(200, 300):
                    # Inform the error microservice
                    print('\n\n-----Publishing the (booking error) message with routing_key=booking.error-----')

                    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="booking.error", 
                        body=message, properties=pika.BasicProperties(delivery_mode = 2)) 
                    # make message persistent within the matching queues until it is received by some receiver 
                    # (the matching queues have to exist and be durable and bound to the exchange)

                
                    print("\Booking status ({:d}) published to the RabbitMQ Exchange:".format(
                        code), booking_updated_reply)

                    # 7. Return error
                    return {
                        "code": 500,
                        "data": {"booking_result": booking_updated_reply},
                        "message": "Booking cancelation failure sent for error handling."
                    }

                else:

                    print('\n\n-----Publishing the (booking info) message with routing_key=cancel_booking.patient-----')
                    amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="cancel_booking.patient", 
                        body=message)
                
                print("\nBooking published to RabbitMQ Exchange.\n")
                
                message = "Booking id " + booking_id + " has been successfully canceled."
                print('\n------------------------')
                print('\nCancellation result: ', message)

                return {
                    "code": 201,
                    "message": message,
                    "data": {
                        "booking_result": booking_updated_reply
                    }
                }

#scenario 5
@app.route("/booking_manager/price/<string:booking_id>", methods=['GET'])
def get_price(booking_id):
    booking_drug_URL = booking_URL + "/" + booking_id
    inventory_price_URL = inventory_URL + "/price"
    drug_details = invoke_http(booking_drug_URL, method='GET')

    if drug_details:
        print("\nReceived a request to get drug details for this booking id:", booking_id)
        
        # drug_data = drug_details.data
        prescription_list = []

        for drug in drug_details["data"]["drug_details_table"]:
            ItemID = drug["item_id"]
            Quantity = drug["quantity"]

            prescription_list.append({"ItemID":ItemID, "Quantity":Quantity})

        prescription_dict = {"Prescription":prescription_list}        

        print(prescription_dict)
        cache.set(booking_id, prescription_dict)

        print('\n-----Invoking inventory microservice-----')
        price_result = invoke_http(inventory_price_URL, method='POST', json=prescription_dict)
        print('total:', price_result)        

        return jsonify(price_result)

#scenario 5
@app.route("/booking_manager/stock/<string:booking_id>", methods=['GET'])
def update_stock(booking_id):
    presscription = cache.get(booking_id)
    print(presscription)
    
    if presscription:
        print("\nReceived a request to update stock:", booking_id)
  

        print('\n-----Invoking inventory microservice-----')
        stock_result = invoke_http(inventory_URL+"/", method='PUT', json=presscription)
        print('stock:', stock_result)

        return jsonify(stock_result)

# Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) +
          " for placing managing a booking...")
    app.run(host="0.0.0.0", port=5727, debug=True)
    # Notes for the parameters:
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program,
    #       and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #   -- it doesn't mean to use http://0.0.0.0 to access the flask program.
