from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import db
from models import Flashcard, Deck

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