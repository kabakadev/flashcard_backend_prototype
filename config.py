from flask import Flask
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from sqlalchemy import MetaData
from dotenv import load_dotenv
from flask_cors import CORS
import os

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Configure database (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flashlearn.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Set up JWT authentication
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'supersecretkey')  # Change this in production
jwt = JWTManager(app)

# Initialize extensions
metadata = MetaData(naming_convention={"fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"})
db = SQLAlchemy(metadata=metadata)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
api = Api(app)

# Attach SQLAlchemy to Flask
db.init_app(app)

# Allow cross-origin requests
CORS(app, supports_credentials=True, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], origins=["*"], allow_headers=["Content-Type", "Authorization"])
