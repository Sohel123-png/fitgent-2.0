"""
Google Fit API integration for the fitness dashboard.
This module handles authentication and data retrieval from Google Fit.
"""

import os
import json
import datetime
from flask import current_app, url_for, redirect, request, session
import google.oauth2.credentials
import google_auth_oauthlib.flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# This variable specifies the name of a file that contains the OAuth 2.0
# information for this application, including its client_id and client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for read-only access to the authenticated
# user's Google Fit data
SCOPES = [
    'https://www.googleapis.com/auth/fitness.activity.read',
    'https://www.googleapis.com/auth/fitness.body.read',
    'https://www.googleapis.com/auth/fitness.heart_rate.read',
    'https://www.googleapis.com/auth/fitness.location.read',
    'https://www.googleapis.com/auth/fitness.nutrition.read',
    'https://www.googleapis.com/auth/fitness.sleep.read',
]

API_SERVICE_NAME = 'fitness'
API_VERSION = 'v1'

def get_client_secrets():
    """Returns the client secrets as a dict, either from file or environment variables."""
    file_path = os.path.join(os.path.dirname(__file__), CLIENT_SECRETS_FILE)

    # Try to load from file first
    if os.path.exists(file_path):
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading client secrets file: {e}")

    # If file doesn't exist or can't be loaded, use environment variables
    return {
        "web": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
            "project_id": os.getenv("GOOGLE_PROJECT_ID", ""),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
            "redirect_uris": [
                os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:5000/oauth2callback")
            ]
        }
    }

def credentials_to_dict(credentials):
    """Convert Credentials to a dictionary for storage in the session."""
    return {
        'token': credentials.token,
        'refresh_token': credentials.refresh_token,
        'token_uri': credentials.token_uri,
        'client_id': credentials.client_id,
        'client_secret': credentials.client_secret,
        'scopes': credentials.scopes
    }

def get_authorization_url():
    """Generate the authorization URL for Google Fit."""
    # Get client secrets
    client_secrets = get_client_secrets()

    # Check if we have valid client secrets
    if not client_secrets.get('web', {}).get('client_id') or not client_secrets.get('web', {}).get('client_secret'):
        print("Missing Google client ID or client secret")
        return None

    # Create a flow instance using client secrets
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        client_secrets, SCOPES)

    # Set the redirect URI
    flow.redirect_uri = url_for('auth.oauth2callback', _external=True)

    # Generate authorization URL
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent')

    # Store the state in the session
    session['state'] = state

    return authorization_url

def get_credentials_from_session():
    """Get credentials from the session."""
    if 'credentials' not in session:
        return None

    credentials_dict = session['credentials']
    return google.oauth2.credentials.Credentials(
        token=credentials_dict['token'],
        refresh_token=credentials_dict['refresh_token'],
        token_uri=credentials_dict['token_uri'],
        client_id=credentials_dict['client_id'],
        client_secret=credentials_dict['client_secret'],
        scopes=credentials_dict['scopes']
    )

def build_fitness_service():
    """Build and return a Fitness service object."""
    credentials = get_credentials_from_session()
    if not credentials:
        return None

    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

