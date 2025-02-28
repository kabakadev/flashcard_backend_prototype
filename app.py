from flask import request, jsonify
from flask_restful import Resource
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from config import app, db, api
from datetime import datetime, timedelta

from sqlalchemy.exc import IntegrityError
import re
from models import db, User, Deck, Progress,UserStats,Flashcard





class FlashcardResource(Resource):
    @jwt_required()
    def get(self):
        """Retrieve all flashcards for the authenticated user."""
        user_id = get_jwt_identity().get("id")
        flashcards = Flashcard.query.join(Deck).filter(Deck.user_id == user_id).all()

        if not flashcards:
            return {"message": "No flashcards found."}, 200

        return [
            {
                "id": flashcard.id,
                "deck_id": flashcard.deck_id,
                "front_text": flashcard.front_text,
                "back_text": flashcard.back_text,
                "created_at": flashcard.created_at.isoformat(),
                "updated_at": flashcard.updated_at.isoformat()
            }
            for flashcard in flashcards
        ], 200

    @jwt_required()
    def post(self):
        """Create a new flashcard for the authenticated user."""
        user_id = get_jwt_identity().get("id")
        data = request.get_json()

        required_fields = ["deck_id", "front_text", "back_text"]
        if not all(field in data and data[field] for field in required_fields):
            return {"error": "All fields are required"}, 400

        # Ensure the deck belongs to the authenticated user
        deck = Deck.query.filter_by(id=data["deck_id"], user_id=user_id).first()
        if not deck:
            return {"error": "Deck not found or does not belong to the user"}, 404

        new_flashcard = Flashcard(
            deck_id=data["deck_id"],
            front_text=data["front_text"],
            back_text=data["back_text"]
        )

        db.session.add(new_flashcard)
        db.session.commit()

        return {
            "id": new_flashcard.id,
            "deck_id": new_flashcard.deck_id,
            "front_text": new_flashcard.front_text,
            "back_text": new_flashcard.back_text,
            "created_at": new_flashcard.created_at.isoformat(),
            "updated_at": new_flashcard.updated_at.isoformat()
        }, 201
api.add_resource(FlashcardResource, "/flashcards")

class FlashcardDetailResource(Resource):
    @jwt_required()
    def put(self, id):
        """Update a flashcard by ID."""
        user_id = get_jwt_identity().get("id")
        data = request.get_json()

        flashcard = Flashcard.query.join(Deck).filter(Flashcard.id == id, Deck.user_id == user_id).first()
        if not flashcard:
            return {"error": "Flashcard not found"}, 404

        flashcard.front_text = data.get("front_text", flashcard.front_text)
        flashcard.back_text = data.get("back_text", flashcard.back_text)

        db.session.commit()

        return {
            "id": flashcard.id,
            "deck_id": flashcard.deck_id,
            "front_text": flashcard.front_text,
            "back_text": flashcard.back_text,
            "updated_at": flashcard.updated_at.isoformat()
        }, 200

    @jwt_required()
    def delete(self, id):
        """Delete a flashcard by ID."""
        user_id = get_jwt_identity().get("id")
        flashcard = Flashcard.query.join(Deck).filter(Flashcard.id == id, Deck.user_id == user_id).first()

        if not flashcard:
            return {"error": "Flashcard not found"}, 404

        db.session.delete(flashcard)
        db.session.commit()

        return {"message": "Flashcard deleted successfully"}, 200


# Add resources to Flask-RESTful API

api.add_resource(FlashcardDetailResource, "/flashcards/<int:id>")


