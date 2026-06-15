from extensions import db
from models.transaction import Transaction
from models.goal import SavingsGoal
from datetime import date, timedelta
from utils.db_utils import month_match_expr
from collections import defaultdict


def monthly_spending_summary(user_id, months=6):
    today = date.today()
    series = []
    for i in range(months - 1, -1, -1):
        m = (today.replace(day=1) - timedelta(days=i * 30)).strftime('%Y-%m')
        total = db.session.scalar(db.select(db.func.coalesce(db.func.sum(Transaction.amount), 0)).filter(
            Transaction.user_id == user_id,
            month_match_expr(Transaction.date, m),
            Transaction.type == 'expense'
        )) or 0
        series.append({'month': m, 'expense': float(total)})
    return series


def monthly_spending_series(user_id, months=6):
    data = monthly_spending_summary(user_id, months)
    labels = [d['month'] for d in data]
    values = [d['expense'] for d in data]
    return {'labels': labels, 'values': values}


def category_pie_data(user_id):
    rows = db.session.execute(db.select(Transaction.category, db.func.coalesce(db.func.sum(Transaction.amount), 0)).filter(
        Transaction.user_id == user_id,
        Transaction.type == 'expense'
    ).group_by(Transaction.category)).all()
    labels = [r[0] for r in rows]
    values = [float(r[1]) for r in rows]
    return {'labels': labels, 'values': values}


def income_expense_series(user_id, months=6):
    today = date.today()
    labels = []
    incomes = []
    expenses = []
    for i in range(months - 1, -1, -1):
        m = (today.replace(day=1) - timedelta(days=i * 30)).strftime('%Y-%m')
        inc = db.session.scalar(db.select(db.func.coalesce(db.func.sum(Transaction.amount), 0)).filter(
            Transaction.user_id == user_id,
            month_match_expr(Transaction.date, m),
            Transaction.type == 'income'
        )) or 0
        exp = db.session.scalar(db.select(db.func.coalesce(db.func.sum(Transaction.amount), 0)).filter(
            Transaction.user_id == user_id,
            month_match_expr(Transaction.date, m),
            Transaction.type == 'expense'
        )) or 0
        labels.append(m)
        incomes.append(float(inc))
        expenses.append(float(exp))
    return {'labels': labels, 'incomes': incomes, 'expenses': expenses}


def savings_growth_series(user_id, months=6):
    goals = db.session.scalars(db.select(SavingsGoal).filter_by(user_id=user_id)).all()
    # compute total savings across all goals month by month
    today = date.today()
    labels = []
    values = []
    running = 0.0
    for i in range(months - 1, -1, -1):
        m = (today.replace(day=1) - timedelta(days=i * 30)).strftime('%Y-%m')
        # approximate by summing goal current_amount if deadline <= month
        running = sum(float(g.current_amount) for g in goals)
        labels.append(m)
        values.append(running)
    return {'labels': labels, 'values': values}
