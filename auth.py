from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session, flash, current_app
from db import db, User, NotificationPreference
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import datetime
import os
import re
import secrets
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import google_auth_oauthlib.flow
import google.oauth2.credentials
import googleapiclient.discovery
import google_fit

auth_bp = Blueprint('auth', __name__)

# Helper functions for authentication
def generate_token(length=32):
    """Generate a secure random token."""
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

def send_email(to_email, subject, html_content):
    """Send an email using SMTP."""
    try:
        # Get email configuration from environment variables or use defaults
        smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.getenv('SMTP_PORT', 587))
        smtp_username = os.getenv('SMTP_USERNAME', 'your-email@gmail.com')
        smtp_password = os.getenv('SMTP_PASSWORD', 'your-password')
        from_email = os.getenv('FROM_EMAIL', 'noreply@fitgen.com')

        # Create message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        # Attach HTML content
        msg.attach(MIMEText(html_content, 'html'))

        # Connect to SMTP server and send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def send_verification_email(user):
    """Send verification email to user."""
    # Generate verification token
    token = generate_token()
    expiration = datetime.datetime.now() + datetime.timedelta(hours=24)

    # Save token to user
    user.verification_token = token
    user.verification_token_expires = expiration
    db.session.commit()

    # Create verification link
    verification_link = url_for('auth.verify_email', token=token, _external=True)

    # Email content
    subject = "Verify Your FitGen Account"
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
            <h2 style="color: #FF5722;">Welcome to FitGen!</h2>
            <p>Thank you for registering. Please verify your email address by clicking the button below:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{verification_link}" style="background-color: #FF5722; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">Verify Email</a>
            </div>
            <p>This link will expire in 24 hours.</p>
            <p>If you didn't create an account, you can safely ignore this email.</p>
            <p>Best regards,<br>The FitGen Team</p>
        </div>
    </body>
    </html>
    """

    # Send email
    return send_email(user.email, subject, html_content)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()

        # Validate required fields
        if not data:
            return jsonify({"msg": "No data provided"}), 400

        email = data.get('email')
        password = data.get('password')
        name = data.get('name', '')
        role = data.get('role', 'User')

        if not email or not password:
            return jsonify({"msg": "Email and password are required"}), 400

        # Validate email format
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"msg": "Invalid email format"}), 400

        # Validate password strength
        if len(password) < 8:
            return jsonify({"msg": "Password must be at least 8 characters long"}), 400

        # Check for at least one uppercase letter, one lowercase letter, and one number
        if not (any(c.isupper() for c in password) and
                any(c.islower() for c in password) and
                any(c.isdigit() for c in password)):
            return jsonify({"msg": "Password must contain at least one uppercase letter, one lowercase letter, and one number"}), 400

        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({"msg": "Email already exists"}), 409

        # Create new user
        user = User(email=email, role=role, name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Create default notification preferences
        create_default_notification_preferences(user.id)

        # Send verification email
        send_verification_email(user)

        return jsonify({
            "msg": "User created successfully. Please check your email to verify your account.",
            "user_id": user.id,
            "email": user.email
        }), 201

    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")
        return jsonify({"msg": "An error occurred during registration. Please try again."}), 500

def create_default_notification_preferences(user_id):
    """Create default notification preferences for a new user."""
    try:
        # Default notification types
        notification_types = [
            'meal_reminder',
            'workout_reminder',
            'goal_achievement',
            'water_reminder',
            'sleep_reminder'
        ]

        for notification_type in notification_types:
            preference = NotificationPreference(
                user_id=user_id,
                notification_type=notification_type,
                enabled=True,
                send_mobile=True,
                send_watch=True
            )
            db.session.add(preference)

        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error creating default notification preferences: {str(e)}")

@auth_bp.route('/verify-email/<token>', methods=['GET'])
def verify_email(token):
    """Verify user email with token."""
    user = User.query.filter_by(verification_token=token).first()

    if not user:
        flash('Invalid verification link.', 'error')
        return redirect(url_for('auth.login_page'))

    # Check if token is expired
    if user.verification_token_expires and user.verification_token_expires < datetime.datetime.now():
        flash('Verification link has expired. Please request a new one.', 'error')
        return redirect(url_for('auth.login_page'))

    # Mark user as verified
    user.is_verified = True
    user.verification_token = None
    user.verification_token_expires = None
    db.session.commit()

    flash('Your email has been verified! You can now log in.', 'success')
    return redirect(url_for('auth.login_page'))

@auth_bp.route('/resend-verification', methods=['POST'])
def resend_verification():
    """Resend verification email."""
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"msg": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        # Don't reveal that the user doesn't exist
        return jsonify({"msg": "If your email exists in our system, a verification link has been sent."}), 200

    if user.is_verified:
        return jsonify({"msg": "Your email is already verified. Please log in."}), 200

    # Send verification email
    send_verification_email(user)

    return jsonify({"msg": "Verification email has been sent. Please check your inbox."}), 200

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Send password reset email."""
    data = request.get_json()
    email = data.get('email')

    if not email:
        return jsonify({"msg": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        # Don't reveal that the user doesn't exist
        return jsonify({"msg": "If your email exists in our system, a password reset link has been sent."}), 200

    # Generate reset token
    token = generate_token()
    expiration = datetime.datetime.now() + datetime.timedelta(hours=1)

    # Save token to user
    user.reset_token = token
    user.reset_token_expires = expiration
    db.session.commit()

    # Create reset link
    reset_link = url_for('auth.reset_password_page', token=token, _external=True)

    # Email content
    subject = "Reset Your FitGen Password"
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 10px;">
            <h2 style="color: #FF5722;">Reset Your Password</h2>
            <p>We received a request to reset your password. Click the button below to create a new password:</p>
            <div style="text-align: center; margin: 30px 0;">
                <a href="{reset_link}" style="background-color: #FF5722; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">Reset Password</a>
            </div>
            <p>This link will expire in 1 hour.</p>
            <p>If you didn't request a password reset, you can safely ignore this email.</p>
            <p>Best regards,<br>The FitGen Team</p>
        </div>
    </body>
    </html>
    """

    # Send email
    send_email(user.email, subject, html_content)

    return jsonify({"msg": "If your email exists in our system, a password reset link has been sent."}), 200

@auth_bp.route('/reset-password/<token>', methods=['GET'])
def reset_password_page(token):
    """Show reset password page."""
    # Check if token is valid
    user = User.query.filter_by(reset_token=token).first()

    if not user or (user.reset_token_expires and user.reset_token_expires < datetime.datetime.now()):
        flash('Invalid or expired password reset link.', 'error')
        return redirect(url_for('auth.login_page'))

    return render_template('reset_password.html', token=token)

@auth_bp.route('/reset-password/<token>', methods=['POST'])
def reset_password(token):
    """Reset user password."""
    # Check if token is valid
    user = User.query.filter_by(reset_token=token).first()

    if not user:
        return jsonify({"msg": "Invalid reset token"}), 400

    # Check if token is expired
    if user.reset_token_expires and user.reset_token_expires < datetime.datetime.now():
        return jsonify({"msg": "Reset token has expired"}), 400

    # Get new password
    data = request.get_json()
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if not password or not confirm_password:
        return jsonify({"msg": "Password and confirmation are required"}), 400

    if password != confirm_password:
        return jsonify({"msg": "Passwords do not match"}), 400

    # Validate password strength
    if len(password) < 8:
        return jsonify({"msg": "Password must be at least 8 characters long"}), 400

    # Check for at least one uppercase letter, one lowercase letter, and one number
    if not (any(c.isupper() for c in password) and
            any(c.islower() for c in password) and
            any(c.isdigit() for c in password)):
        return jsonify({"msg": "Password must contain at least one uppercase letter, one lowercase letter, and one number"}), 400

    # Update password
    user.set_password(password)
    user.reset_token = None
    user.reset_token_expires = None
    db.session.commit()

    return jsonify({"msg": "Password has been reset successfully. You can now log in with your new password."}), 200

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Invalid credentials"}), 401

    # Check if user is verified
    if not user.is_verified:
        return jsonify({
            "msg": "Please verify your email before logging in.",
            "needs_verification": True,
            "email": user.email
        }), 401

    # Update last login time
    user.last_login = datetime.datetime.now()
    db.session.commit()

    expires = datetime.timedelta(days=1)
    token = create_access_token(identity={'email': user.email, 'role': user.role, 'user_id': user.id}, expires_delta=expires)

    return jsonify({
        "access_token": token,
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role
        }
    }), 200

@auth_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET'])
def register_page():
    return render_template('register.html')

@auth_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@auth_bp.route('/user-dashboard')
def user_dashboard():
    # Check if user is authenticated with Google Fit
    has_google_fit = 'credentials' in session

    # Get fitness data if authenticated
    fitness_data = None
    if has_google_fit:
        try:
            fitness_data = google_fit.get_all_fitness_data()
        except Exception as e:
            print(f"Error getting fitness data: {e}")

    return render_template('user_dashboard.html',
                          has_google_fit=has_google_fit,
                          fitness_data=fitness_data)

@auth_bp.route('/modern-dashboard')
def modern_dashboard():
    """Render the modern dashboard page with FitGen 2.0 design."""
    return render_template('modern-dashboard.html')

@auth_bp.route('/authorize-google-fit')
def authorize_google_fit():
    """Redirect to Google for authorization."""
    try:
        authorization_url = google_fit.get_authorization_url()
        return redirect(authorization_url)
    except Exception as e:
        return jsonify(error=str(e)), 500

@auth_bp.route('/oauth2callback')
def oauth2callback():
    """Handle the OAuth 2.0 callback from Google."""
    # Specify the state when creating the flow in the callback
    state = session.get('state', None)

    try:
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            google_fit.get_client_secrets_file(),
            scopes=google_fit.SCOPES,
            state=state)
        flow.redirect_uri = url_for('auth.oauth2callback', _external=True)

        # Use the authorization server's response to fetch the OAuth 2.0 tokens
        authorization_response = request.url
        flow.fetch_token(authorization_response=authorization_response)

        # Store credentials in the session
        credentials = flow.credentials
        session['credentials'] = google_fit.credentials_to_dict(credentials)

        return redirect(url_for('auth.user_dashboard'))
    except Exception as e:
        return jsonify(error=str(e)), 500

@auth_bp.route('/revoke-google-fit')
def revoke_google_fit():
    """Revoke Google Fit access."""
    if 'credentials' not in session:
        return redirect(url_for('auth.user_dashboard'))

    credentials = google.oauth2.credentials.Credentials(**session['credentials'])

    try:
        # Revoke token
        import requests
        requests.post('https://oauth2.googleapis.com/revoke',
                    params={'token': credentials.token},
                    headers={'content-type': 'application/x-www-form-urlencoded'})
    except Exception as e:
        print(f"Error revoking token: {e}")

    # Clear credentials from session
    session.pop('credentials', None)

    return redirect(url_for('auth.user_dashboard'))

@auth_bp.route('/sync-google-fit')
def sync_google_fit():
    """Sync data from Google Fit."""
    if 'credentials' not in session:
        return jsonify(success=False, error="Not authenticated with Google Fit"), 401

    try:
        fitness_data = google_fit.get_all_fitness_data()
        return jsonify(success=True, data=fitness_data)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500
