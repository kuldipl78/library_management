from flask_restful import Resource
from flask import request, jsonify
from flask_jwt_extended import jwt_required

class LibrarianResource(Resource):
    @jwt_required()
    def post(self):
        # Handle creating a new user
        pass
