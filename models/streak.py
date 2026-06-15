from datetime import datetime
from extensions import db


class Streak(db.Model):
    __tablename__ = 'streaks'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    current_streak = db.Column(db.Integer, default=0)
    longest_streak = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, nullable=True)

    def increment(self):
        self.current_streak = (self.current_streak or 0) + 1
        if self.current_streak > (self.longest_streak or 0):
            self.longest_streak = self.current_streak
        self.updated_at = datetime.utcnow()

    def reset(self):
        self.current_streak = 0
        self.updated_at = datetime.utcnow()

    def __repr__(self):
        return f"<Streak user={self.user_id} current={self.current_streak} longest={self.longest_streak}>"
