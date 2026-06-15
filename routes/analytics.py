from flask import Blueprint, jsonify, render_template, current_app
from flask_login import login_required, current_user
from services.analytics_service import (
    monthly_spending_series,
    category_pie_data,
    income_expense_series,
    savings_growth_series,
)

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics', template_folder='templates')


@analytics_bp.route('/')
@login_required
def index():
    return render_template('analytics/index.html')


@analytics_bp.route('/monthly.json')
@login_required
def monthly():
    return jsonify(monthly_spending_series(current_user.id))


@analytics_bp.route('/categories.json')
@login_required
def categories():
    return jsonify(category_pie_data(current_user.id))


@analytics_bp.route('/income-expense.json')
@login_required
def income_expense():
    return jsonify(income_expense_series(current_user.id))


@analytics_bp.route('/savings.json')
@login_required
def savings():
    return jsonify(savings_growth_series(current_user.id))