class DecksResource(Resource):
    @jwt_required()
    def get(self):
        """Get all decks for the authenticated user."""
        user_data = get_jwt_identity()
        user_id = user_data.get("id")
        decks = Deck.query.filter_by(user_id=user_id).all()

        if not decks:
            return {"message": "You have no decks yet."}, 200

        return [
            {
                "id": deck.id,
                "title": deck.title,
                "description": deck.description,
                "subject": deck.subject,
                "category": deck.category,
                "difficulty": deck.difficulty,
                "created_at": deck.created_at.isoformat(),
                "updated_at": deck.updated_at.isoformat(),
            }
            for deck in decks
        ], 200
    @jwt_required()
    def post(self):
        """Create a new deck for the authenticated user."""
        data = request.get_json()
        user_data = get_jwt_identity()
        user_id = user_data.get("id")

        # Validate input
        required_fields = ["title", "description", "subject", "category", "difficulty"]
        if not all(field in data and data[field] for field in required_fields):
            return {"error": "All fields are required"}, 400

        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404

        # Create the new deck
        new_deck = Deck(
            title=data["title"],
            description=data["description"],
            subject=data["subject"],
            category=data["category"],
            difficulty=data["difficulty"],
            user_id=user_id
        )

        db.session.add(new_deck)
        db.session.commit()

        # Manually construct a safe JSON response
        return {
            "id": new_deck.id,
            "title": new_deck.title,
            "description": new_deck.description,
            "subject": new_deck.subject,
            "category": new_deck.category,
            "difficulty": new_deck.difficulty,
            "user_id": new_deck.user_id,
            "created_at": new_deck.created_at.isoformat(),
            "updated_at": new_deck.updated_at.isoformat()
        }, 201

api.add_resource(DecksResource, "/decks")
class DeckResource(Resource):
    @jwt_required()
    def get(self, deck_id):
        """Retrieve a single deck by ID for the authenticated user."""
        user_data = get_jwt_identity()
        user_id = user_data.get("id")

        deck = Deck.query.filter_by(id=deck_id, user_id=user_id).first()
        if not deck:
            return {"error": "Deck not found"}, 404

        return {
            "id": deck.id,
            "title": deck.title,
            "description": deck.description,
            "subject": deck.subject,
            "category": deck.category,
            "difficulty": deck.difficulty,
            "created_at": deck.created_at.isoformat(),
            "updated_at": deck.updated_at.isoformat()
        }, 200

    @jwt_required()
    def put(self, deck_id):
        """Update an existing deck."""
        user_data = get_jwt_identity()
        user_id = user_data.get("id")
        data = request.get_json()

        deck = Deck.query.filter_by(id=deck_id, user_id=user_id).first()
        if not deck:
            return {"error": "Deck not found"}, 404

        # Update deck fields if provided
        for field in ["title", "description", "subject", "category", "difficulty"]:
            if field in data:
                setattr(deck, field, data[field])

        db.session.commit()

        return {
            "id": deck.id,
            "title": deck.title,
            "description": deck.description,
            "subject": deck.subject,
            "category": deck.category,
            "difficulty": deck.difficulty,
            "updated_at": deck.updated_at.isoformat()
        }, 200

    @jwt_required()
    def delete(self, deck_id):
        """Delete an existing deck."""
        user_data = get_jwt_identity()
        user_id = user_data.get("id")

        deck = Deck.query.filter_by(id=deck_id, user_id=user_id).first()
        if not deck:
            return {"error": "Deck not found"}, 404

        db.session.delete(deck)
        db.session.commit()

        return {"message": "Deck deleted successfully"}, 200
api.add_resource(DeckResource, "/decks/<int:deck_id>")



