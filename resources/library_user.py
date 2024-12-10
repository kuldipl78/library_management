from flask_restful import Resource
from flask import request
from flask_jwt_extended import jwt_required

class LibraryUserResource(Resource):
    @jwt_required()
    def get(self):
        # Handle fetching books
        pass
