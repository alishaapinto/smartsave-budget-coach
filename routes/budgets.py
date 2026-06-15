from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models.budget import Budget
from datetime import date

budgets_bp = Blueprint('budgets', __name__, url_prefix='/budgets', template_folder='templates')


@budgets_bp.route('/')
@login_required
def manage_budgets():
    # show current month budget and list
    month = request.args.get('month') or date.today().strftime('%Y-%m')
    budgets = db.session.scalars(db.select(Budget).filter_by(user_id=current_user.id).order_by(Budget.month.desc())).all()
    current = db.session.scalar(db.select(Budget).filter_by(user_id=current_user.id, month=month))
    return render_template('budgets/manage.html', budgets=budgets, current=current, month=month)


@budgets_bp.route('/set', methods=['POST'])
@login_required
def set_budget():
    month = request.form.get('month')
    amount = float(request.form.get('amount') or 0)
    if not month:
        flash('Month is required', 'danger')
        return redirect(url_for('budgets.manage_budgets'))
    budget = db.session.scalar(db.select(Budget).filter_by(user_id=current_user.id, month=month))
    if budget:
        budget.budget_amount = amount
    else:
        budget = Budget(user_id=current_user.id, month=month, budget_amount=amount)
        db.session.add(budget)
    db.session.commit()
    flash('Budget saved.', 'success')
    return redirect(url_for('budgets.manage_budgets'))