class Dashboard(Resource):
    @jwt_required()
    def get(self):
        """
        Fetches the logged-in user's dashboard data, including:
        - Total flashcards studied
        - Most reviewed decks
        - Overall progress tracking
        - Study statistics (weekly goal, mastery level, streak, focus, retention, minutes per day)
        """
        user_data = get_jwt_identity()
        user_id = user_data.get("id")
        
        user = User.query.filter_by(id=user_id).first()
        if not user:
            return {"error": "User not found"}, 404
        
        # Fetch user's decks
        decks = Deck.query.filter_by(user_id=user_id).all()
        deck_data = []
        total_flashcards_studied = 0
        most_reviewed_deck = None
        most_reviews = 0
        
        for deck in decks:
            progress_entries = Progress.query.filter_by(deck_id=deck.id, user_id=user_id).all()
            deck_study_count = sum(entry.study_count for entry in progress_entries)
            total_flashcards_studied += deck_study_count

            # Track the most reviewed deck
            if deck_study_count > most_reviews:
                most_reviews = deck_study_count
                most_reviewed_deck = deck.title

            deck_data.append({
                "deck_id": deck.id,
                "deck_title": deck.title,
                "flashcards_studied": deck_study_count
            })
        
        # Fetch user stats
        stats = UserStats.query.filter_by(user_id=user_id).first()
        if not stats:
            stats = UserStats(user_id=user_id)
            db.session.add(stats)
            db.session.commit()
        
        # Compute mastery level (accuracy %)
        total_correct = db.session.query(db.func.sum(Progress.correct_attempts)).filter_by(user_id=user_id).scalar() or 0
        total_attempts = db.session.query(db.func.sum(Progress.study_count)).filter_by(user_id=user_id).scalar() or 1
        mastery_level = (total_correct / total_attempts) * 100 if total_attempts > 0 else 0

        # Compute retention rate
        retention_rate = mastery_level  # Retention rate is the same as mastery level in this case

        # Compute focus score
        total_study_time = db.session.query(db.func.sum(Progress.total_study_time)).filter_by(user_id=user_id).scalar() or 0
        target_time_per_flashcard = 1  # Target time in minutes per flashcard
        focus_score = 0

        if total_flashcards_studied > 0:
            average_time_per_flashcard = total_study_time / total_flashcards_studied
            focus_score = (average_time_per_flashcard / target_time_per_flashcard) * 100

        # Update user stats with calculated metrics
        stats.mastery_level = mastery_level
        stats.retention_rate = retention_rate
        stats.focus_score = focus_score
        db.session.commit()

        response_data = {
            "username": user.username,
            "total_flashcards_studied": total_flashcards_studied,
            "most_reviewed_deck": most_reviewed_deck,
            "weekly_goal": stats.weekly_goal,
            "mastery_level": mastery_level,
            "study_streak": stats.study_streak,
            "focus_score": focus_score,
            "retention_rate": retention_rate,
            "cards_mastered": stats.cards_mastered,
            "minutes_per_day": stats.minutes_per_day,
            "accuracy": mastery_level,
            "decks": deck_data
        }

        return response_data, 200
# Register the resource with Flask-RESTful
api.add_resource(Dashboard, "/dashboard")




# Email validation
def is_valid_email(email):
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(email_regex, email) is not None

# Username validation
def is_valid_username(username):
    return 3 <= len(username) <= 50

class Signup(Resource):
    def post(self):
        data = request.get_json()
        username, email, password = data.get("username"), data.get("email"), data.get("password")

        if not username or not email or not password:
            return {"error": "Missing required fields"}, 400
        if not is_valid_email(email):
            return {"error": "Invalid email format"}, 400
        if not is_valid_username(username):
            return {"error": "Username must be between 3 and 50 characters"}, 400

        try:
            user = User(username=username, email=email)
            user.password_hash = password  # Hash password
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
        email, password = data.get("email"), data.get("password")

        if not email or not password:
            return {"error": "Email and password are required"}, 400

        user = User.query.filter_by(email=email.lower()).first()
        if user and user.check_password(password):
            token = create_access_token(identity={"id": user.id, "username": user.username})
            return {"message": "Login successful", "token": token}, 200

        return {"error": "Invalid email or password"}, 401

api.add_resource(Login, "/login")

