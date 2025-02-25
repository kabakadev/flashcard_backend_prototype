from flask import Flask
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os

app = Flask(__name__)
from datetime import timedelta

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=8)  # Extend to 8 hours

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashlearn.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'supersecretkey') 

jwt = JWTManager(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
api = Api(app)


CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

