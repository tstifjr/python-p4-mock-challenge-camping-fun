#!/usr/bin/env python3

from models import db, Activity, Camper, Signup
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)
api = Api(app)

#### not restful
@app.route('/')
def home():
    return ''


###restful
class Campers(Resource):
    def get (self):
        return make_response([c.to_dict(rules = ('-signups',)) for c in Camper.query.all()], 200)

    def post (self):
        try:
            new_camper = Camper(name = request.get_json()['name'], age = request.get_json()['age'])
            db.session.add(new_camper)
            db.session.commit()

            return make_response(new_camper.to_dict(), 201)
        
        except ValueError as v_error:
            return make_response({'errors' : v_error.args[0]}, 400)
    
api.add_resource(Campers, '/campers')

class CamperById(Resource):
    def get(self,id):
        try:
            return make_response(Camper.query.filter_by(id=id).first().to_dict(), 200)
        except:
            return make_response({'error' : "Camper not found"}, 404)
        
    def patch(self, id):
        try:
            camper = Camper.query.filter_by(id=id).first()
            data = request.get_json()
            for attr in data:
                setattr(camper, attr, data[attr])
            db.session.commit()
            return make_response(camper.to_dict(), 202)
        except ValueError as v_error:
            return make_response({'errors' : v_error.args[0]}, 400)
        except Exception:
            return make_response({'error' : "Camper not found"}, 404)

api.add_resource(CamperById, '/campers/<int:id>')

class Activities(Resource):
    def get (self):
        return make_response([a.to_dict() for a in Activity.query.all()], 200)

api.add_resource(Activities, '/activities')

class ActivityById(Resource):
    def delete (self, id):
        try:
            db.session.delete(Activity.query.filter_by(id=id).first())
            db.session.commit()
            return make_response({}, 204)
        except:
            return make_response({"error": "Activity not found"}, 404)

api.add_resource(ActivityById, '/activities/<int:id>')

class Signups(Resource):
    def post (self):
        try:
            new_signup = Signup(camper_id = request.get_json()['camper_id'], activity_id = request.get_json()['activity_id'], time = request.get_json()['time'])
            db.session.add(new_signup)
            db.session.commit()

            return make_response(new_signup.to_dict(), 201)
        
        except ValueError as v_error:
            return make_response({'errors' : v_error.args[0]}, 400)

api.add_resource(Signups, '/signups')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
