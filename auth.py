from flask import Blueprint, request, jsonify, render_template, redirect, url_for, session
from db import db, User
from flask_jwt_extended import create_access_token
import datetime
import os
import google_auth_oauthlib.flow
import google.oauth2.credentials
import googleapiclient.discovery
import google_fit

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role', 'User')

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "Email already exists"}), 409

    user = User(email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"msg": "User created successfully"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Invalid credentials"}), 401

    expires = datetime.timedelta(days=1)
    token = create_access_token(identity={'email': user.email, 'role': user.role}, expires_delta=expires)
    return jsonify(access_token=token), 200

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
