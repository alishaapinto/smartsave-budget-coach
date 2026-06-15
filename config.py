import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TEMPLATES_AUTO_RELOAD = True
    DB_USER = os.getenv('MYSQL_USER', 'root')
    DB_PASS = os.getenv('MYSQL_PASSWORD', '')
    DB_HOST = os.getenv('MYSQL_HOST', '127.0.0.1')
    DB_PORT = os.getenv('MYSQL_PORT', '3306')
    DB_NAME = os.getenv('MYSQL_DB', 'smartsave')

    # Use PyMySQL driver by default, but allow a development SQLite fallback
    use_sqlite = os.getenv('USE_SQLITE', '').lower() in ('1', 'true', 'yes')
    mysql_env_provided = bool(os.getenv('MYSQL_HOST') or os.getenv('MYSQL_DB') or os.getenv('MYSQL_USER'))
    if use_sqlite or not mysql_env_provided:
        # Development fallback: local SQLite file (not for production)
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', f"sqlite:///{os.path.join(os.getcwd(), 'smartsave_dev.db')}")
    else:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASS)}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
        )

    # Session cookie settings
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Flask-Mail could be configured later; not required for core functionality
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', None)
    MAIL_SERVER = os.getenv('MAIL_SERVER', '')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 0) or 0)
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', None)
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', None)
    # Exchange rate for USD -> INR used for display only (default 83.0)
    EXCHANGE_RATE_USD_TO_INR = float(os.getenv('EXCHANGE_RATE_USD_TO_INR', '83.0'))
