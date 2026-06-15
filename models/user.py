from datetime import datetime
from flask_login import UserMixin
from sqlalchemy.orm import relationship
from extensions import db, bcrypt


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    budgets = relationship('Budget', backref='user', cascade='all, delete-orphan')
    transactions = relationship('Transaction', backref='user', cascade='all, delete-orphan')
    goals = relationship('SavingsGoal', backref='user', cascade='all, delete-orphan')
    badges = relationship('Badge', backref='user', cascade='all, delete-orphan')
    streak = relationship('Streak', uselist=False, backref='user', cascade='all, delete-orphan')

    def set_password(self, password: str):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.email}>"
