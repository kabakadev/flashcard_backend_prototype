from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import ForeignKey
import re
from config import db, bcrypt

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    _password_hash = db.Column("password_hash", db.String(255), nullable=False)

    decks = db.relationship('Deck', backref='user', cascade="all, delete-orphan")
    progress = db.relationship('Progress', backref='user', cascade="all, delete-orphan")

    serialize_rules = ('-decks.user', '-progress.user')

    @hybrid_property
    def password_hash(self):
        return self._password_hash

    @password_hash.setter
    def password_hash(self, password):
        self._password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self._password_hash, password)

    # VALIDATIONS
    @validates("email")
    def validate_email(self, key, email):
        email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_regex, email):
            raise ValueError("Invalid email format")
        return email.lower()  # Normalize to lowercase

    @validates("username")
    def validate_username(self, key, username):
        if len(username) < 3 or len(username) > 50:
            raise ValueError("Username must be between 3 and 50 characters")
        return username

class Deck(db.Model, SerializerMixin):
    __tablename__ = 'decks'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    subject = db.Column(db.String(50))
    category = db.Column(db.String(50))
    difficulty = db.Column(db.Integer)  # Range 1-5
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    flashcards = db.relationship('Flashcard', backref='deck', cascade="all, delete-orphan")

    serialize_rules = ('-user.decks', '-flashcards.deck')

class Flashcard(db.Model, SerializerMixin):
    __tablename__ = 'flashcards'

    id = db.Column(db.Integer, primary_key=True)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=False)
    front_text = db.Column(db.Text, nullable=False)
    back_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    serialize_rules = ('-deck.flashcards',)

class Progress(db.Model, SerializerMixin):
    __tablename__ = 'progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    deck_id = db.Column(db.Integer, db.ForeignKey('decks.id'), nullable=False)
    flashcard_id = db.Column(db.Integer, db.ForeignKey('flashcards.id'), nullable=False)

    study_count = db.Column(db.Integer, default=0, nullable=False)
    correct_attempts = db.Column(db.Integer, default=0, nullable=False)  # New: Tracks correct answers
    incorrect_attempts = db.Column(db.Integer, default=0, nullable=False)  # New: Tracks incorrect answers
    total_study_time = db.Column(db.Float, default=0.0)  # New: Tracks total time spent on flashcard (in minutes)
    last_studied_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    next_review_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    review_status = db.Column(db.Enum('new', 'learning', 'reviewing', 'mastered', name="review_status"))
    is_learned = db.Column(db.Boolean, default=False)

    serialize_rules = ('-user.progress', '-deck.progress')

    __table_args__ = (db.UniqueConstraint('user_id', 'flashcard_id', name='unique_user_flashcard_progress'),)

class UserStats(db.Model, SerializerMixin):
    __tablename__ = 'user_stats'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)

    weekly_goal = db.Column(db.Integer, default=0)  # Target number of flashcards per week
    mastery_level = db.Column(db.Float, default=0.0)  # % of mastered cards
    study_streak = db.Column(db.Integer, default=0)  # Days in a row studied
    focus_score = db.Column(db.Float, default=0.0)  # Engagement metric (e.g., % of uninterrupted study sessions)
    retention_rate = db.Column(db.Float, default=0.0)  # % of retained flashcards
    cards_mastered = db.Column(db.Integer, default=0)  # Number of mastered flashcards
    minutes_per_day = db.Column(db.Float, default=0.0)  # Avg. minutes studied per day
    accuracy = db.Column(db.Float, default=0.0)  # Equivalent to mastery_level

    user = db.relationship("User", backref=db.backref("stats", uselist=False, cascade="all, delete-orphan"))

    serialize_rules = ('-user.stats',)
