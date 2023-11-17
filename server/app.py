#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
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

class Scientists(Resource):
    def get(self):
        scientists = [scientist.to_dict(only = ('id', 'name', 'field_of_study')) for scientist in Scientist.query.all()]
        return make_response(scientists, 200)
    def post(self):
        params = request.json
        new_scientist = Scientist(name = params['name'], field_of_study = params['field_of_study'])
        db.session.add(new_scientist)
        db.session.commit()
        return make_response(new_scientist.to_dict(), 201)
    
api.add_resource(Scientists, '/scientists')

class ScientistById(Resource):
    def get(self, id):
        scientist = Scientist.query.get(id)
        return make_response(scientist.to_dict(), 200)
    def patch(self, id):
        scientist = Scientist.query.get(id)
        if not scientist:
            return make_response({"error": "Scientist not found"}, 404)
        params = request.json
        for attr in params:
            setattr(scientist, attr, params[attr])
        db.session.commit()
        return make_response(scientist.to_dict(only = ('id', 'name', 'field_of_study')), 202)
    def delete(self, id):
        scientist = Scientist.query.get(id)
        if not scientist:
            return make_response({"error": "Scientist not found"}, 404)
        db.session.delete(scientist)
        db.session.commit()
        return make_response({}, 204)
    
api.add_resource(ScientistById, '/scientists/<int:id>')

class Planets(Resource):
    def get(self):
        planets = [planet.to_dict(only = ('id', 'name', 'distance_from_earth', 'nearest_star')) for planet in Planet.query.all()]
        return make_response(planets, 200)
    
api.add_resource(Planets, '/planets')

class Missions(Resource):
    def post(self):
        params = request.json
        new_mission = Mission(name = params['name'], scientist_id = params['scientist_id'], planet_id = params['planet_id'])
        db.session.add(new_mission)
        db.session.commit()
        return make_response(new_mission.to_dict(), 201)

api.add_resource(Missions, '/missions')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
