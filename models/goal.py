from datetime import date
from extensions import db


class SavingsGoal(db.Model):
    __tablename__ = 'savings_goals'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    goal_name = db.Column(db.String(128), nullable=False)
    target_amount = db.Column(db.Numeric(14, 2), nullable=False)
    current_amount = db.Column(db.Numeric(14, 2), nullable=False, default=0.00)
    deadline = db.Column(db.Date, nullable=True)

    def progress(self) -> float:
        if not self.target_amount or float(self.target_amount) <= 0:
            return 0.0
        return min(100.0, float(self.current_amount) / float(self.target_amount) * 100.0)

    def contribute(self, amount: float):
        self.current_amount = float(self.current_amount) + float(amount)

    def __repr__(self):
        return f"<SavingsGoal {self.goal_name} {self.current_amount}/{self.target_amount}>"
