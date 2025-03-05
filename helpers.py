# helpers.py
from config import DEFAULT_DECKS_TEMPLATE
from models import db, Deck, Flashcard

def create_default_decks_for_user(user_id):
    for deck_data in DEFAULT_DECKS_TEMPLATE:
        # Create a new deck for the user
        new_deck = Deck(
            user_id=user_id,
            title=deck_data["title"],
            description=deck_data["description"],
            subject=deck_data["subject"],
            category=deck_data["category"],
            difficulty=deck_data["difficulty"],
            is_default=True  # Mark this deck as a default deck
        )
        db.session.add(new_deck)
        db.session.flush()  # Ensure the deck ID is available for flashcards

        # Create flashcards for the deck
        for flashcard_data in deck_data["flashcards"]:
            new_flashcard = Flashcard(
                deck_id=new_deck.id,
                front_text=flashcard_data["front_text"],
                back_text=flashcard_data["back_text"]
            )
            db.session.add(new_flashcard)

    db.session.commit()