from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import db
from models import UserStats

class UserStatsResource(Resource):
    @jwt_required()
    def put(self):
        """Update user stats, such as weekly goal."""
        user_id = get_jwt_identity().get("id")
        data = request.get_json()

        stats = UserStats.query.filter_by(user_id=user_id).first()
        if not stats:
            stats = UserStats(user_id=user_id)
            db.session.add(stats)

        if "weekly_goal" in data:
            stats.weekly_goal = data["weekly_goal"]
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