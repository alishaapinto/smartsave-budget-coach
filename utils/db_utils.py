from sqlalchemy import func
from flask import current_app


def month_match_expr(column, month_str):
    """Return a SQL expression that matches year-month across DBs.

    Detect the configured DB from the Flask app's `SQLALCHEMY_DATABASE_URI`.
    Use `strftime` for SQLite and `date_format` for MySQL-style engines.
    """
    uri = ''
    try:
        uri = current_app.config.get('SQLALCHEMY_DATABASE_URI', '') or ''
    except RuntimeError:
        # not in app context; fall back to MySQL-style function
        uri = ''

    if 'sqlite' in uri.lower():
        return func.strftime('%Y-%m', column) == month_str
    return func.date_format(column, '%Y-%m') == month_str