class ProtectedUser(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        return jsonify(current_user)  # Directly returning user data

api.add_resource(ProtectedUser, "/user")


class ProgressResource(Resource):
    @jwt_required()
    def get(self, deck_id=None, flashcard_id=None):
        """
        Retrieve progress for a specific deck or flashcard for the authenticated user.
        """
        user_id = get_jwt_identity().get("id")
        
        query = Progress.query.filter_by(user_id=user_id)

        if deck_id:
            query = query.filter_by(deck_id=deck_id)
        if flashcard_id:
            query = query.filter_by(flashcard_id=flashcard_id)

        progress_entries = query.all()

        if not progress_entries:
            return {"message": "No progress found."}, 200

        return [
            {
                "id": p.id,
                "deck_id": p.deck_id,
                "flashcard_id": p.flashcard_id,
                "study_count": p.study_count,
                "correct_attempts": p.correct_attempts,
                "incorrect_attempts": p.incorrect_attempts,
                "total_study_time": p.total_study_time,
                "last_studied_at": p.last_studied_at.isoformat() if p.last_studied_at else None,
                "next_review_at": p.next_review_at.isoformat() if p.next_review_at else None,
                "review_status": p.review_status,
                "is_learned": p.is_learned
            }
            for p in progress_entries
        ], 200

    @jwt_required()
    def post(self):
        """
        Track user progress for a flashcard.
        """
        user_id = get_jwt_identity().get("id")
        data = request.get_json()

        # Fetch or create progress entry
        progress = Progress.query.filter_by(
            user_id=user_id,
            flashcard_id=data["flashcard_id"],
        ).first()

        if not progress:
            progress = Progress(
                user_id=user_id,
                flashcard_id=data["flashcard_id"],
                deck_id=data["deck_id"],
                study_count=0,
                total_study_time=0,
                correct_attempts=0,
                incorrect_attempts=0,
                review_status='new',
                is_learned=False
            )
            db.session.add(progress)

        # Update progress data
        progress.study_count += 1
        progress.total_study_time += data.get("time_spent", 0)
        if data.get("was_correct"):
            progress.correct_attempts += 1
        else:
            progress.incorrect_attempts += 1

        # Update review status and mastery
        if progress.correct_attempts >= 3:  # Example: 3 correct attempts to master
            progress.review_status = "mastered"
            progress.is_learned = True

        db.session.commit()

        # Update user stats
        stats = UserStats.query.filter_by(user_id=user_id).first()
        if not stats:
            stats = UserStats(user_id=user_id)
            db.session.add(stats)

        # Recalculate metrics
        total_correct = db.session.query(db.func.sum(Progress.correct_attempts)).filter_by(user_id=user_id).scalar() or 0
        total_attempts = db.session.query(db.func.sum(Progress.study_count)).filter_by(user_id=user_id).scalar() or 1
        stats.mastery_level = round((total_correct / total_attempts) * 100, 2)  # Round to 2 decimal places

        # Update cards_mastered
        stats.cards_mastered = Progress.query.filter_by(user_id=user_id, review_status="mastered").count()

        # Update retention_rate (same as mastery_level in this case)
        stats.retention_rate = stats.mastery_level

        # Update focus_score (example calculation)
        total_study_time = db.session.query(db.func.sum(Progress.total_study_time)).filter_by(user_id=user_id).scalar() or 0
        target_time_per_flashcard = 1  # Target time in minutes per flashcard
        if total_attempts > 0:
            average_time_per_flashcard = total_study_time / total_attempts
            stats.focus_score = round((average_time_per_flashcard / target_time_per_flashcard) * 100, 2)

        db.session.commit()

        return {
            "id": progress.id,
            "user_id": progress.user_id,
            "flashcard_id": progress.flashcard_id,
            "deck_id": progress.deck_id,
            "study_count": progress.study_count,
            "correct_attempts": progress.correct_attempts,
            "incorrect_attempts": progress.incorrect_attempts,
            "total_study_time": progress.total_study_time,
            "review_status": progress.review_status,
            "is_learned": progress.is_learned,
        }, 200

# Add resource to API
api.add_resource(ProgressResource, "/progress", "/progress/<int:progress_id>", "/progress/deck/<int:deck_id>", "/progress/flashcard/<int:flashcard_id>")
class UserStatsResource(Resource):
    @jwt_required()
    def put(self):
        """Update user stats, such as weekly goal."""
        user_id = get_jwt_identity().get("id")
        data = request.get_json()

        # Fetch or create user stats
        stats = UserStats.query.filter_by(user_id=user_id).first()
        if not stats:
            stats = UserStats(user_id=user_id)
            db.session.add(stats)

        # Update weekly goal if provided
        if "weekly_goal" in data:
            stats.weekly_goal = data["weekly_goal"]

        # Update other stats if needed
        if "mastery_level" in data:
            stats.mastery_level = data["mastery_level"]
        if "study_streak" in data:
            stats.study_streak = data["study_streak"]
        if "focus_score" in data:
            stats.focus_score = data["focus_score"]
        if "retention_rate" in data:
            stats.retention_rate = data["retention_rate"]
        if "cards_mastered" in data:
            stats.cards_mastered = data["cards_mastered"]
        if "minutes_per_day" in data:
            stats.minutes_per_day = data["minutes_per_day"]
        if "accuracy" in data:
            stats.accuracy = data["accuracy"]

        db.session.commit()

        return {
            "id": stats.id,
            "user_id": stats.user_id,
            "weekly_goal": stats.weekly_goal,
            "mastery_level": stats.mastery_level,
            "study_streak": stats.study_streak,
            "focus_score": stats.focus_score,
            "retention_rate": stats.retention_rate,
            "cards_mastered": stats.cards_mastered,
            "minutes_per_day": stats.minutes_per_day,
            "accuracy": stats.accuracy,
        }, 200

# Register the resource with Flask-RESTful
api.add_resource(UserStatsResource, "/user/stats")