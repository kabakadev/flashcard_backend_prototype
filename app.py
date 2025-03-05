from flask import Flask
from config import app, db, api
from routes.auth_routes import Signup, Login, ProtectedUser
from routes.deck_routes import DecksResource, DeckResource
from routes.flashcard_routes import FlashcardResource, FlashcardDetailResource
from routes.dashboard_routes import Dashboard
from routes.progress_routes import ProgressResource
from routes.stats_routes import UserStatsResource

# Register all routes
api.add_resource(Signup, "/signup")
api.add_resource(Login, "/login")
api.add_resource(ProtectedUser, "/user")  # Add this line
api.add_resource(DecksResource, "/decks")
api.add_resource(DeckResource, "/decks/<int:deck_id>")
api.add_resource(FlashcardResource, "/flashcards")
api.add_resource(FlashcardDetailResource, "/flashcards/<int:id>")
api.add_resource(Dashboard, "/dashboard")
api.add_resource(ProgressResource, "/progress", "/progress/<int:progress_id>", "/progress/deck/<int:deck_id>", "/progress/flashcard/<int:flashcard_id>")
api.add_resource(UserStatsResource, "/user/stats")

if __name__ == "__main__":
    app.run(debug=True)