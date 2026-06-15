from flask import Blueprint

from .auth import auth_bp
from .dashboard import dashboard_bp
from .transactions import transactions_bp
from .budgets import budgets_bp
from .goals import goals_bp
from .analytics import analytics_bp

__all__ = ['auth_bp', 'dashboard_bp', 'transactions_bp', 'budgets_bp', 'goals_bp', 'analytics_bp']