def get_steps_data(time_period_days=7):
    """Get step count data from Google Fit for the specified time period."""
    fitness_service = build_fitness_service()
    if not fitness_service:
        return None

    end_time = datetime.datetime.now(datetime.timezone.utc)
    start_time = end_time - datetime.timedelta(days=time_period_days)

    # Convert times to milliseconds since epoch
    end_time_ms = int(end_time.timestamp() * 1000)
    start_time_ms = int(start_time.timestamp() * 1000)

    try:
        data_sources = fitness_service.users().dataSources().list(
            userId='me'
        ).execute()

        # Find the step count data source
        step_data_source = None
        for data_source in data_sources.get('dataSource', []):
            if 'com.google.step_count.delta' in data_source.get('dataType', {}).get('name', ''):
                step_data_source = data_source['dataStreamId']
                break

        if not step_data_source:
            return None

        # Get step count data
        dataset = f"{start_time_ms}-{end_time_ms}"
        steps_data = fitness_service.users().dataSources().datasets().get(
            userId='me',
            dataSourceId=step_data_source,
            datasetId=dataset
        ).execute()

        # Process the data
        daily_steps = {}
        for point in steps_data.get('point', []):
            start_time_nanos = int(point['startTimeNanos'])
            end_time_nanos = int(point['endTimeNanos'])

            # Convert nanos to datetime
            start_date = datetime.datetime.fromtimestamp(start_time_nanos / 1e9)
            date_key = start_date.strftime('%Y-%m-%d')

            # Get step value
            step_value = point['value'][0]['intVal']

            # Add to daily steps
            if date_key in daily_steps:
                daily_steps[date_key] += step_value
            else:
                daily_steps[date_key] = step_value

        return daily_steps

    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def get_calories_data(time_period_days=7):
    """Get calories burned data from Google Fit for the specified time period."""
    fitness_service = build_fitness_service()
    if not fitness_service:
        return None

    end_time = datetime.datetime.now(datetime.timezone.utc)
    start_time = end_time - datetime.timedelta(days=time_period_days)

    # Convert times to milliseconds since epoch
    end_time_ms = int(end_time.timestamp() * 1000)
    start_time_ms = int(start_time.timestamp() * 1000)

    try:
        data_sources = fitness_service.users().dataSources().list(
            userId='me'
        ).execute()

        # Find the calories data source
        calories_data_source = None
        for data_source in data_sources.get('dataSource', []):
            if 'com.google.calories.expended' in data_source.get('dataType', {}).get('name', ''):
                calories_data_source = data_source['dataStreamId']
                break

        if not calories_data_source:
            return None

        # Get calories data
        dataset = f"{start_time_ms}-{end_time_ms}"
        calories_data = fitness_service.users().dataSources().datasets().get(
            userId='me',
            dataSourceId=calories_data_source,
            datasetId=dataset
        ).execute()

        # Process the data
        daily_calories = {}
        for point in calories_data.get('point', []):
            start_time_nanos = int(point['startTimeNanos'])
            end_time_nanos = int(point['endTimeNanos'])

            # Convert nanos to datetime
            start_date = datetime.datetime.fromtimestamp(start_time_nanos / 1e9)
            date_key = start_date.strftime('%Y-%m-%d')

            # Get calories value
            calories_value = point['value'][0]['fpVal']

            # Add to daily calories
            if date_key in daily_calories:
                daily_calories[date_key] += calories_value
            else:
                daily_calories[date_key] = calories_value

        return daily_calories

    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def get_heart_rate_data(time_period_days=7):
    """Get heart rate data from Google Fit for the specified time period."""
    fitness_service = build_fitness_service()
    if not fitness_service:
        return None

    end_time = datetime.datetime.now(datetime.timezone.utc)
    start_time = end_time - datetime.timedelta(days=time_period_days)

    # Convert times to milliseconds since epoch
    end_time_ms = int(end_time.timestamp() * 1000)
    start_time_ms = int(start_time.timestamp() * 1000)

    try:
        data_sources = fitness_service.users().dataSources().list(
            userId='me'
        ).execute()

        # Find the heart rate data source
        heart_rate_data_source = None
        for data_source in data_sources.get('dataSource', []):
            if 'com.google.heart_rate.bpm' in data_source.get('dataType', {}).get('name', ''):
                heart_rate_data_source = data_source['dataStreamId']
                break

        if not heart_rate_data_source:
            return None

        # Get heart rate data
        dataset = f"{start_time_ms}-{end_time_ms}"
        heart_rate_data = fitness_service.users().dataSources().datasets().get(
            userId='me',
            dataSourceId=heart_rate_data_source,
            datasetId=dataset
        ).execute()

        # Process the data
        heart_rates = []
        for point in heart_rate_data.get('point', []):
            start_time_nanos = int(point['startTimeNanos'])

            # Convert nanos to datetime
            timestamp = datetime.datetime.fromtimestamp(start_time_nanos / 1e9)

            # Get heart rate value
            heart_rate_value = point['value'][0]['fpVal']

            heart_rates.append({
                'timestamp': timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'value': heart_rate_value
            })

        # Calculate average resting heart rate (assuming lowest 10% of readings are resting)
        if heart_rates:
            sorted_rates = sorted(heart_rates, key=lambda x: x['value'])
            resting_sample_size = max(1, int(len(sorted_rates) * 0.1))
            resting_rates = sorted_rates[:resting_sample_size]
            avg_resting_rate = sum(item['value'] for item in resting_rates) / len(resting_rates)

            return {
                'heart_rates': heart_rates,
                'avg_resting_rate': round(avg_resting_rate, 1)
            }

        return None

    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def get_weight_data(time_period_days=30):
    """Get weight data from Google Fit for the specified time period."""
    fitness_service = build_fitness_service()
    if not fitness_service:
        return None

    end_time = datetime.datetime.now(datetime.timezone.utc)
    start_time = end_time - datetime.timedelta(days=time_period_days)

    # Convert times to milliseconds since epoch
    end_time_ms = int(end_time.timestamp() * 1000)
    start_time_ms = int(start_time.timestamp() * 1000)

    try:
        data_sources = fitness_service.users().dataSources().list(
            userId='me'
        ).execute()

        # Find the weight data source
        weight_data_source = None
        for data_source in data_sources.get('dataSource', []):
            if 'com.google.weight' in data_source.get('dataType', {}).get('name', ''):
                weight_data_source = data_source['dataStreamId']
                break

        if not weight_data_source:
            return None

        # Get weight data
        dataset = f"{start_time_ms}-{end_time_ms}"
        weight_data = fitness_service.users().dataSources().datasets().get(
            userId='me',
            dataSourceId=weight_data_source,
            datasetId=dataset
        ).execute()

        # Process the data
        weights = []
        for point in weight_data.get('point', []):
            start_time_nanos = int(point['startTimeNanos'])

            # Convert nanos to datetime
            timestamp = datetime.datetime.fromtimestamp(start_time_nanos / 1e9)

            # Get weight value in kg
            weight_value = point['value'][0]['fpVal']

            weights.append({
                'timestamp': timestamp.strftime('%Y-%m-%d'),
                'value': weight_value
            })

        # Sort by timestamp and get the latest weight
        if weights:
            sorted_weights = sorted(weights, key=lambda x: x['timestamp'], reverse=True)
            latest_weight = sorted_weights[0]['value']

            # Calculate weight change if we have at least two measurements
            weight_change = None
            if len(sorted_weights) > 1:
                earliest_weight = sorted_weights[-1]['value']
                weight_change = latest_weight - earliest_weight

            return {
                'weights': weights,
                'latest_weight': round(latest_weight, 1),
                'weight_change': round(weight_change, 1) if weight_change is not None else None
            }

        return None

    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def get_sleep_data(time_period_days=7):
    """Get sleep data from Google Fit for the specified time period."""
    fitness_service = build_fitness_service()
    if not fitness_service:
        return None

    end_time = datetime.datetime.now(datetime.timezone.utc)
    start_time = end_time - datetime.timedelta(days=time_period_days)

    # Convert times to milliseconds since epoch
    end_time_ms = int(end_time.timestamp() * 1000)
    start_time_ms = int(start_time.timestamp() * 1000)

    try:
        data_sources = fitness_service.users().dataSources().list(
            userId='me'
        ).execute()

        # Find the sleep data source
        sleep_data_source = None
        for data_source in data_sources.get('dataSource', []):
            if 'com.google.sleep.segment' in data_source.get('dataType', {}).get('name', ''):
                sleep_data_source = data_source['dataStreamId']
                break

        if not sleep_data_source:
            return None

        # Get sleep data
        dataset = f"{start_time_ms}-{end_time_ms}"
        sleep_data = fitness_service.users().dataSources().datasets().get(
            userId='me',
            dataSourceId=sleep_data_source,
            datasetId=dataset
        ).execute()

        # Process the data
        sleep_segments = []
        for point in sleep_data.get('point', []):
            start_time_nanos = int(point['startTimeNanos'])
            end_time_nanos = int(point['endTimeNanos'])

            # Convert nanos to datetime
            start_time = datetime.datetime.fromtimestamp(start_time_nanos / 1e9)
            end_time = datetime.datetime.fromtimestamp(end_time_nanos / 1e9)

            # Calculate duration in hours
            duration_hours = (end_time - start_time).total_seconds() / 3600

            # Get sleep stage value
            sleep_stage = point['value'][0]['intVal']

            # Map sleep stage value to name
            sleep_stage_name = {
                1: 'Awake',
                2: 'Sleep',
                3: 'Out-of-bed',
                4: 'Light sleep',
                5: 'Deep sleep',
                6: 'REM sleep'
            }.get(sleep_stage, 'Unknown')

            sleep_segments.append({
                'date': start_time.strftime('%Y-%m-%d'),
                'start_time': start_time.strftime('%H:%M:%S'),
                'end_time': end_time.strftime('%H:%M:%S'),
                'duration_hours': round(duration_hours, 2),
                'sleep_stage': sleep_stage_name
            })

        # Group by date and calculate total sleep time
        daily_sleep = {}
        for segment in sleep_segments:
            date = segment['date']
            if segment['sleep_stage'] in ['Sleep', 'Light sleep', 'Deep sleep', 'REM sleep']:
                if date in daily_sleep:
                    daily_sleep[date] += segment['duration_hours']
                else:
                    daily_sleep[date] = segment['duration_hours']

        # Get last night's sleep
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        last_night_sleep = daily_sleep.get(yesterday, 0)

        return {
            'sleep_segments': sleep_segments,
            'daily_sleep': daily_sleep,
            'last_night_sleep': round(last_night_sleep, 1)
        }

    except HttpError as error:
        print(f'An error occurred: {error}')
        return None

