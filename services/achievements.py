from extensions import db
from models.badge import Badge
from models.transaction import Transaction
from models.goal import SavingsGoal
from datetime import datetime


def _saver_check(user_id, threshold):
    total_saved = db.session.query(db.func.coalesce(db.func.sum(Transaction.amount), 0)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'income'
    ).scalar() or 0
    return float(total_saved) >= float(threshold)


def _goal_achieved(user_id):
    goal = db.session.scalar(db.select(SavingsGoal).filter_by(user_id=user_id))
    if not goal:
        return False
    return float(goal.current_amount) >= float(goal.target_amount)


def _legend_check(user_id):
    # Example: many transactions and high savings
    tx_count = db.session.query(db.func.count(Transaction.id)).filter(Transaction.user_id == user_id).scalar() or 0
    total_saved = db.session.query(db.func.coalesce(db.func.sum(Transaction.amount), 0)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'income'
    ).scalar() or 0
    return tx_count > 200 and float(total_saved) > 10000


BADGES = [
    ('Budget Beginner', lambda user_id: True),
    ('Smart Saver', lambda user_id: _saver_check(user_id, 500)),
    ('Budget Master', lambda user_id: _saver_check(user_id, 2000)),
    ('Savings Champion', lambda user_id: _goal_achieved(user_id)),
    ('Financial Legend', lambda user_id: _legend_check(user_id)),
]


def evaluate_badges(user_id):
    for name, checker in BADGES:
        try:
            exists = db.session.scalar(db.select(Badge).filter_by(user_id=user_id, badge_name=name))
            if not exists and checker(user_id):
                b = Badge(user_id=user_id, badge_name=name, earned_at=datetime.utcnow())
                db.session.add(b)
        except Exception:
            db.session.rollback()
    db.session.commit()
