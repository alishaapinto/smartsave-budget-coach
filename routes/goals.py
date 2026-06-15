from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from extensions import db
from models.goal import SavingsGoal
from datetime import datetime

goals_bp = Blueprint('goals', __name__, url_prefix='/goals', template_folder='templates')


@goals_bp.route('/')
@login_required
def list_goals():
    goals = db.session.scalars(db.select(SavingsGoal).filter_by(user_id=current_user.id)).all()
    return render_template('goals/list.html', goals=goals)


@goals_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_goal():
    if request.method == 'POST':
        name = request.form.get('goal_name')
        target = float(request.form.get('target_amount') or 0)
        deadline = request.form.get('deadline')
        date_obj = datetime.fromisoformat(deadline).date() if deadline else None
        goal = SavingsGoal(user_id=current_user.id, goal_name=name, target_amount=target, current_amount=0.0, deadline=date_obj)
        db.session.add(goal)
        db.session.commit()
        flash('Goal created.', 'success')
        return redirect(url_for('goals.list_goals'))
    return render_template('goals/create.html')


@goals_bp.route('/<int:goal_id>/contribute', methods=['POST'])
@login_required
def contribute(goal_id):
    goal = db.get_or_404(SavingsGoal, goal_id)
    if goal.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('goals.list_goals'))
    amount = float(request.form.get('amount') or 0)
    goal.current_amount = float(goal.current_amount) + amount
    db.session.commit()
    flash('Contribution saved.', 'success')
    return redirect(url_for('goals.list_goals'))
