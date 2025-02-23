from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from config import app, db, api
from models import User
import logging

logging.basicConfig(level=logging.INFO)

class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        if not username or not email or not password:
            return {"error": "Missing required fields"}, 400

        try:
            user = User(username=username, email=email)
            user.password_hash = password
            db.session.add(user)
            db.session.commit()
            return {"message": "User registered successfully"}, 201
        except IntegrityError:
            db.session.rollback()
            return {"error": "Username or email already exists"}, 409

class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            access_token = create_access_token(identity=user.id)
            return {
                "message": "Login successful",
                "token": access_token
            }, 200
        
        return {"error": "Invalid email or password"}, 401


class ProtectedUser(Resource):
    @jwt_required()
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        return {"username": user.username, "email": user.email}, 200

api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")
api.add_resource(ProtectedUser, "/user")

if __name__ == "__main__":
    app.run(debug=True)
