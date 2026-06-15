import os
from datetime import datetime
from flask import Flask
from config import Config
from extensions import db, migrate, login_manager, bcrypt, csrf

# guard so we only start the auto-open once per process
_auto_open_started = False

def create_app():
    app = Flask(__name__, static_folder='static', template_folder='templates')
    app.config.from_object(Config)
    # Allow forcing debug mode via environment for create_app time decisions
    debug_mode = os.getenv('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes')
    app.debug = debug_mode

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)

    # import models so migrations can detect them
    from models import user, budget, transaction, goal, badge, streak

    # register blueprints
    from routes import auth_bp, dashboard_bp, transactions_bp, budgets_bp, goals_bp, analytics_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(budgets_bp)
    app.register_blueprint(goals_bp)
    app.register_blueprint(analytics_bp)

    # Ensure the login user loader is registered with this LoginManager instance
    try:
        from routes.auth import load_user as _load_user
        login_manager.user_loader(_load_user)
    except Exception:
        pass

    # create DB tables automatically if configured
    with app.app_context():
        if os.getenv('AUTO_CREATE_DB', 'true').lower() in ('1', 'true', 'yes'):
            db.create_all()

    # Configure file logging for unhandled exceptions to help debugging
    try:
        import logging
        fh = logging.FileHandler('error.log')
        fh.setLevel(logging.ERROR)
        app.logger.addHandler(fh)
    except Exception:
        pass

    # Global exception handler to ensure stack traces are logged to error.log
    try:
        import traceback

        if not debug_mode:
            @app.errorhandler(Exception)
            def _handle_exception(e):
                app.logger.exception('Unhandled exception')
                return ('Internal Server Error', 500)
        # If debug_mode is True, let Flask/Werkzeug show the interactive traceback.
    except Exception:
        pass

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'
    # Register Jinja filter for INR formatting
    try:
        from utils.currency import format_inr
        app.jinja_env.filters['inr'] = format_inr
        # expose exchange rate as a global in templates
        app.jinja_env.globals['EXCHANGE_RATE_USD_TO_INR'] = app.config.get('EXCHANGE_RATE_USD_TO_INR', 83.0)
    except Exception:
        pass
    # Open the app URL in the default web browser shortly after startup.
    # Can be disabled by setting DISABLE_AUTO_OPEN=1 in the environment.
    global _auto_open_started
    if not _auto_open_started and os.getenv('DISABLE_AUTO_OPEN', 'false').lower() not in ('1', 'true', 'yes'):
        try:
            import webbrowser
            from threading import Timer

            port = int(os.environ.get('PORT', 5000))
            url = f'http://127.0.0.1:{port}'
            # delay slightly to give the server time to start
            Timer(1.5, lambda: webbrowser.open_new(url)).start()
            _auto_open_started = True
        except Exception:
            pass

    return app


if __name__ == '__main__':
    app = create_app()
    debug_mode = os.getenv('FLASK_DEBUG', '').lower() in ('1', 'true', 'yes')
    # Disable the reloader to avoid double-process DB locking during dev tests
    app.run(debug=debug_mode, use_reloader=False)
