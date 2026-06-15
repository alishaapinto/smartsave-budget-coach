from datetime import date
from extensions import db


class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'income' or 'expense'
    description = db.Column(db.String(255), nullable=True)
    date = db.Column(db.Date, nullable=False)
    emergency = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            'id': self.id,
            'amount': float(self.amount),
            'category': self.category,
            'type': self.type,
            'description': self.description,
            'date': self.date.isoformat(),
            'emergency': bool(self.emergency),
        }

    def __repr__(self):
        return f"<Transaction {self.id} {self.type} {self.amount}>"
