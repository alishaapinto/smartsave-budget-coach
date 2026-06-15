from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.transaction import Transaction
from datetime import datetime

transactions_bp = Blueprint('transactions', __name__, url_prefix='/transactions', template_folder='templates')

CATEGORIES = ['Food', 'Travel', 'Shopping', 'Education', 'Health', 'Entertainment', 'Bills', 'Emergency', 'Other']


@transactions_bp.route('/')
@login_required
def list_transactions():
    q = db.select(Transaction).filter_by(user_id=current_user.id)
    category = request.args.get('category')
    start = request.args.get('start')
    end = request.args.get('end')
    search = request.args.get('q')
    if category:
        q = q.filter_by(category=category)
    if start:
        try:
            start_date = datetime.fromisoformat(start).date()
            q = q.filter(Transaction.date >= start_date)
        except Exception:
            pass
    if end:
        try:
            end_date = datetime.fromisoformat(end).date()
            q = q.filter(Transaction.date <= end_date)
        except Exception:
            pass
    if search:
        q = q.filter(Transaction.description.ilike(f"%{search}%"))
    transactions = db.session.scalars(q.order_by(Transaction.date.desc())).all()
    return render_template('transactions/list.html', transactions=transactions, categories=CATEGORIES)


@transactions_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_transaction():
    if request.method == 'POST':
        try:
            amount = float(request.form['amount'])
            category = request.form['category']
            t_type = request.form['type']
            description = request.form.get('description')
            date_str = request.form.get('date')
            emergency = request.form.get('emergency') == 'on'
            date_obj = datetime.fromisoformat(date_str).date() if date_str else datetime.utcnow().date()
            tx = Transaction(user_id=current_user.id, amount=amount, category=category, type=t_type,
                             description=description, date=date_obj, emergency=emergency)
            db.session.add(tx)
            db.session.commit()
            flash('Transaction saved.', 'success')
            return redirect(url_for('transactions.list_transactions'))
        except Exception as e:
            db.session.rollback()
            flash(f'Failed to save transaction: {e}', 'danger')
            return redirect(url_for('transactions.add_transaction'))
    return render_template('transactions/add.html', categories=CATEGORIES)


@transactions_bp.route('/<int:tx_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_transaction(tx_id):
    tx = db.get_or_404(Transaction, tx_id)
    if tx.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('transactions.list_transactions'))
    if request.method == 'POST':
        tx.amount = float(request.form['amount'])
        tx.category = request.form['category']
        tx.type = request.form['type']
        tx.description = request.form.get('description')
        tx.date = datetime.fromisoformat(request.form.get('date')).date()
        tx.emergency = request.form.get('emergency') == 'on'
        db.session.commit()
        flash('Transaction updated.', 'success')
        return redirect(url_for('transactions.list_transactions'))
    return render_template('transactions/edit.html', tx=tx, categories=CATEGORIES)


@transactions_bp.route('/<int:tx_id>/delete', methods=['POST'])
@login_required
def delete_transaction(tx_id):
    tx = db.get_or_404(Transaction, tx_id)
    if tx.user_id != current_user.id:
        flash('Unauthorized', 'danger')
        return redirect(url_for('transactions.list_transactions'))
    db.session.delete(tx)
    db.session.commit()
    flash('Transaction deleted.', 'info')
    return redirect(url_for('transactions.list_transactions'))
