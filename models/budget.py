from datetime import date
from extensions import db


class Budget(db.Model):
    __tablename__ = 'budgets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    month = db.Column(db.String(7), nullable=False)  # YYYY-MM
    budget_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0.00)

    def usage_percentage(self, spent_amount: float) -> float:
        if not self.budget_amount or float(self.budget_amount) <= 0:
            return 0.0
        return min(100.0, float(spent_amount) / float(self.budget_amount) * 100.0)

    def remaining(self, spent_amount: float) -> float:
        return max(0.0, float(self.budget_amount) - float(spent_amount))

    def __repr__(self):
        return f"<Budget {self.user_id} {self.month} {self.budget_amount}>"
