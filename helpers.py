from config import app, db
from models import DefaultDeck, DefaultFlashcard

def populate_default_decks():
    default_decks = [
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

    for deck_data in default_decks:
        new_deck = DefaultDeck(
            title=deck_data["title"],
            description=deck_data["description"],
            subject=deck_data["subject"],
            category=deck_data["category"],
            difficulty=deck_data["difficulty"]
        )
        db.session.add(new_deck)
        db.session.flush()  # Ensure the deck ID is available for flashcards

        for flashcard_data in deck_data["flashcards"]:
            new_flashcard = DefaultFlashcard(
                default_deck_id=new_deck.id,
                front_text=flashcard_data["front_text"],
                back_text=flashcard_data["back_text"]
            )
            db.session.add(new_flashcard)

    db.session.commit()

if __name__ == "__main__":
    # Use the existing app instance from config.py
    with app.app_context():
        populate_default_decks()