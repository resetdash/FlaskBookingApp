from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('dbURL') or 'mysql+mysqlconnector://root@localhost:3306/patient_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

CORS(app)

class Patient(db.Model):
    __tablename__ = 'patient_table'

    patient_id = db.Column(db.Integer, primary_key=True)
    patient_name = db.Column(db.String(64), nullable=False)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(255))

    def __init__(self, patient_id, name, username, email):
        self.patient_id = patient_id
        self.patient_name = patient_name
        self.username = username
        self.email = email

    def json(self):
        return {"patient_id": self.patient_id, "patient_name": self.patient_name, "username": self.username, "email":self.email}

@app.route("/patient/<string:username>")
def find_by_username(username):
    patient = Patient.query.filter_by(username=username).first()
    if patient:
        return jsonify(
            {
                "code": 200,
                "data": patient.patient_id
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Patient not found."
        }
    ), 404

@app.route("/patient/email/<string:patient_id>")
def get_patient_email(patient_id):
    patient = Patient.query.filter_by(patient_id=patient_id).first()
    if patient:
        return jsonify(
            {
                "code": 200,
                "data": {
                    "email": patient.email
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "Patient not found."
        }
    ), 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3737, debug=True)
