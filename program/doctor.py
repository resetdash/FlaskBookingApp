from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3306/doctor_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

CORS(app)

class Doctor_Class(db.Model):
    __tablename__ = 'doctor_table'

    doctor_id = db.Column(db.Integer, primary_key=True)
    doctor_name = db.Column(db.String(64), nullable=False)
    date_time = db.Column(db.DateTime, primary_key=True)
    availability = db.Column(db.Boolean, default = False)


    def __init__(self, doctor_id, doctor_name, date_time, availability):
        self.doctor_id = doctor_id
        self.doctor_name = doctor_name
        self.date_time = date_time
        self.availability = availability

    def json(self):
        return {"doctor_id": self.doctor_id, "doctor_name": self.doctor_name, "date_time": self.date_time, "availability": self.availability}

@app.route("/doctor")
def get_all():
    doctorlist = Doctor_Class.query.all()
    if len(doctorlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "doctors": [doctor.json() for doctor in doctorlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no doctors."
        }
    ), 404


@app.route("/doctor/<string:doctor_id>/<string:date_time>")
def get_doctor_availability(doctor_id,date_time):
    doctor = Doctor_Class.query.filter_by(doctor_id=doctor_id, date_time=date_time).first()
    if doctor:
        return jsonify(
            {
                "code": 200,
                "data": doctor.doctor_id,
                "Name": doctor.doctor_name, 
                "date_time": doctor.date_time,
                "availability": doctor.availability
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Doctor not found."
        }
    ), 404

@app.route("/doctor/<string:doctor_id>/<string:date_time>", methods=['PUT'])
def update_availability(doctor_id,date_time):
    try:
        doctor = Doctor_Class.query.filter_by(doctor_id=doctor_id, date_time=date_time).first()
        if doctor:
            data = request.get_json()
            print(data['availability'])
            if 'availability' in data:
                doctor.availability = data['availability']
                db.session.commit()
            return jsonify(
                {
                    "code": 200,
                    "data": doctor.json()
                }
            ), 200
        # update status
        
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "doctor": doctor_id
                },
                "message": "An error occurred while updating the availability. " + str(e)
            }
        ), 500

#find all the timeslots where there is a doctor available
@app.route("/doctor/availabletimes", methods=['GET'])
def get_timeslots_with_available_doctors():
    doctor = Doctor_Class.query.filter_by(availability=1)

    if doctor:        
        available_timeslots_list = []

        for d in doctor:
            available_timeslot = d.date_time
            if available_timeslot not in available_timeslots_list:
                available_timeslots_list.append(available_timeslot) 
            

        return jsonify(
            {
                "code": 200,
                "data": {
                    "Available_timeslots": available_timeslots_list
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "No Available doctors."
        }
    ), 404

#find the first doctor available at a specified timeslot
@app.route("/doctor/availabledoctor", methods=['POST'])
def get_available_doctor():
    data = request.get_json()
    selected_time = data["selected_time"]

    doctor = Doctor_Class.query.filter_by(date_time=selected_time,availability=1).first()

    if doctor:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "Available doctor": doctor.json()
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "No Available doctors."
        }
    ), 404



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4848, debug=True)