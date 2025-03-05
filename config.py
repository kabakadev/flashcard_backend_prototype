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
# Default decks template
DEFAULT_DECKS_TEMPLATE = [
    {
        "title": "Default Deck 1",
        "description": "This is a default deck",
        "subject": "General",
        "category": "Default",
        "difficulty": 1,
        "flashcards": [
            {"front_text": "What is 2 + 2?", "back_text": "4"},
            {"front_text": "What is the capital of France?", "back_text": "Paris"}
        ]
    },
    {
        "title": "Default Deck 2",
        "description": "This is another default deck",
        "subject": "General",
        "category": "Default",
        "difficulty": 2,
        "flashcards": [
            {"front_text": "What is 3 * 3?", "back_text": "9"},
            {"front_text": "What is the largest planet?", "back_text": "Jupiter"}
        ]
    }
]

