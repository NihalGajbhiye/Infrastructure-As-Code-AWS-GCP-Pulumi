from flask import Response, jsonify
import re
import csv
from datetime import datetime
from app.models import User
from app.extension import db

def create_response(status_code, data=None):
    response = jsonify(data) if data else Response()
    response.status_code = status_code
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    return response

def load_users_from_csv():
    with open('login.csv', 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            if is_valid_email(row['email']) and is_valid_password(row['password']) and len(row['first_name']) > 0 and len(row['last_name']) > 0:
                user = User.query.filter_by(email=row['email']).first()
                if not user:
                    new_user = User(
                        first_name = row['first_name'],
                        last_name = row['last_name'],
                        email = row['email']
                    )
                    new_user.password = row['password']
                    db.session.add(new_user)
        db.session.commit()

def is_valid_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(pattern, email) is not None

def is_valid_password(password):
    if len(password) < 6:
        return False
    
    if not any(char.isdigit() for char in password):
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char.islower() for char in password):
        return False
    if not any(char in '!@#$%^&*()' for char in password):
        return False
    return True

def validate_datetime_format(dt_str):
    try:
        dt_obj = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S.%fZ")
        return True, dt_obj
    except ValueError:
        return False, None





