from extensions import db
from models.streak import Streak
from models.budget import Budget
from models.transaction import Transaction
from datetime import date


def update_streak_for_user(user_id):
    today = date.today()
    month_key = today.strftime('%Y-%m')
    # find budget for this month
    budget = db.session.scalar(db.select(Budget).filter_by(user_id=user_id, month=month_key))
    from utils.db_utils import month_match_expr

    spent = db.session.scalar(db.select(db.func.coalesce(db.func.sum(Transaction.amount), 0)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense',
        month_match_expr(Transaction.date, month_key)
    )) or 0

    streak = db.session.scalar(db.select(Streak).filter_by(user_id=user_id))
    if not streak:
        streak = Streak(user_id=user_id, current_streak=0, longest_streak=0)
        db.session.add(streak)
        db.session.flush()

    # If no budget set, do not modify streak
    if not budget or not budget.budget_amount or float(budget.budget_amount) <= 0:
        db.session.commit()
        return streak

    usage = float(spent) / float(budget.budget_amount) * 100.0 if float(budget.budget_amount) > 0 else 0.0
    if usage <= 100.0:
        # within budget -> increment only if not already updated today
        last_updated_date = streak.updated_at.date() if streak.updated_at else None
        if last_updated_date != today:
            streak.increment()
    else:
        # exceeded -> reset unless emergency expenses account for it
        # simple rule: if any non-emergency expense pushed over budget, reset
        over = float(spent) - float(budget.budget_amount)
        emergency_sum = db.session.scalar(db.select(db.func.coalesce(db.func.sum(Transaction.amount), 0)).filter(
            Transaction.user_id == user_id,
            Transaction.type == 'expense',
            Transaction.emergency == True,
            month_match_expr(Transaction.date, month_key)
        )) or 0
        if over > float(emergency_sum):
            streak.reset()
        else:
            # emergency covered the overage; do not break streak
            pass

    db.session.commit()
    return streak
