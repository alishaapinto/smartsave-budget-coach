from datetime import datetime
from extensions import db


class Badge(db.Model):
    __tablename__ = 'badges'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    badge_name = db.Column(db.String(64), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Badge {self.badge_name} for {self.user_id}>"
