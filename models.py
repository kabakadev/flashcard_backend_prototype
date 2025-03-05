from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import ForeignKey
import re
from config import db, bcrypt
# Association table for many-to-many relationship between users and default decks
user_default_decks = db.Table(
    'user_default_decks',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('default_deck_id', db.Integer, db.ForeignKey('default_decks.id'), primary_key=True)
)
class DefaultDeck(db.Model, SerializerMixin):
    __tablename__ = 'default_decks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    subject = db.Column(db.String(50))
    category = db.Column(db.String(50))
    difficulty = db.Column(db.Integer)  # Range 1-5
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    flashcards = db.relationship('DefaultFlashcard', backref='default_deck', cascade="all, delete-orphan")

    serialize_rules = ('-flashcards.default_deck',)

class DefaultFlashcard(db.Model, SerializerMixin):
    __tablename__ = 'default_flashcards'

    id = db.Column(db.Integer, primary_key=True)
    default_deck_id = db.Column(db.Integer, db.ForeignKey('default_decks.id'), nullable=False)
    front_text = db.Column(db.Text, nullable=False)
    back_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    serialize_rules = ('-default_deck.flashcards',)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    _password_hash = db.Column("password_hash", db.String(255), nullable=False)

    decks = db.relationship('Deck', backref='user', cascade="all, delete-orphan")
    default_decks = db.relationship('DefaultDeck', secondary=user_default_decks, backref='users')
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
    is_default = db.Column(db.Boolean, default=False, nullable=False, server_default='0')
    
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

    # Fields with default values to ensure they are never None
    study_count = db.Column(db.Integer, default=0, nullable=False)
    correct_attempts = db.Column(db.Integer, default=0, nullable=False)  # Tracks correct answers
    incorrect_attempts = db.Column(db.Integer, default=0, nullable=False)  # Tracks incorrect answers
    total_study_time = db.Column(db.Float, default=0.0, nullable=False)  # Tracks total time spent on flashcard (in minutes)

    # Timestamps
    last_studied_at = db.Column(db.DateTime, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    next_review_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    # Review status and learning status
    review_status = db.Column(db.Enum('new', 'learning', 'reviewing', 'mastered', name="review_status"), default='new', nullable=False)
    is_learned = db.Column(db.Boolean, default=False, nullable=False)

    # Serialization rules
    serialize_rules = ('-user.progress', '-deck.progress')

    # Unique constraint to ensure one progress entry per user-flashcard pair
    __table_args__ = (db.UniqueConstraint('user_id', 'flashcard_id', name='unique_user_flashcard_progress'),)

    def __init__(self, user_id, deck_id, flashcard_id, study_count=0, correct_attempts=0, incorrect_attempts=0, total_study_time=0.0, review_status='new', is_learned=False):
        """
        Constructor to ensure all fields are initialized with default values.
        """
        self.user_id = user_id
        self.deck_id = deck_id
        self.flashcard_id = flashcard_id
        self.study_count = study_count
        self.correct_attempts = correct_attempts
        self.incorrect_attempts = incorrect_attempts
        self.total_study_time = total_study_time
        self.review_status = review_status
        self.is_learned = is_learned
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
