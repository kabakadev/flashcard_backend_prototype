from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import db
from models import Deck, User

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

        required_fields = ["title", "description", "subject", "category", "difficulty"]
        if not all(field in data and data[field] for field in required_fields):
            return {"error": "All fields are required"}, 400

        user = User.query.get(user_id)
        if not user:
            return {"error": "User not found"}, 404

        new_deck = Deck(
            title=data["title"],
            description=data["description"],
            subject=data["subject"],
            category=data["category"],
            difficulty=data["difficulty"],
            user_id=user_id,
        )

        db.session.add(new_deck)
        db.session.commit()

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