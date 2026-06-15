from flask import Blueprint, render_template
from flask_login import login_required, current_user
from extensions import db
from models.transaction import Transaction
from models.budget import Budget
from models.goal import SavingsGoal
from models.badge import Badge
from models.streak import Streak
from services.achievements import evaluate_badges
from services.streaks import update_streak_for_user
from services.analytics_service import monthly_spending_summary
from datetime import datetime, date
from utils.db_utils import month_match_expr
from flask import current_app

dashboard_bp = Blueprint('dashboard', __name__, template_folder='templates')


@dashboard_bp.route('/')
@login_required
def index():
    user = current_user
    today = date.today()
    month_key = today.strftime('%Y-%m')

    # Totals
    incomes = db.session.scalar(db.select(db.func.coalesce(db.func.sum(Transaction.amount), 0)).filter_by(user_id=user.id, type='income')) or 0
    expenses = db.session.scalar(db.select(db.func.coalesce(db.func.sum(Transaction.amount), 0)).filter_by(user_id=user.id, type='expense')) or 0
    balance = float(incomes) - float(expenses)

    # Budget
    budget = db.session.scalar(db.select(Budget).filter_by(user_id=user.id, month=month_key))
    spent_this_month = db.session.scalar(db.select(db.func.coalesce(db.func.sum(Transaction.amount), 0)).filter(
        Transaction.user_id == user.id,
        Transaction.type == 'expense',
        month_match_expr(Transaction.date, month_key)
    )) or 0

    budget_amount = float(budget.budget_amount) if budget else 0.0
    remaining = budget_amount - float(spent_this_month)
    usage_pct = budget.usage_percentage(spent_this_month) if budget else 0.0

    # Goals
    goals = db.session.scalars(db.select(SavingsGoal).filter_by(user_id=user.id)).all()

    # Streaks and badges
    # Update streak logic (simple): increment if within budget, else reset
    streak = update_streak_for_user(user.id)

    # Evaluate badges
    evaluate_badges(user.id)
    badges = db.session.scalars(db.select(Badge).filter_by(user_id=user.id)).all()

    # Motivation
    motivations = [
        'Great job staying within your budget.',
        'You are building strong financial habits.',
        'Every small saving matters.',
        'Keep going. Your future self will thank you.'
    ]

    # Analytics quick data
    monthly = monthly_spending_summary(user.id)
    # Values are already in INR; ensure they are floats for charting
    for m in monthly:
        m['expense'] = float(m.get('expense', 0))

    return render_template('dashboard/index.html',
                           total_income=float(incomes),
                           total_expense=float(expenses),
                           balance=balance,
                           budget_amount=budget_amount,
                           remaining=remaining,
                           usage_pct=usage_pct,
                           goals=goals,
                           streak=streak,
                           badges=badges,
                           motivation=motivations[(today.day + user.id) % len(motivations)],
                           monthly_data=monthly)


@dashboard_bp.route('/dashboard')
@login_required
def dashboard_alias():
    # Alias route to support /dashboard URL
    return index()
