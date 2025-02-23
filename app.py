from flask import request, jsonify
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from config import app, db, api
from models import User
import logging
import re
from flask_cors import cross_origin

logging.basicConfig(level=logging.INFO)

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        return '', 200  # Send an empty response with status 200



def is_valid_email(email):
    """Check if email is in a valid format."""
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, email) is not None

def is_valid_username(username):
    """Check if username length is valid."""
    return 3 <= len(username) <= 50

class Signup(Resource):
    def post(self):
        data = request.get_json()
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")

        # Check for missing fields
        if not username or not email or not password:
            return {"error": "Missing required fields"}, 400

        # Validate email format
        if not is_valid_email(email):
            return {"error": "Invalid email format"}, 400
        
        # Validate username length
        if not is_valid_username(username):
            return {"error": "Username must be between 3 and 50 characters"}, 400

        try:
            user = User(username=username, email=email)
            user.password_hash = password  # Hashes password
            db.session.add(user)
            db.session.commit()
            return {"message": "User registered successfully"}, 201
        except IntegrityError:
            db.session.rollback()
            return {"error": "Username or email already exists"}, 409
api.add_resource(Signup, "/signup")

class Login(Resource):
    def post(self):
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")

        # Check if email and password are provided
        if not email or not password:
            return {"error": "Email and password are required"}, 400

        user = User.query.filter_by(email=email.lower()).first()  # Normalize email

        if user and user.check_password(password):
            access_token = create_access_token(identity=user.id)
            return {
                "message": "Login successful",
                "token": access_token
            }, 200
        
        return {"error": "Invalid email or password"}, 401

api.add_resource(Login, "/login")

class ProtectedUser(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        user = User.query.filter_by(id=current_user).first()

        if not user:
            return jsonify({"error": "User not found"}), 404

        return jsonify({
            "id": user.id,
            "username": user.username,
            "email": user.email
        })

api.add_resource(ProtectedUser, "/user")

if __name__ == "__main__":
    app.run(debug=True)
