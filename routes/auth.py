from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email
from models.user import User
from extensions import db, bcrypt, login_manager
from itsdangerous import URLSafeTimedSerializer
from datetime import datetime

auth_bp = Blueprint('auth', __name__, url_prefix='/auth', template_folder='templates')


class RegisterForm(FlaskForm):
    username = StringField('Username', [InputRequired(), Length(min=2, max=80)])
    email = StringField('Email', [InputRequired(), Email(), Length(max=255)])
    password = PasswordField('Password', [InputRequired(), Length(min=6)])


class LoginForm(FlaskForm):
    email = StringField('Email', [InputRequired(), Email()])
    password = PasswordField('Password', [InputRequired()])


class ForgotForm(FlaskForm):
    email = StringField('Email', [InputRequired(), Email()])


class ResetForm(FlaskForm):
    password = PasswordField('Password', [InputRequired(), Length(min=6)])


def load_user(user_id):
    return db.session.get(User, int(user_id))


def generate_token(email: str):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(email, salt='password-reset-salt')


def verify_token(token, expiration=3600):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='password-reset-salt', max_age=expiration)
        return email
    except Exception:
        return None


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    try:
        form = RegisterForm()
        if form.validate_on_submit():
            if db.session.scalar(db.select(User).filter_by(email=form.email.data)):
                flash('Email already registered', 'danger')
                return redirect(url_for('auth.register'))
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            try:
                db.session.commit()
            except Exception:
                current_app.logger.exception('Database error during registration')
                db.session.rollback()
                flash('An internal error occurred. Please try again later.', 'danger')
                return redirect(url_for('auth.register'))
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('auth.login'))
        return render_template('auth/register.html', form=form)
    except Exception:
        import traceback
        tb = traceback.format_exc()
        try:
            with open('traceback_register.log', 'a', encoding='utf-8') as f:
                f.write(tb + "\n---\n")
        except Exception:
            pass
        current_app.logger.exception('Unhandled exception in register route')
        # In debug mode return traceback in response to aid diagnosis
        if current_app.debug:
            return (f"<pre>{tb}</pre>", 500)
        raise


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        form = LoginForm()
        if form.validate_on_submit():
            user = db.session.scalar(db.select(User).filter_by(email=form.email.data))
            if user and user.check_password(form.password.data):
                login_user(user)
                flash('Logged in successfully.', 'success')
                return redirect(url_for('dashboard.index'))
            flash('Invalid credentials', 'danger')
            return redirect(url_for('auth.login'))
        return render_template('auth/login.html', form=form)
    except Exception:
        import traceback
        tb = traceback.format_exc()
        try:
            with open('traceback_login.log', 'a', encoding='utf-8') as f:
                f.write(tb + "\n---\n")
        except Exception:
            pass
        current_app.logger.exception('Unhandled exception in login route')
        if current_app.debug:
            return (f"<pre>{tb}</pre>", 500)
        raise


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot', methods=['GET', 'POST'])
def forgot():
    form = ForgotForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).filter_by(email=form.email.data))
        if user:
            token = generate_token(user.email)
            reset_link = url_for('auth.reset_password', token=token, _external=True)
            
            # Force reload .env file dynamically to guarantee latest App Password is read
            try:
                from dotenv import load_dotenv
                load_dotenv(override=True)
            except Exception:
                pass
            
            import os
            mail_server = os.getenv('MAIL_SERVER') or current_app.config.get('MAIL_SERVER')
            mail_user = os.getenv('MAIL_USERNAME') or current_app.config.get('MAIL_USERNAME')
            mail_pass = os.getenv('MAIL_PASSWORD') or current_app.config.get('MAIL_PASSWORD')
            
            mail_sent = False
            if mail_server and mail_user and mail_pass and mail_pass != 'YOUR_GMAIL_APP_PASSWORD':
                try:
                    import smtplib
                    from email.mime.text import MIMEText
                    from email.mime.multipart import MIMEMultipart

                    msg = MIMEMultipart()
                    msg['From'] = os.getenv('MAIL_DEFAULT_SENDER') or current_app.config.get('MAIL_DEFAULT_SENDER') or mail_user
                    msg['To'] = user.email
                    msg['Subject'] = "Reset Your SmartSave Password"

                    body = f"Hello,\n\nPlease click the link below to reset your password:\n{reset_link}\n\nIf you did not request this, please ignore this email."
                    msg.attach(MIMEText(body, 'plain'))

                    port = int(os.getenv('MAIL_PORT') or current_app.config.get('MAIL_PORT') or 587)
                    server = smtplib.SMTP(mail_server, port)
                    server.starttls()
                    server.login(mail_user, mail_pass)
                    server.send_message(msg)
                    server.quit()
                    mail_sent = True
                except Exception as e:
                    current_app.logger.exception('SMTP Email sending failed')

            current_app.logger.info(f'Password reset link for {user.email}: {reset_link}')
            
            if mail_sent:
                flash('Password reset link has been sent to your email address.', 'success')
            else:
                flash(f'Reset link: {reset_link} (Configure SMTP in .env to send to your inbox)', 'warning')
            return redirect(url_for('auth.login'))
        flash('If that email exists, a reset link was generated.', 'info')
    return render_template('auth/forgot.html', form=form)


@auth_bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    email = verify_token(token)
    if not email:
        flash('Invalid or expired token', 'danger')
        return redirect(url_for('auth.forgot'))
    form = ResetForm()
    if form.validate_on_submit():
        password = form.password.data
        user = db.session.scalar(db.select(User).filter_by(email=email))
        if not user:
            flash('User not found', 'danger')
            return redirect(url_for('auth.register'))
        user.set_password(password)
        db.session.commit()
        flash('Password reset successful. Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset.html', token=token, form=form)
