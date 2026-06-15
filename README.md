<<<<<<< HEAD
# SmartSave – Gamified Budget Coach

Production-ready Flask application for habit-forming budgeting via gamification.

## Setup

1. Install Python 3.12+
2. Create MySQL database:

```sql
CREATE DATABASE smartsave CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

3. Create a `.env` file and configure your database, secret key, and email settings.

4. Install dependencies:

```bash
pip install -r requirements.txt
```

5. Run the application:

```bash
set FLASK_APP=app.py
flask run
```

## Notes

* The application uses SQLAlchemy to automatically create database tables when `AUTO_CREATE_DB` is enabled.
* For production, use a secure random value for `SECRET_KEY`.
* Built using Python, Flask, MySQL, SQLAlchemy, Bootstrap, and Chart.js.
=======
# smartsave-budget-coach
Gamified personal finance and budget management application built using Python, Flask, MySQL, SQLAlchemy, Bootstrap, and Chart.js.
>>>>>>> 2dd8d858e123d83836a731c3e3a10d6ec615811c