def get_all_fitness_data():
    """Get all fitness data from Google Fit."""
    steps_data = get_steps_data()
    calories_data = get_calories_data()
    heart_rate_data = get_heart_rate_data()
    weight_data = get_weight_data()
    sleep_data = get_sleep_data()

    # Get today's data
    today = datetime.datetime.now().strftime('%Y-%m-%d')

    # Calculate today's steps
    today_steps = steps_data.get(today, 0) if steps_data else 0

    # Calculate today's calories
    today_calories = int(calories_data.get(today, 0)) if calories_data else 0

    # Get yesterday's data for comparison
    yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    yesterday_steps = steps_data.get(yesterday, 0) if steps_data else 0

    # Calculate step change percentage
    step_change_pct = 0
    if yesterday_steps > 0 and today_steps > 0:
        step_change_pct = ((today_steps - yesterday_steps) / yesterday_steps) * 100

    # Get latest weight and heart rate
    latest_weight = weight_data.get('latest_weight', 0) if weight_data else 0
    weight_change = weight_data.get('weight_change', 0) if weight_data else 0
    avg_resting_heart_rate = heart_rate_data.get('avg_resting_rate', 0) if heart_rate_data else 0

    # Get sleep data
    last_night_sleep = sleep_data.get('last_night_sleep', 0) if sleep_data else 0

    return {
        'today_steps': today_steps,
        'today_calories': today_calories,
        'step_change_pct': round(step_change_pct, 1),
        'latest_weight': latest_weight,
        'weight_change': weight_change,
        'avg_resting_heart_rate': avg_resting_heart_rate,
        'last_night_sleep': last_night_sleep,
        'has_data': bool(steps_data or calories_data or heart_rate_data or weight_data or sleep_data)
    }
